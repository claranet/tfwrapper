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
    logger.debug(f"Reading {SP_CREDENTIALS_FILE} to fetch {profile_name} credentials.")

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


def set_context(wrapper_config, subscription_id, tenant_id, context_name, sp_profile=None, backend_context=False):
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
    context_name: str
        Name of the context to set up. Must be empty for default context
    sp_profile : str
        Azure Service Principal profile name to use to configure credentials
    backend_context : bool
        True if context has to be set/check for a backend configuration

    Returns
    -------
    dict
        Terraform variables
    """
    logger.debug(f"Configuring azurerm {'backend' if backend_context else 'stack'} context.")

    tf_vars = {}
    backend_session = None
    if backend_context:
        backend_session = os.environ.get("ARM_ACCESS_KEY", None) or os.environ.get("ARM_SAS_TOKEN", None)
        if backend_session:
            logger.info("'ARM_SAS_TOKEN' or 'ARM_ACCESS_KEY' already set, don't try to get a new session.")
            logger.debug("Session token found for backend: {}".format(backend_session))
            tf_vars["azure_state_access_key"] = backend_session

    az_config_dir = None
    azure_local_session = wrapper_config.get("config", {}).get("use_local_azure_session_directory", True)
    if azure_local_session:
        logger.debug("Using Azure isolated session")
    else:
        logger.debug("Using Azure global context, no session isolation")
    if not azure_local_session and context_name:
        raise AzureError(
            "Cannot configure multiple providers context without session isolation.\n"
            "Set `use_local_azure_session_directory: true` in your configuration."
        )

    if azure_local_session:
        suffix = f"_{context_name}" if context_name else ""
        env_var_name = f"AZURE_CONFIG_DIR{suffix.upper()}"
        az_config_dir = os.path.join(wrapper_config["rootdir"], ".run", f"azure{suffix}")
        if env_var_name not in os.environ:
            logger.debug(f"Exporting `{env_var_name}` to `{az_config_dir}` directory")
            os.environ[env_var_name] = az_config_dir

    vars_prefix = f"{context_name}_" if context_name else ""

    tf_vars.update(
        {
            f"{vars_prefix}azure_subscription_id": subscription_id,
            f"{vars_prefix}azure_tenant_id": tenant_id,
        }
    )

    if sp_profile is None and not backend_session:
        logger.debug(f"Trying to fetch Azure access token to ensure " f"{'backend' if backend_context else 'stack'} access.")
        try:
            _launch_cli_command(["az", "account", "get-access-token", "-s", subscription_id], az_config_dir)
        except subprocess.CalledProcessError:
            msg = (
                f"Error accessing subscription {subscription_id}, check that you have Azure CLI installed and "
                f"are authorized on this subscription then log yourself in with:\n\n"
            )

            if az_config_dir:
                msg += f"{env_var_name}={az_config_dir} "
            if tenant_id:
                msg += f"az login --tenant {tenant_id}"
            else:
                msg += "az login"
            raise AzureError(msg)
    elif sp_profile:
        sp_tenant_id, client_id, client_secret = get_sp_profile(sp_profile)
        logger.debug(f'Service principal "{sp_profile}" loaded with client id "{client_id}" and tenant id "{sp_tenant_id}"')

        if tenant_id is not None and tenant_id != sp_tenant_id:
            raise AzureError(f'Configured tenant id and Service Principal tenant id must be the same for service "{sp_profile}".')

        # Logging in, useful for az CLI calls from Terraform code
        log_context = ""
        if context_name:
            log_context = f' for "{context_name}" stack context'
        logger.info(f'Logging in with Service Principal "{sp_profile}"{log_context}')
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

        if not backend_context and not context_name:
            os.environ["ARM_CLIENT_ID"] = client_id
            os.environ["ARM_CLIENT_SECRET"] = client_secret
            os.environ["ARM_TENANT_ID"] = sp_tenant_id

        tf_vars.update({f"{vars_prefix}azure_client_id": client_id, f"{vars_prefix}azure_client_secret": client_secret})

    return tf_vars


def _launch_cli_command(command, az_config_dir=None):
    """Launch an Azure CLI command with a given AZURE_CONFIG_DIR context."""
    if az_config_dir:
        logger.debug(f'Launching command "{" ".join(command)}" with AZURE_CONFIG_DIR="{az_config_dir}" context')
    else:
        logger.debug(f'Launching command "{" ".join(command)}"')
    env = os.environ.copy()
    if az_config_dir:
        env["AZURE_CONFIG_DIR"] = az_config_dir
    subprocess.run(command, check=True, env=env, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
