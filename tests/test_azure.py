"""Test azure related functions."""

import os
import subprocess
from unittest.mock import MagicMock

import pytest

import claranet_tfwrapper.azure as azure


def test_user_context(monkeypatch, tmp_path):
    wrapper_config = {"rootdir": tmp_path, "config": {"use_local_azure_session_directory": True}}
    subscription_id = "00000000-0000-0000-0000-000000000000"
    tenant_id = "11111111-1111-1111-1111-111111111111"

    launch_cli = MagicMock()
    monkeypatch.setattr(azure, "_launch_cli_command", launch_cli)

    tf_vars = azure.set_context(wrapper_config, subscription_id, tenant_id, "")

    launch_cli.assert_called_once_with(
        ["az", "account", "get-access-token", "-s", subscription_id], os.path.join(tmp_path, ".run", "azure")
    )
    assert os.environ.get("AZURE_CONFIG_DIR", None) == os.path.join(tmp_path, ".run", "azure")
    assert tf_vars["azure_subscription_id"] == subscription_id
    assert tf_vars["azure_tenant_id"] == tenant_id


def test_user_context_no_isolation(monkeypatch, tmp_path):
    wrapper_config = {"rootdir": tmp_path, "config": {"use_local_azure_session_directory": False}}
    subscription_id = "00000000-0000-0000-0000-000000000000"
    tenant_id = "11111111-1111-1111-1111-111111111111"

    launch_cli = MagicMock()
    monkeypatch.setattr(azure, "_launch_cli_command", launch_cli)

    tf_vars = azure.set_context(wrapper_config, subscription_id, tenant_id, "")

    launch_cli.assert_called_once_with(["az", "account", "get-access-token", "-s", subscription_id], None)
    assert os.environ.get("AZURE_CONFIG_DIR", "should be unset") == "should be unset"
    assert tf_vars["azure_subscription_id"] == subscription_id
    assert tf_vars["azure_tenant_id"] == tenant_id


def test_sp_context(monkeypatch, tmp_path):
    wrapper_config = {"rootdir": tmp_path, "config": {"use_local_azure_session_directory": True}}
    subscription_id = "00000000-0000-0000-0000-000000000000"
    tenant_id = "11111111-1111-1111-1111-111111111111"
    client_id = "22222222-2222-2222-2222-222222222222"
    client_secret = "mysecret"

    launch_cli = MagicMock()
    monkeypatch.setattr(azure, "_launch_cli_command", launch_cli)

    sp_profile_mock = MagicMock()
    monkeypatch.setattr(azure, "get_sp_profile", sp_profile_mock)
    sp_profile_mock.return_value = (tenant_id, client_id, client_secret)

    tf_vars = azure.set_context(wrapper_config, subscription_id, tenant_id, "", sp_profile="my-profile")

    launch_cli.assert_called_once_with(
        ["az", "login", "--service-principal", "--username", client_id, "--password=@-", "--tenant", tenant_id],
        os.path.join(tmp_path, ".run", "azure"),
        stdin=client_secret,
    )
    sp_profile_mock.assert_called_once_with("my-profile")
    assert os.environ.get("AZURE_CONFIG_DIR", None) == os.path.join(tmp_path, ".run", "azure")
    assert os.environ.get("ARM_CLIENT_ID", None) == client_id
    assert os.environ.get("ARM_CLIENT_SECRET", None) == client_secret
    assert os.environ.get("ARM_TENANT_ID", None) == tenant_id
    assert tf_vars["azure_subscription_id"] == subscription_id
    assert tf_vars["azure_tenant_id"] == tenant_id
    assert tf_vars["azure_client_id"] == client_id
    assert tf_vars["azure_client_secret"] == client_secret


def test_user_multiple_context(monkeypatch, tmp_path):
    wrapper_config = {"rootdir": tmp_path, "config": {"use_local_azure_session_directory": True}}
    subscription_id = "00000000-0000-0000-0000-000000000000"
    tenant_id = "11111111-1111-1111-1111-111111111111"

    alt_subscription_id = "22222222-2222-2222-2222-222222222222"
    alt_tenant_id = "33333333-3333-3333-3333-333333333333"

    launch_cli = MagicMock()
    monkeypatch.setattr(azure, "_launch_cli_command", launch_cli)

    tf_vars = azure.set_context(wrapper_config, subscription_id, tenant_id, "")
    launch_cli.assert_called_with(
        ["az", "account", "get-access-token", "-s", subscription_id], os.path.join(tmp_path, ".run", "azure")
    )

    tf_vars_alt = azure.set_context(wrapper_config, alt_subscription_id, alt_tenant_id, "alternative")
    launch_cli.assert_called_with(
        ["az", "account", "get-access-token", "-s", alt_subscription_id], os.path.join(tmp_path, ".run", "azure_alternative")
    )

    tf_vars.update(tf_vars_alt)

    assert os.environ.get("AZURE_CONFIG_DIR", None) == os.path.join(tmp_path, ".run", "azure")
    assert tf_vars["azure_subscription_id"] == subscription_id
    assert tf_vars["azure_tenant_id"] == tenant_id

    assert os.environ.get("AZURE_CONFIG_DIR_ALTERNATIVE", None) == os.path.join(tmp_path, ".run", "azure_alternative")
    assert tf_vars["alternative_azure_subscription_id"] == alt_subscription_id
    assert tf_vars["alternative_azure_tenant_id"] == alt_tenant_id


def test_sp_multiple_context_no_isolation(monkeypatch, tmp_path):
    wrapper_config = {"rootdir": tmp_path, "config": {"use_local_azure_session_directory": False}}
    subscription_id = "00000000-0000-0000-0000-000000000000"
    tenant_id = "11111111-1111-1111-1111-111111111111"

    alt_subscription_id = "22222222-2222-2222-2222-222222222222"
    alt_tenant_id = "33333333-3333-3333-3333-333333333333"

    launch_cli = MagicMock()
    monkeypatch.setattr(azure, "_launch_cli_command", launch_cli)

    azure.set_context(wrapper_config, subscription_id, tenant_id, "")
    with pytest.raises(azure.AzureError):
        azure.set_context(wrapper_config, alt_subscription_id, alt_tenant_id, "alternative")


def test_sp_multiple_context(monkeypatch, tmp_path):
    wrapper_config = {"rootdir": tmp_path, "config": {"use_local_azure_session_directory": True}}
    subscription_id = "00000000-0000-0000-0000-000000000000"
    tenant_id = "11111111-1111-1111-1111-111111111111"
    client_id = "44444444-4444-4444-4444-444444444444"
    client_secret = "mysecret"

    alt_subscription_id = "22222222-2222-2222-2222-222222222222"
    alt_tenant_id = "33333333-3333-3333-3333-333333333333"
    alt_client_id = "55555555-5555-5555-5555-555555555555"
    alt_client_secret = "myalternativesecret"

    launch_cli = MagicMock()
    monkeypatch.setattr(azure, "_launch_cli_command", launch_cli)

    sp_profile_mock = MagicMock()
    monkeypatch.setattr(azure, "get_sp_profile", sp_profile_mock)
    sp_profile_mock.side_effect = lambda p: (
        (tenant_id, client_id, client_secret) if p == "my-profile" else (alt_tenant_id, alt_client_id, alt_client_secret)
    )

    tf_vars = azure.set_context(wrapper_config, subscription_id, tenant_id, "", sp_profile="my-profile")
    sp_profile_mock.assert_called_with("my-profile")
    launch_cli.assert_called_with(
        ["az", "login", "--service-principal", "--username", client_id, "--password=@-", "--tenant", tenant_id],
        os.path.join(tmp_path, ".run", "azure"),
        stdin=client_secret,
    )

    tf_vars_alt = azure.set_context(
        wrapper_config, alt_subscription_id, alt_tenant_id, "alternative", sp_profile="my-alternative-profile"
    )
    tf_vars.update(tf_vars_alt)
    sp_profile_mock.assert_called_with("my-alternative-profile")
    launch_cli.assert_called_with(
        [
            "az",
            "login",
            "--service-principal",
            "--username",
            alt_client_id,
            "--password=@-",
            "--tenant",
            alt_tenant_id,
        ],
        os.path.join(tmp_path, ".run", "azure_alternative"),
        stdin=alt_client_secret,
    )

    assert os.environ.get("AZURE_CONFIG_DIR", None) == os.path.join(tmp_path, ".run", "azure")
    assert os.environ.get("ARM_CLIENT_ID", None) == client_id
    assert os.environ.get("ARM_CLIENT_SECRET", None) == client_secret
    assert os.environ.get("ARM_TENANT_ID", None) == tenant_id
    assert tf_vars["azure_subscription_id"] == subscription_id
    assert tf_vars["azure_tenant_id"] == tenant_id
    assert tf_vars["azure_client_id"] == client_id
    assert tf_vars["azure_client_secret"] == client_secret

    assert os.environ.get("AZURE_CONFIG_DIR_ALTERNATIVE", None) == os.path.join(tmp_path, ".run", "azure_alternative")
    assert tf_vars["alternative_azure_subscription_id"] == alt_subscription_id
    assert tf_vars["alternative_azure_tenant_id"] == alt_tenant_id
    assert tf_vars["alternative_azure_client_id"] == alt_client_id
    assert tf_vars["alternative_azure_client_secret"] == alt_client_secret


def test_user_context_backend(monkeypatch, tmp_path):
    wrapper_config = {"rootdir": tmp_path, "config": {"use_local_azure_session_directory": True}}
    subscription_id = "00000000-0000-0000-0000-000000000000"
    tenant_id = "11111111-1111-1111-1111-111111111111"

    launch_cli = MagicMock()
    monkeypatch.setattr(azure, "_launch_cli_command", launch_cli)

    azure.set_context(wrapper_config, subscription_id, tenant_id, "", backend_context=True)

    launch_cli.assert_called_once_with(
        ["az", "account", "get-access-token", "-s", subscription_id], os.path.join(tmp_path, ".run", "azure")
    )
    assert os.environ.get("AZURE_CONFIG_DIR", None) == os.path.join(tmp_path, ".run", "azure")


def test_user_context_backend_no_isolation(monkeypatch, tmp_path):
    wrapper_config = {"rootdir": tmp_path, "config": {"use_local_azure_session_directory": False}}
    subscription_id = "00000000-0000-0000-0000-000000000000"
    tenant_id = "11111111-1111-1111-1111-111111111111"

    launch_cli = MagicMock()
    monkeypatch.setattr(azure, "_launch_cli_command", launch_cli)

    azure.set_context(wrapper_config, subscription_id, tenant_id, "", backend_context=True)

    launch_cli.assert_called_once_with(["az", "account", "get-access-token", "-s", subscription_id], None)
    assert os.environ.get("AZURE_CONFIG_DIR", "") == ""


def test_sas_context_backend_user_stack(monkeypatch, tmp_path):
    wrapper_config = {"rootdir": tmp_path, "config": {"use_local_azure_session_directory": True}}
    subscription_id = "00000000-0000-0000-0000-000000000000"
    tenant_id = "11111111-1111-1111-1111-111111111111"

    os.environ["ARM_SAS_TOKEN"] = "azurerm-sas-token"

    launch_cli = MagicMock()
    monkeypatch.setattr(azure, "_launch_cli_command", launch_cli)

    tf_vars = azure.set_context(wrapper_config, subscription_id, tenant_id, "", backend_context=True)

    launch_cli.assert_not_called()
    assert tf_vars.get("azure_state_access_key") == "azurerm-sas-token"


def test_sp_context_login_error_shows_cli_stderr(monkeypatch, tmp_path):
    wrapper_config = {"rootdir": tmp_path, "config": {"use_local_azure_session_directory": True}}
    subscription_id = "00000000-0000-0000-0000-000000000000"
    tenant_id = "11111111-1111-1111-1111-111111111111"
    az_error = "AADSTS7000222: The provided client secret keys for app '22222222' are expired."

    launch_cli = MagicMock(
        side_effect=subprocess.CalledProcessError(1, ["az", "login"], output=b"", stderr=f"ERROR: {az_error}\n".encode())
    )
    monkeypatch.setattr(azure, "_launch_cli_command", launch_cli)
    monkeypatch.setattr(azure, "get_sp_profile", MagicMock(return_value=(tenant_id, "client", "secret")))

    with pytest.raises(azure.AzureError) as excinfo:
        azure.set_context(wrapper_config, subscription_id, tenant_id, "", sp_profile="my-profile")

    assert excinfo.value.message == f"Cannot log in with service principal my-profile: ERROR: {az_error}"


def test_sp_context_login_error_drops_cli_login_advice(monkeypatch, tmp_path):
    wrapper_config = {"rootdir": tmp_path, "config": {"use_local_azure_session_directory": True}}
    subscription_id = "00000000-0000-0000-0000-000000000000"
    tenant_id = "11111111-1111-1111-1111-111111111111"
    az_error = "ERROR: AADSTS7000222: The provided client secret keys for app '22222222' are expired."
    stderr = (
        f"{az_error}\n"
        "Run the command below to authenticate interactively; additional arguments may be added as needed:\n"
        "az logout\n"
        f'az login --tenant "{tenant_id}"\n'
    )

    launch_cli = MagicMock(side_effect=subprocess.CalledProcessError(1, ["az", "login"], output=b"", stderr=stderr.encode()))
    monkeypatch.setattr(azure, "_launch_cli_command", launch_cli)
    monkeypatch.setattr(azure, "get_sp_profile", MagicMock(return_value=(tenant_id, "client", "secret")))

    with pytest.raises(azure.AzureError) as excinfo:
        azure.set_context(wrapper_config, subscription_id, tenant_id, "", sp_profile="my-profile")

    assert excinfo.value.message == f"Cannot log in with service principal my-profile: {az_error}"
    assert excinfo.value.__suppress_context__


def test_user_context_access_token_error_shows_cli_stderr(monkeypatch, tmp_path):
    rootdir = tmp_path / "root dir"
    wrapper_config = {"rootdir": rootdir, "config": {"use_local_azure_session_directory": True}}
    subscription_id = "00000000-0000-0000-0000-000000000000"
    tenant_id = "11111111-1111-1111-1111-111111111111"
    az_error = "ERROR: Please run 'az login' to setup account."

    launch_cli = MagicMock(side_effect=subprocess.CalledProcessError(1, ["az"], output=b"", stderr=f"{az_error}\n".encode()))
    monkeypatch.setattr(azure, "_launch_cli_command", launch_cli)

    with pytest.raises(azure.AzureError) as excinfo:
        azure.set_context(wrapper_config, subscription_id, tenant_id, "")

    assert excinfo.value.message.startswith(f"Error accessing subscription {subscription_id}: {az_error}\n")
    assert excinfo.value.message.endswith(f"AZURE_CONFIG_DIR='{rootdir / '.run' / 'azure'}' az login --tenant {tenant_id}")


def test_user_named_context_access_token_error_hint_uses_azure_config_dir(monkeypatch, tmp_path):
    wrapper_config = {"rootdir": tmp_path, "config": {"use_local_azure_session_directory": True}}
    tenant_id = "11111111-1111-1111-1111-111111111111"

    launch_cli = MagicMock(side_effect=subprocess.CalledProcessError(1, ["az"], output=b"", stderr=b""))
    monkeypatch.setattr(azure, "_launch_cli_command", launch_cli)

    with pytest.raises(azure.AzureError) as excinfo:
        azure.set_context(wrapper_config, "00000000-0000-0000-0000-000000000000", tenant_id, "my-alt")

    assert "Azure CLI exited with status 1" in excinfo.value.message
    assert excinfo.value.message.endswith(f"AZURE_CONFIG_DIR={tmp_path / '.run' / 'azure_my-alt'} az login --tenant {tenant_id}")


@pytest.mark.parametrize(
    "stderr, expected",
    [
        (b"ERROR: boom\nRun the command below to authenticate interactively\naz logout\n", "ERROR: boom"),
        (b"Traceback (most recent call last):\n  ...\nValueError: oops\n", "ValueError: oops"),
        (b"", "Azure CLI exited with status 137"),
        (None, "Azure CLI exited with status 137"),
    ],
)
def test_cli_error_output(stderr, expected):
    error = subprocess.CalledProcessError(137, ["az"], output=b'{"accessToken": "eyJsecret"}', stderr=stderr)

    assert azure._cli_error_output(error) == expected


def test_launch_cli_command_error_output_from_real_process(monkeypatch, tmp_path):
    az = tmp_path / "az"
    az.write_text("#!/bin/sh\necho 'ERROR: boom' >&2\nexit 1\n")
    az.chmod(0o755)
    monkeypatch.setenv("PATH", f"{tmp_path}{os.pathsep}{os.environ['PATH']}")

    with pytest.raises(subprocess.CalledProcessError) as excinfo:
        azure._launch_cli_command(["az", "account", "show"])

    assert azure._cli_error_output(excinfo.value) == "ERROR: boom"


def test_launch_cli_command_passes_stdin_to_real_process(monkeypatch, tmp_path):
    az = tmp_path / "az"
    az.write_text('#!/bin/sh\nread secret\necho "ERROR: got $secret" >&2\nexit 1\n')
    az.chmod(0o755)
    monkeypatch.setenv("PATH", f"{tmp_path}{os.pathsep}{os.environ['PATH']}")

    with pytest.raises(subprocess.CalledProcessError) as excinfo:
        azure._launch_cli_command(["az", "login", "--password=@-"], stdin="mysecret\n")

    assert azure._cli_error_output(excinfo.value) == "ERROR: got mysecret"
    assert "mysecret" not in str(excinfo.value)


def test_launch_cli_command_missing_cli(monkeypatch, tmp_path):
    monkeypatch.setenv("PATH", str(tmp_path))

    with pytest.raises(azure.AzureError) as excinfo:
        azure._launch_cli_command(["az", "account", "show"])

    assert "check that it is installed" in excinfo.value.message


@pytest.mark.parametrize("az_config_dir", ["/tmp/az", None])
def test_launch_cli_command_runs_subprocess(monkeypatch, caplog, az_config_dir):
    run = MagicMock()
    monkeypatch.setattr(azure.subprocess, "run", run)
    command = ["az", "login", "--service-principal", "--password=@-"]

    with caplog.at_level("DEBUG", logger=azure.logger.name):
        azure._launch_cli_command(command, az_config_dir, stdin="mysecret")

    assert "mysecret" not in caplog.text
    assert run.call_args.args[0] == command
    assert run.call_args.kwargs["input"] == b"mysecret"
    assert run.call_args.kwargs["check"] is True
    assert run.call_args.kwargs["stderr"] == subprocess.PIPE
    assert run.call_args.kwargs["env"].get("AZURE_CONFIG_DIR") == az_config_dir


def test_sp_profile_without_client_secret(monkeypatch, tmp_path):
    config = tmp_path / "config.yml"
    config.write_text("my-profile:\n  tenant_id: t\n  client_id: c\n  client_secret:\n")
    monkeypatch.setattr(azure, "SP_CREDENTIALS_FILE", str(config))

    with pytest.raises(azure.AzureError) as excinfo:
        azure.get_sp_profile("my-profile")

    assert '"client_secret" is not set' in excinfo.value.message
