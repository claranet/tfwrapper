"""Test GCP/GKE configuration parsing."""

import textwrap

import claranet_tfwrapper as tfwrapper


def test_aws(tmp_working_dir_empty_conf):
    paths = tmp_working_dir_empty_conf
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
                account: &aws_account '12345678910'
                region: &aws_region eu-west-1
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

    account = "testaccount"
    environment = "testenvironment"
    region = "testregion"
    stack = "teststack"

    stack_config_file = tfwrapper.get_stack_config_path(paths["conf_dir"], account, environment, region, stack)
    parsed_stack_config = tfwrapper.load_stack_config_from_file(stack_config_file)

    expected_config = {
        "aws": {"general": {"account": "12345678910", "region": "eu-west-1"}, "credentials": {"profile": "account-alias"}},
        "terraform": {"vars": {"client_name": "claranet", "aws_account": "12345678910", "aws_region": "eu-west-1"}},
    }

    assert parsed_stack_config == expected_config


def test_stack_with_underscores(tmp_working_dir_empty_conf):
    paths = tmp_working_dir_empty_conf
    stack_config_b = paths["conf_dir"] / "testaccount_testenvironment_testregion_teststack_with_underscores.yml"
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
                account: &aws_account '12345678910'
                region: &aws_region eu-west-1
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

    account = "testaccount"
    environment = "testenvironment"
    region = "testregion"
    stack = "teststack_with_underscores"

    stack_config_file = tfwrapper.get_stack_config_path(paths["conf_dir"], account, environment, region, stack)
    parsed_stack_config = tfwrapper.load_stack_config_from_file(stack_config_file)

    expected_config = {
        "aws": {"general": {"account": "12345678910", "region": "eu-west-1"}, "credentials": {"profile": "account-alias"}},
        "terraform": {"vars": {"client_name": "claranet", "aws_account": "12345678910", "aws_region": "eu-west-1"}},
    }

    assert parsed_stack_config == expected_config


def test_azure_user(tmp_working_dir_empty_conf):
    paths = tmp_working_dir_empty_conf
    stack_config_b = paths["conf_dir"] / "testaccount_testenvironment_testregion_teststack.yml"
    stack_config_b.write_text(
        textwrap.dedent(
            """
            ---
            azure:
              general:
                mode: user
                directory_id: &directory_id '00000000-0000-0000-0000-000000000000'
                subscription_id: &subscription_id '11111111-1111-1111-1111-111111111111'

            terraform:
              vars:
                version: "1.0"
                subscription_id: *subscription_id
                directory_id: *directory_id
            """
        )
    )

    account = "testaccount"
    environment = "testenvironment"
    region = "testregion"
    stack = "teststack"

    stack_config_file = tfwrapper.get_stack_config_path(paths["conf_dir"], account, environment, region, stack)
    parsed_stack_config = tfwrapper.load_stack_config_from_file(stack_config_file)

    expected_config = {
        "azure": {
            "general": {
                "mode": "user",
                "directory_id": "00000000-0000-0000-0000-000000000000",
                "subscription_id": "11111111-1111-1111-1111-111111111111",
            }
        },
        "terraform": {
            "vars": {
                "version": "1.0",
                "directory_id": "00000000-0000-0000-0000-000000000000",
                "subscription_id": "11111111-1111-1111-1111-111111111111",
            }
        },
    }

    assert parsed_stack_config == expected_config


def test_azure_sp(tmp_working_dir_empty_conf):
    paths = tmp_working_dir_empty_conf
    stack_config_b = paths["conf_dir"] / "testaccount_testenvironment_testregion_teststack.yml"
    stack_config_b.write_text(
        textwrap.dedent(
            """
            ---
            azure:
              general:
                mode: service_principal
                directory_id: &directory_id '00000000-0000-0000-0000-000000000000'
                subscription_id: &subscription_id '11111111-1111-1111-1111-111111111111'
              credentials:
                profile: azurerm-account-profile

            terraform:
              vars:
                version: "1.0"
                subscription_id: *subscription_id
                directory_id: *directory_id
            """
        )
    )

    account = "testaccount"
    environment = "testenvironment"
    region = "testregion"
    stack = "teststack"

    stack_config_file = tfwrapper.get_stack_config_path(paths["conf_dir"], account, environment, region, stack)
    parsed_stack_config = tfwrapper.load_stack_config_from_file(stack_config_file)

    expected_config = {
        "azure": {
            "general": {
                "mode": "service_principal",
                "directory_id": "00000000-0000-0000-0000-000000000000",
                "subscription_id": "11111111-1111-1111-1111-111111111111",
            },
            "credentials": {"profile": "azurerm-account-profile"},
        },
        "terraform": {
            "vars": {
                "version": "1.0",
                "directory_id": "00000000-0000-0000-0000-000000000000",
                "subscription_id": "11111111-1111-1111-1111-111111111111",
            }
        },
    }

    assert parsed_stack_config == expected_config


def test_azure_sp_compat(tmp_working_dir_empty_conf):
    paths = tmp_working_dir_empty_conf
    stack_config_b = paths["conf_dir"] / "testaccount_testenvironment_testregion_teststack.yml"
    stack_config_b.write_text(
        textwrap.dedent(
            """
            ---
            azure:
              general:
                mode: service_principal
                directory_id: &directory_id '00000000-0000-0000-0000-000000000000'
                subscription_id: &subscription_id '11111111-1111-1111-1111-111111111111'
              credential:
                profile: azurerm-account-profile

            terraform:
              vars:
                version: "1.0"
                subscription_id: *subscription_id
                directory_id: *directory_id
            """
        )
    )

    account = "testaccount"
    environment = "testenvironment"
    region = "testregion"
    stack = "teststack"

    stack_config_file = tfwrapper.get_stack_config_path(paths["conf_dir"], account, environment, region, stack)
    parsed_stack_config = tfwrapper.load_stack_config_from_file(stack_config_file)

    expected_config = {
        "azure": {
            "general": {
                "mode": "service_principal",
                "directory_id": "00000000-0000-0000-0000-000000000000",
                "subscription_id": "11111111-1111-1111-1111-111111111111",
            },
            "credential": {"profile": "azurerm-account-profile"},
        },
        "terraform": {
            "vars": {
                "version": "1.0",
                "directory_id": "00000000-0000-0000-0000-000000000000",
                "subscription_id": "11111111-1111-1111-1111-111111111111",
            }
        },
    }

    assert parsed_stack_config == expected_config


def test_azure_sp_multiple(tmp_working_dir_empty_conf):
    paths = tmp_working_dir_empty_conf
    stack_config_b = paths["conf_dir"] / "testaccount_testenvironment_testregion_teststack.yml"
    stack_config_b.write_text(
        textwrap.dedent(
            """
            ---
            azure:
              general:
                mode: service_principal
                directory_id: &directory_id '00000000-0000-0000-0000-000000000000'
                subscription_id: &subscription_id '11111111-1111-1111-1111-111111111111'
                credentials:
                  profile: azurerm-account-profile
              alternative:
                mode: service_principal
                directory_id: '22222222-2222-2222-2222-222222222222'
                subscription_id: '33333333-3333-3333-3333-333333333333'
                credentials:
                  profile: azurerm-account-profile2

            terraform:
              vars:
                version: "1.0"
                subscription_id: *subscription_id
                directory_id: *directory_id
            """
        )
    )

    account = "testaccount"
    environment = "testenvironment"
    region = "testregion"
    stack = "teststack"

    stack_config_file = tfwrapper.get_stack_config_path(paths["conf_dir"], account, environment, region, stack)
    parsed_stack_config = tfwrapper.load_stack_config_from_file(stack_config_file)

    expected_config = {
        "azure": {
            "general": {
                "mode": "service_principal",
                "directory_id": "00000000-0000-0000-0000-000000000000",
                "subscription_id": "11111111-1111-1111-1111-111111111111",
                "credentials": {"profile": "azurerm-account-profile"},
            },
            "alternative": {
                "mode": "service_principal",
                "directory_id": "22222222-2222-2222-2222-222222222222",
                "subscription_id": "33333333-3333-3333-3333-333333333333",
                "credentials": {"profile": "azurerm-account-profile2"},
            },
        },
        "terraform": {
            "vars": {
                "version": "1.0",
                "subscription_id": "11111111-1111-1111-1111-111111111111",
                "directory_id": "00000000-0000-0000-0000-000000000000",
            }
        },
    }

    assert parsed_stack_config == expected_config
