"""Azure related functns for tfwrapper."""

import logging
import os
import subprocess

import yaml

SP_CREDENTIALS_FILE = os.path.expanduser("~/.azurerm/config.yml")

logger = logging.getLogger()


class AzureError(Exception):
    """Azure specific error class."""

    pass


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


def set_context(wrapper_config, subscription_id, tenant_id=None, sp_profile=None):
    """Preconfigure context and check credentials."""
    azure_local_session = wrapper_config.get("config", {}).get("use_local_azure_session_directory", True)
    if azure_local_session:
        az_config_dir = os.path.join(wrapper_config["rootdir"], ".run", "azure")
        logger.debug(f"Exporting `AZURE_CONFIG_DIR` to `{az_config_dir}` directory")
        os.environ["AZURE_CONFIG_DIR"] = az_config_dir

    # Backwards compatibility
    os.environ["TF_VAR_azure_state_access_key"] = os.environ.get("ARM_ACCESS_KEY", "")

    if sp_profile is None:
        try:
            subprocess.run(["az", "account", "get-access-token", "-s", subscription_id], check=True, capture_output=True)
        except subprocess.CalledProcessError:
            msg = (
                "Error accessing subscription, check that you have Azure CLI installed and are authorized "
                "on this subscription then log yourself in with:\n\n"
            )

            if azure_local_session:
                msg += f"AZURE_CONFIG_DIR={az_config_dir} "
            if tenant_id:
                msg += f"az login --tenant {tenant_id}"
            else:
                msg += "az login"
            raise AzureError(msg)
    else:
        sp_tenant_id, client_id, client_secret = get_sp_profile(sp_profile)

        if tenant_id is not None and tenant_id != sp_tenant_id:
            raise AzureError("Configured tenant id and Service Principal tenant id must be the same.")

        # Logging in, useful for az CLI calls from Terraform code
        logger.info(f"Logging in with Service Principal {sp_profile}")
        try:
            subprocess.run(
                [
                    "az",
                    "login",
                    "--service-principal",
                    "--username",
                    client_id,
                    "--password",
                    client_secret,
                    "--tenant",
                    tenant_id,
                ],
                check=True,
                capture_output=True,
                universal_newlines=True,
            )
        except subprocess.CalledProcessError as e:
            raise AzureError(f"Cannot log in with service principal {sp_profile}: {e.output}")

        os.environ["ARM_CLIENT_ID"] = client_id
        os.environ["ARM_CLIENT_SECRET"] = client_secret
        os.environ["ARM_TENANT_ID"] = sp_tenant_id
