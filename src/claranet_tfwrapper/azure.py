"""Azure related functions for tfwrapper."""

import logging
import os
import subprocess

import yaml

SP_CREDENTIALS_FILE = os.path.expanduser("~/.azurerm/config.yml")

logger = logging.getLogger()


class AzureError(Exception):
    """Azure specific error class."""

    @property
    def message(self):
        """Error message."""
        return self.args[0]


def get_sp_profile(profile_name):
    """Retrieve Service Principal credentials from name."""
    with open(SP_CREDENTIALS_FILE, "r") as f:
        load_azure_config = yaml.safe_load(f)
        if load_azure_config is None:
            raise AzureError(f"Please configure your {SP_CREDENTIALS_FILE} configuration file")
        if profile_name not in load_azure_config.keys():
            raise AzureError(f'Cannot find "{profile_name}" profile in your {SP_CREDENTIALS_FILE} configuration file')
        return (
            load_azure_config[profile_name]["tenant_id"],
            load_azure_config[profile_name]["client_id"],
            load_azure_config[profile_name]["client_secret"],
        )


def set_context(wrapper_config, subscription_id, tenant_id=None, sp_profile=None, backend_context=False):
    """
    Configure context and check credentials.

    This function configures environment variables needed for the Azure context.
    It also checks the credentials from Azure CLI context or given Service Principal profile.
    It returns a dict of Terraform variables to ease Azure configuration

    Parameters
    ----------
    wrapper_config : dict
        The wrapper global configuration
    subscription_id : str
        Azure subscription id
    tenant_id : str
        Azure Tenant/Directory id
    sp_profile : str
        Azure Service Principal profile name to use to configure credentials
    backend_context : bool
        True is context has to be set/check for a backend configuration

    Returns
    -------
    dict
        Terraform variables
    """
    if backend_context:
        session = os.environ.get("ARM_ACCESS_KEY", None) or os.environ.get("ARM_SAS_TOKEN", None)
        if session:
            logger.info("'ARM_SAS_TOKEN' or 'ARM_ACCESS_KEY' already set, don't try to get a new session.")
            logger.debug("Session token found for backend: {}".format(session))
            os.environ["TF_VAR_azure_state_access_key"] = session

    az_config_dir = None
    azure_local_session = wrapper_config.get("config", {}).get("use_local_azure_session_directory", True)
    if azure_local_session and "AZURE_CONFIG_DIR" not in os.environ:
        az_config_dir = os.path.join(wrapper_config["rootdir"], ".run", "azure")
        logger.debug(f"Exporting `AZURE_CONFIG_DIR` to `{az_config_dir}` directory")
        os.environ["AZURE_CONFIG_DIR"] = az_config_dir

    if sp_profile is None:
        try:
            _launch_cli_command(["az", "account", "get-access-token", "-s", subscription_id], az_config_dir)
        except subprocess.CalledProcessError:
            msg = (
                "Error accessing subscription, check that you have Azure CLI installed and are authorized "
                "on this subscription then log yourself in with:\n\n"
            )

            if az_config_dir:
                msg += f"AZURE_CONFIG_DIR={az_config_dir} "
            if tenant_id:
                msg += f"az login --tenant {tenant_id}"
            else:
                msg += "az login"
            raise AzureError(msg)
    else:
        sp_tenant_id, client_id, client_secret = get_sp_profile(sp_profile)

        if tenant_id is not None and tenant_id != sp_tenant_id:
            raise AzureError(f'Configured tenant id and Service Principal tenant id must be the same for service "{sp_profile}".')

        # Logging in, useful for az CLI calls from Terraform code
        logger.info(f"Logging in with Service Principal {sp_profile}")
        try:
            _launch_cli_command(
                [
                    "az",
                    "login",
                    "--service-principal",
                    "--username",
                    client_id,
                    "--password",
                    client_secret,
                    "--tenant",
                    sp_tenant_id,
                ],
                os.path.join(wrapper_config["rootdir"], ".run", "azure_backend") if backend_context else az_config_dir,
            )
        except subprocess.CalledProcessError as e:
            raise AzureError(f"Cannot log in with service principal {sp_profile}: {e.output}")

        if not backend_context:
            os.environ["ARM_CLIENT_ID"] = client_id
            os.environ["ARM_CLIENT_SECRET"] = client_secret
            os.environ["ARM_TENANT_ID"] = sp_tenant_id
        else:
            os.environ["TF_VAR_azure_state_client_id"] = client_id
            os.environ["TF_VAR_azure_state_client_secret"] = client_secret
            os.environ["TF_VAR_azure_state_client_tenant_id"] = sp_tenant_id


def _launch_cli_command(command, az_config_dir=None):
    """Launch an Azure CLI command with en given AZURE_CONFIG_DIR context."""
    env = os.environ.copy()
    if az_config_dir:
        env["AZURE_CONFIG_DIR"] = az_config_dir
    subprocess.run(command, check=True, capture_output=True, env=env)
