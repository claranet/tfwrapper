"""Test stacks and states configurations."""

import os
import textwrap
import pytest

from unittest.mock import MagicMock

import claranet_tfwrapper as tfwrapper
from claranet_tfwrapper import azure


def test_basic_aws_backend(monkeypatch, tmp_working_dir_regional_valid):
    paths = tmp_working_dir_regional_valid
    stack_config_b = paths["conf_dir"] / "testaccount_testenvironment_testregion_teststack.yml"
    paths["state_conf"].write_text(
        textwrap.dedent(
            """
            ---
            aws:
                general:
                    account: '12345678910'
                    region: eu-west-1
                credentials:
                    profile: terraform-states-profile

            backend_parameters:
                state_snaphot: "false"
            """
        )
    )
    stack_config_b.write_text(
        textwrap.dedent(
            """
            ---
            aws:
              general:
                account: &aws_account '9876543210'
                region: &aws_region eu-west-2
              credentials:
                profile: account-alias
            terraform:
              vars:
                client_name: claranet
                aws_account: *aws_account
                aws_region: *aws_region
            """
        )
    )

    get_session = MagicMock()
    aws_state_session = MagicMock()
    aws_state_session_credentials = MagicMock()
    aws_state_session_frozen_credentials = MagicMock()
    aws_state_session_frozen_credentials.access_key = "state access key"
    aws_state_session_frozen_credentials.secret_key = "state secret key"
    aws_state_session_frozen_credentials.token = "state token"
    aws_state_session.get_credentials = lambda: aws_state_session_credentials
    aws_state_session_credentials.get_frozen_credentials = lambda: aws_state_session_frozen_credentials

    aws_stack_session = MagicMock()
    aws_stack_session_credentials = MagicMock()
    aws_stack_session_frozen_credentials = MagicMock()
    aws_stack_session_frozen_credentials.access_key = "stack access key"
    aws_stack_session_frozen_credentials.secret_key = "stack secret key"
    aws_stack_session_frozen_credentials.token = "stack token"
    aws_stack_session.get_credentials = lambda: aws_stack_session_credentials
    aws_stack_session_credentials.get_frozen_credentials = lambda: aws_stack_session_frozen_credentials

    def get_session_func(wrapper_config, account, region, profile, backend_type=None, conf=None):
        assert wrapper_config["state"] == {
            "aws": {
                "account": "12345678910",
                "region": "eu-west-1",
                "state_backend_type": "aws",
                "state_backend_parameters": {"state_snaphot": "false"},
                "state_subscription": None,
                "state_rg": None,
                "state_storage": None,
                "state_account": "12345678910",
                "state_region": "eu-west-1",
                "state_profile": "terraform-states-profile",
            }
        }
        assert wrapper_config["stack"] == "teststack"
        assert wrapper_config["environment"] == "testenvironment"
        assert wrapper_config["region"] == "testregion"
        assert wrapper_config["account"] == "testaccount"
        assert backend_type == "aws"

        if conf is None:  # Stack session
            assert account == "9876543210"
            assert region == "eu-west-2"
            assert profile == "account-alias"
            return aws_stack_session
        else:  # State session
            assert account == "12345678910"
            assert region == "eu-west-1"
            assert profile == "terraform-states-profile"
            assert conf == {
                "account": "12345678910",
                "region": "eu-west-1",
                "state_backend_type": "aws",
                "state_backend_parameters": {"state_snaphot": "false"},
                "state_subscription": None,
                "state_rg": None,
                "state_storage": None,
                "state_account": "12345678910",
                "state_region": "eu-west-1",
                "state_profile": "terraform-states-profile",
            }
            return aws_state_session

    get_session.side_effect = get_session_func
    aws_state_session.get_credentials = lambda: aws_state_session_credentials
    aws_state_session_credentials.get_frozen_credentials = lambda: aws_state_session_frozen_credentials
    monkeypatch.setattr(tfwrapper, "get_session", get_session)

    tf_init = MagicMock()
    tf_init.side_effect = lambda x: 0
    monkeypatch.setattr(tfwrapper, "terraform_init", tf_init)

    with pytest.raises(SystemExit) as e:
        tfwrapper.main(["-d", "-atestaccount", "-etestenvironment", "-rtestregion", "-steststack", "init"])
    assert e.type is SystemExit
    assert e.value.code == 0

    get_session.assert_called()
    tf_init.assert_called_once()


def test_basic_azure_backend(monkeypatch, tmp_working_dir_regional_valid):
    paths = tmp_working_dir_regional_valid
    stack_config_b = paths["conf_dir"] / "testaccount_testenvironment_testregion_teststack.yml"
    paths["state_conf"].write_text(
        textwrap.dedent(
            """
            ---
            azure:
                general:
                    subscription_id: '00000000-0000-0000-0000-000000000000'
                    resource_group_name: 'rg-test' # The Azure resource group with state storage
                    storage_account_name: 'sttest' # The Azure storage account
                    additional_param: additional_value
            backend_parameters:
                state_snaphot: "false"
            """
        )
    )
    stack_config_b.write_text(
        textwrap.dedent(
            """
            ---
            azure:
                general:
                    mode: service_principal # Uses an Azure tenant Service Principal account
                    directory_id: &directory_id '11111111-1111-1111-1111-111111111111'
                    subscription_id: &subscription_id '22222222-2222-2222-2222-222222222222'
                    credentials:
                        profile: stack-profile
            terraform:
                vars:
                    client_name: claranet
                    subscription_id: *subscription_id
                    directory_id: *directory_id
            """
        )
    )

    get_session = MagicMock()

    def get_session_func(wrapper_config, account, region, profile, backend_type=None, conf=None):
        assert account is None
        assert region is None
        assert profile is None
        assert backend_type == "azure"
        assert wrapper_config["stack"] == "teststack"
        assert wrapper_config["environment"] == "testenvironment"
        assert wrapper_config["region"] == "testregion"
        assert wrapper_config["account"] == "testaccount"
        assert wrapper_config["state"] == {
            "azure": {
                "subscription_id": "00000000-0000-0000-0000-000000000000",
                "resource_group_name": "rg-test",
                "storage_account_name": "sttest",
                "state_backend_type": "azure",
                "state_backend_parameters": {"state_snaphot": "false"},
                "state_subscription": "00000000-0000-0000-0000-000000000000",
                "state_rg": "rg-test",
                "state_storage": "sttest",
                "state_account": None,
                "state_region": None,
                "state_profile": None,
                "additional_param": "additional_value",
            }
        }
        return {"state_session": "yes"}

    get_session.side_effect = get_session_func
    monkeypatch.setattr(tfwrapper, "get_session", get_session)

    def azure_set_context_func(wrapper_config, subscription_id, tenant_id, context_name, sp_profile=None, backend_context=False):
        assert context_name == ""
        if backend_context:
            assert subscription_id == "00000000-0000-0000-0000-000000000000"
            assert sp_profile is None
        else:
            assert subscription_id == "22222222-2222-2222-2222-222222222222"
            assert sp_profile == "stack-profile"
        return {"my_var": "my_value"}

    azure_set_context = MagicMock()
    azure_set_context.side_effect = azure_set_context_func
    monkeypatch.setattr(azure, "set_context", azure_set_context)

    tf_init = MagicMock()
    tf_init.side_effect = lambda x: 0
    monkeypatch.setattr(tfwrapper, "terraform_init", tf_init)

    with pytest.raises(SystemExit) as e:
        tfwrapper.main(["-d", "-atestaccount", "-etestenvironment", "-rtestregion", "-steststack", "init"])
    assert e.type is SystemExit
    assert e.value.code == 0
    assert os.environ["TF_VAR_my_var"] == "my_value"
    assert os.environ["TF_VAR_state_session"] == "yes"

    get_session.assert_called_once()
    tf_init.assert_called_once()


def test_basic_azure_aws_backend(monkeypatch, tmp_working_dir_regional_valid):
    paths = tmp_working_dir_regional_valid
    stack_config_b = paths["conf_dir"] / "testaccount_testenvironment_testregion_teststack.yml"
    paths["state_conf"].write_text(
        textwrap.dedent(
            """
            ---
            aws:
                general:
                    account: '12345678910'
                    region: eu-west-1
                credentials:
                    profile: terraform-states-profile

            azure:
                general:
                    subscription_id: '00000000-0000-0000-0000-000000000000'
                    resource_group_name: 'rg-test' # The Azure resource group with state storage
                    storage_account_name: 'sttest' # The Azure storage account
                    additional_param: additional_value
                    credentials:
                        profile: state-profile
            backend_parameters:
                state_snaphot: "false"
            """
        )
    )
    stack_config_b.write_text(
        textwrap.dedent(
            """
            ---
            state_configuration_name: azure
            azure:
                general:
                    mode: service_principal # Uses an Azure tenant Service Principal account
                    directory_id: &directory_id '11111111-1111-1111-1111-111111111111'
                    subscription_id: &subscription_id '22222222-2222-2222-2222-222222222222'
                    credentials:
                        profile: stack-profile
            terraform:
                vars:
                    client_name: claranet
                    subscription_id: *subscription_id
                    directory_id: *directory_id
            """
        )
    )

    get_session = MagicMock()

    def get_session_func(wrapper_config, account, region, profile, backend_type=None, conf=None):
        assert account is None
        assert region is None
        assert profile is None
        assert backend_type == "azure"
        assert wrapper_config["stack"] == "teststack"
        assert wrapper_config["environment"] == "testenvironment"
        assert wrapper_config["region"] == "testregion"
        assert wrapper_config["account"] == "testaccount"
        assert wrapper_config["state"] == {
            "azure": {
                "subscription_id": "00000000-0000-0000-0000-000000000000",
                "resource_group_name": "rg-test",
                "storage_account_name": "sttest",
                "credentials": {"profile": "state-profile"},
                "state_backend_type": "azure",
                "state_backend_parameters": {"state_snaphot": "false"},
                "state_subscription": "00000000-0000-0000-0000-000000000000",
                "state_rg": "rg-test",
                "state_storage": "sttest",
                "state_account": None,
                "state_region": None,
                "state_profile": None,
                "additional_param": "additional_value",
            },
            "aws": {
                "account": "12345678910",
                "region": "eu-west-1",
                "state_backend_type": "aws",
                "state_backend_parameters": {"state_snaphot": "false"},
                "state_subscription": None,
                "state_rg": None,
                "state_storage": None,
                "state_account": "12345678910",
                "state_region": "eu-west-1",
                "state_profile": "terraform-states-profile",
            },
        }
        return {"state_session": "yes"}

    get_session.side_effect = get_session_func
    monkeypatch.setattr(tfwrapper, "get_session", get_session)

    def azure_set_context_func(wrapper_config, subscription_id, tenant_id, context_name, sp_profile=None, backend_context=False):
        assert context_name == ""
        if backend_context:
            assert subscription_id == "00000000-0000-0000-0000-000000000000"
            assert sp_profile == "state-profile"
        else:
            assert subscription_id == "22222222-2222-2222-2222-222222222222"
            assert sp_profile == "stack-profile"
        return {"my_var": "my_value"}

    azure_set_context = MagicMock()
    azure_set_context.side_effect = azure_set_context_func
    monkeypatch.setattr(azure, "set_context", azure_set_context)

    tf_init = MagicMock()
    tf_init.side_effect = lambda x: 0
    monkeypatch.setattr(tfwrapper, "terraform_init", tf_init)

    with pytest.raises(SystemExit) as e:
        tfwrapper.main(["-d", "-atestaccount", "-etestenvironment", "-rtestregion", "-steststack", "init"])
    assert e.type is SystemExit
    assert e.value.code == 0
    assert os.environ["TF_VAR_my_var"] == "my_value"
    assert os.environ["TF_VAR_state_session"] == "yes"

    get_session.assert_called_once()
    tf_init.assert_called_once()


def test_basic_named_backend(monkeypatch, tmp_working_dir_regional_valid):
    paths = tmp_working_dir_regional_valid
    stack_config_b = paths["conf_dir"] / "testaccount_testenvironment_testregion_teststack.yml"
    paths["state_conf"].write_text(
        textwrap.dedent(
            """
            ---
            aws:
                general:
                    account: '12345678910'
                    region: eu-west-1
                credentials:
                    profile: terraform-states-profile

            azure:
                - name: backend1
                  general:
                      subscription_id: '00000000-0000-0000-0000-000000000000'
                      resource_group_name: 'rg-test' # The Azure resource group with state storage
                      storage_account_name: 'sttest' # The Azure storage account
                      additional_param: additional_value
                      credentials:
                          profile: state-profile
                - name: backend2
                  general:
                      subscription_id: '33333333-3333-3333-3333-333333333333'
                      resource_group_name: 'rg-test2' # The Azure resource group with state storage
                      storage_account_name: 'sttest2' # The Azure storage account
                      additional_param2: additional_value2
                      credentials:
                          profile: state-profile2
            backend_parameters:
                state_snaphot: "false"
            """
        )
    )
    stack_config_b.write_text(
        textwrap.dedent(
            """
            ---
            state_configuration_name: backend2
            azure:
                general:
                    mode: service_principal # Uses an Azure tenant Service Principal account
                    directory_id: &directory_id '11111111-1111-1111-1111-111111111111'
                    subscription_id: &subscription_id '22222222-2222-2222-2222-222222222222'
                    credentials:
                        profile: stack-profile
            terraform:
                vars:
                    client_name: claranet
                    subscription_id: *subscription_id
                    directory_id: *directory_id
            """
        )
    )

    get_session = MagicMock()

    def get_session_func(wrapper_config, account, region, profile, backend_type=None, conf=None):
        assert account is None
        assert region is None
        assert profile is None
        assert backend_type == "azure"
        assert wrapper_config["stack"] == "teststack"
        assert wrapper_config["environment"] == "testenvironment"
        assert wrapper_config["region"] == "testregion"
        assert wrapper_config["account"] == "testaccount"
        assert wrapper_config["state"] == {
            "backend1": {
                "subscription_id": "00000000-0000-0000-0000-000000000000",
                "resource_group_name": "rg-test",
                "storage_account_name": "sttest",
                "credentials": {"profile": "state-profile"},
                "state_backend_type": "azure",
                "state_backend_parameters": {"state_snaphot": "false"},
                "state_subscription": "00000000-0000-0000-0000-000000000000",
                "state_rg": "rg-test",
                "state_storage": "sttest",
                "state_account": None,
                "state_region": None,
                "state_profile": None,
                "additional_param": "additional_value",
            },
            "backend2": {
                "subscription_id": "33333333-3333-3333-3333-333333333333",
                "resource_group_name": "rg-test2",
                "storage_account_name": "sttest2",
                "credentials": {"profile": "state-profile2"},
                "state_backend_type": "azure",
                "state_backend_parameters": {"state_snaphot": "false"},
                "state_subscription": "33333333-3333-3333-3333-333333333333",
                "state_rg": "rg-test2",
                "state_storage": "sttest2",
                "state_account": None,
                "state_region": None,
                "state_profile": None,
                "additional_param2": "additional_value2",
            },
            "aws": {
                "account": "12345678910",
                "region": "eu-west-1",
                "state_backend_type": "aws",
                "state_backend_parameters": {"state_snaphot": "false"},
                "state_subscription": None,
                "state_rg": None,
                "state_storage": None,
                "state_account": "12345678910",
                "state_region": "eu-west-1",
                "state_profile": "terraform-states-profile",
            },
        }
        return {"state_session": "yes"}

    get_session.side_effect = get_session_func
    monkeypatch.setattr(tfwrapper, "get_session", get_session)

    def azure_set_context_func(wrapper_config, subscription_id, tenant_id, context_name, sp_profile=None, backend_context=False):
        assert context_name == ""
        if backend_context:
            assert subscription_id == "33333333-3333-3333-3333-333333333333"
            assert sp_profile == "state-profile2"
        else:
            assert subscription_id == "22222222-2222-2222-2222-222222222222"
            assert sp_profile == "stack-profile"
        return {"my_var": "my_value"}

    azure_set_context = MagicMock()
    azure_set_context.side_effect = azure_set_context_func
    monkeypatch.setattr(azure, "set_context", azure_set_context)

    tf_init = MagicMock()
    tf_init.side_effect = lambda x: 0
    monkeypatch.setattr(tfwrapper, "terraform_init", tf_init)

    with pytest.raises(SystemExit) as e:
        tfwrapper.main(["-d", "-atestaccount", "-etestenvironment", "-rtestregion", "-steststack", "init"])
    assert e.type is SystemExit
    assert e.value.code == 0
    assert os.environ["TF_VAR_my_var"] == "my_value"
    assert os.environ["TF_VAR_state_session"] == "yes"

    get_session.assert_called_once()
    tf_init.assert_called_once()
