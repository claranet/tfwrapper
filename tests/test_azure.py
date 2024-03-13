"""Test azure related functions."""

import os
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
        ["az", "login", "--service-principal", "--username", client_id, "--password", client_secret, "--tenant", tenant_id],
        os.path.join(tmp_path, ".run", "azure"),
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
        ["az", "login", "--service-principal", "--username", client_id, "--password", client_secret, "--tenant", tenant_id],
        os.path.join(tmp_path, ".run", "azure"),
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
            "--password",
            alt_client_secret,
            "--tenant",
            alt_tenant_id,
        ],
        os.path.join(tmp_path, ".run", "azure_alternative"),
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
