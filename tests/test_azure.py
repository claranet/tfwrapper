"""Test azure related functions."""

import os
import subprocess
from unittest.mock import MagicMock

import claranet_tfwrapper.azure as azure


def test_user_context(monkeypatch, tmp_path):  # noqa: D103
    wrapper_config = {"rootdir": tmp_path, "config": {"use_local_azure_session_directory": True}}
    subscription_id = "00000000-0000-0000-0000-000000000000"
    tenant_id = "11111111-1111-1111-1111-111111111111"

    subprocess_mock = MagicMock()

    monkeypatch.setattr(subprocess, "run", subprocess_mock)

    azure.set_context(wrapper_config, subscription_id, tenant_id=tenant_id)

    subprocess_mock.assert_called_once_with(
        ["az", "account", "get-access-token", "-s", subscription_id], check=True, capture_output=True
    )
    assert os.environ.get("AZURE_CONFIG_DIR", None) == os.path.join(tmp_path, ".run", "azure")


def test_user_context_no_isolation(monkeypatch, tmp_path):  # noqa: D103
    wrapper_config = {"rootdir": tmp_path, "config": {"use_local_azure_session_directory": False}}
    subscription_id = "00000000-0000-0000-0000-000000000000"
    tenant_id = "11111111-1111-1111-1111-111111111111"

    subprocess_mock = MagicMock()
    monkeypatch.setattr(subprocess, "run", subprocess_mock)

    azure.set_context(wrapper_config, subscription_id, tenant_id=tenant_id)

    subprocess_mock.assert_called_once_with(
        ["az", "account", "get-access-token", "-s", subscription_id], check=True, capture_output=True
    )
    assert os.environ.get("AZURE_CONFIG_DIR", "") == ""


def test_sp_context(monkeypatch, tmp_path):  # noqa: D103
    wrapper_config = {"rootdir": tmp_path, "config": {"use_local_azure_session_directory": True}}
    subscription_id = "00000000-0000-0000-0000-000000000000"
    tenant_id = "11111111-1111-1111-1111-111111111111"
    client_id = "22222222-2222-2222-2222-222222222222"
    client_secret = "mysecret"

    subprocess_mock = MagicMock()
    monkeypatch.setattr(subprocess, "run", subprocess_mock)
    subprocess_mock.return_value = {"ret": 0}

    sp_profile_mock = MagicMock()
    monkeypatch.setattr(azure, "get_sp_profile", sp_profile_mock)
    sp_profile_mock.return_value = (tenant_id, client_id, client_secret)

    azure.set_context(wrapper_config, subscription_id, tenant_id=tenant_id, sp_profile="my-profile")

    subprocess_mock.assert_called_once_with(
        ["az", "login", "--service-principal", "--username", client_id, "--password", client_secret, "--tenant", tenant_id],
        check=True,
        capture_output=True,
        universal_newlines=True,
        env=None,
    )
    sp_profile_mock.assert_called_once_with("my-profile")
    assert os.environ.get("AZURE_CONFIG_DIR", None) == os.path.join(tmp_path, ".run", "azure")
    assert os.environ.get("ARM_CLIENT_ID", None) == client_id
    assert os.environ.get("ARM_CLIENT_SECRET", None) == client_secret
    assert os.environ.get("ARM_TENANT_ID", None) == tenant_id


def test_user_context_backend(monkeypatch, tmp_path):  # noqa: D103
    wrapper_config = {"rootdir": tmp_path, "config": {"use_local_azure_session_directory": True}}
    subscription_id = "00000000-0000-0000-0000-000000000000"
    tenant_id = "11111111-1111-1111-1111-111111111111"

    subprocess_mock = MagicMock()

    monkeypatch.setattr(subprocess, "run", subprocess_mock)

    azure.set_context(wrapper_config, subscription_id, tenant_id=tenant_id, backend_context=True)

    subprocess_mock.assert_called_once_with(
        ["az", "account", "get-access-token", "-s", subscription_id], check=True, capture_output=True
    )
    assert os.environ.get("AZURE_CONFIG_DIR", None) == os.path.join(tmp_path, ".run", "azure")


def test_user_context_backend_no_isolation(monkeypatch, tmp_path):  # noqa: D103
    wrapper_config = {"rootdir": tmp_path, "config": {"use_local_azure_session_directory": False}}
    subscription_id = "00000000-0000-0000-0000-000000000000"
    tenant_id = "11111111-1111-1111-1111-111111111111"

    subprocess_mock = MagicMock()
    monkeypatch.setattr(subprocess, "run", subprocess_mock)

    azure.set_context(wrapper_config, subscription_id, tenant_id=tenant_id, backend_context=True)

    subprocess_mock.assert_called_once_with(
        ["az", "account", "get-access-token", "-s", subscription_id], check=True, capture_output=True
    )
    assert os.environ.get("AZURE_CONFIG_DIR", "") == ""


def test_sp_context_backend(monkeypatch, tmp_path):  # noqa: D103
    wrapper_config = {"rootdir": tmp_path, "config": {"use_local_azure_session_directory": True}}
    subscription_id = "00000000-0000-0000-0000-000000000000"
    tenant_id = "11111111-1111-1111-1111-111111111111"
    client_id = "22222222-2222-2222-2222-222222222222"
    client_secret = "mysecret"

    subprocess_mock = MagicMock()
    monkeypatch.setattr(subprocess, "run", subprocess_mock)
    subprocess_mock.return_value = {"ret": 0}

    sp_profile_mock = MagicMock()
    monkeypatch.setattr(azure, "get_sp_profile", sp_profile_mock)
    sp_profile_mock.return_value = (tenant_id, client_id, client_secret)

    azure.set_context(wrapper_config, subscription_id, tenant_id=tenant_id, sp_profile="my-profile", backend_context=True)

    subprocess_mock.assert_called_once_with(
        ["az", "login", "--service-principal", "--username", client_id, "--password", client_secret, "--tenant", tenant_id],
        check=True,
        capture_output=True,
        universal_newlines=True,
        env={"AZURE_CONFIG_DIR": os.path.join(tmp_path, ".run", "azure_backend")},
    )
    sp_profile_mock.assert_called_once_with("my-profile")
    assert os.environ.get("AZURE_CONFIG_DIR", None) == os.path.join(tmp_path, ".run", "azure")
    assert os.environ.get("ARM_CLIENT_ID", None) is None
    assert os.environ.get("ARM_CLIENT_SECRET", None) is None
    assert os.environ.get("ARM_TENANT_ID", None) is None
    assert os.environ.get("TF_VAR_azure_state_client_id", None) == client_id
    assert os.environ.get("TF_VAR_azure_state_client_secret", None) == client_secret
    assert os.environ.get("TF_VAR_azure_state_client_tenant_id", None) == tenant_id
