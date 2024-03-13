"""Test state configuration."""

import textwrap

import claranet_tfwrapper as tfwrapper


def test_load_stack_config_missing(tmp_working_dir_regional):
    paths = tmp_working_dir_regional

    account = "testaccount"
    environment = "testenvironment"
    region = "testregion"
    stack = "teststack"

    stack_config_file = tfwrapper.get_stack_config_path(paths["conf_dir"], account, environment, region, stack)

    stack_config = tfwrapper.load_stack_config_from_file(stack_config_file)
    assert stack_config == {}


def test_load_stack_config_from_file_exists(tmp_working_dir_regional):
    paths = tmp_working_dir_regional

    account = "testaccount"
    environment = "testenvironment"
    region = "testregion"
    stack = "teststack"

    stack_config_file = paths["conf_dir"] / "{}_{}_{}_{}.yml".format(account, environment, region, stack)

    stack_config_file.write_text(
        textwrap.dedent(
            """
            ---
            aws:
                general:
                    account: &aws_account "12345678910" # the AWS account to use for state storage
                    region: &aws_region eu-west-3
                credentials:
                    profile: &aws_account_alias terraform-stack-profile

            terraform:
                vars:
                    aws_account: *aws_account
                    aws_account_alias: *aws_account_alias
                    aws_region: *aws_region
                    client_name: claranet
                    version: "1.1.7"
            """
        )
    )

    stack_config = tfwrapper.load_stack_config_from_file(stack_config_file)
    assert stack_config == {
        "aws": {
            "credentials": {"profile": "terraform-stack-profile"},
            "general": {"account": "12345678910", "region": "eu-west-3"},
        },
        "terraform": {
            "vars": {
                "aws_account": "12345678910",
                "aws_account_alias": "terraform-stack-profile",
                "aws_region": "eu-west-3",
                "client_name": "claranet",
                "version": "1.1.7",
            }
        },
    }
