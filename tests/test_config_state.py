"""Test state configuration."""

from copy import deepcopy

import os
import textwrap

import claranet_tfwrapper as tfwrapper


def test_load_wrapper_config_empty_state_conf(tmp_working_dir_regional, default_args):
    paths = tmp_working_dir_regional

    paths["state_conf"].write_text("")
    wrapper_config = deepcopy(vars(default_args))
    tfwrapper.detect_config_dir(wrapper_config)
    tfwrapper.load_wrapper_config(wrapper_config)
    assert wrapper_config["state"] == {}

    paths["state_conf"].write_text("#")
    wrapper_config = deepcopy(vars(default_args))
    tfwrapper.detect_config_dir(wrapper_config)
    tfwrapper.load_wrapper_config(wrapper_config)
    assert wrapper_config["state"] == {}

    paths["state_conf"].write_text("{}")
    wrapper_config = deepcopy(vars(default_args))
    tfwrapper.detect_config_dir(wrapper_config)
    tfwrapper.load_wrapper_config(wrapper_config)
    assert wrapper_config["state"] == {}

    paths["state_conf"].write_text("---")
    wrapper_config = deepcopy(vars(default_args))
    tfwrapper.detect_config_dir(wrapper_config)
    tfwrapper.load_wrapper_config(wrapper_config)
    assert wrapper_config["state"] == {}


def test_load_wrapper_config_autodetect_regional(tmp_working_dir_regional, default_args):
    paths = tmp_working_dir_regional

    paths["state_conf"].write_text(
        textwrap.dedent(
            """
            ---
            aws:
                general:
                    account: '12345678910' # the AWS account to use for state storage
                    region: eu-west-1
                credentials:
                    profile: terraform-states-profile # the AWS profile to use for state storage

            backend_parameters:
                state_snaphot: "false"
            """
        )
    )

    os.chdir(paths["stack_dir"])

    wrapper_config = deepcopy(vars(default_args))
    parents_count = tfwrapper.detect_config_dir(wrapper_config)
    tfwrapper.detect_stack(wrapper_config, parents_count)
    tfwrapper.load_wrapper_config(wrapper_config)
    assert wrapper_config["account"] == "testaccount"
    assert wrapper_config["environment"] == "testenvironment"
    assert wrapper_config["region"] == "testregion"
    assert wrapper_config["stack"] == "teststack"
    assert wrapper_config["state"]["aws"]["state_account"] == "12345678910"
    assert wrapper_config["state"]["aws"]["state_region"] == "eu-west-1"
    assert wrapper_config["state"]["aws"]["state_profile"] == "terraform-states-profile"
    assert wrapper_config["state"]["aws"]["account"] == "12345678910"
    assert wrapper_config["state"]["aws"]["region"] == "eu-west-1"
    assert wrapper_config["state"]["aws"]["state_backend_parameters"]["state_snaphot"] == "false"


def test_load_wrapper_config_autodetect_global(tmp_working_dir_global, default_args):
    paths = tmp_working_dir_global

    paths["state_conf"].write_text(
        textwrap.dedent(
            """
            ---
            aws:
                general:
                    account: '12345678910' # the AWS account to use for state storage
                credentials:
                    profile: terraform-states-profile # the AWS profile to use for state storage

            backend_parameters:
                state_snaphot: "false"
            """
        )
    )

    os.chdir(paths["stack_dir"])

    wrapper_config = deepcopy(vars(default_args))
    parents_count = tfwrapper.detect_config_dir(wrapper_config)
    tfwrapper.detect_stack(wrapper_config, parents_count)
    tfwrapper.load_wrapper_config(wrapper_config)
    assert wrapper_config["account"] == "testaccount"
    assert wrapper_config["environment"] == "global"
    assert wrapper_config["region"] is None
    assert wrapper_config["stack"] == "teststack"
    assert wrapper_config["state"]["aws"]["state_account"] == "12345678910"
    assert wrapper_config["state"]["aws"]["state_profile"] == "terraform-states-profile"
    assert wrapper_config["state"]["aws"]["account"] == "12345678910"
    assert wrapper_config["state"]["aws"]["state_backend_parameters"]["state_snaphot"] == "false"


def test_load_wrapper_config_list(tmp_working_dir_regional, default_args):
    paths = tmp_working_dir_regional

    paths["state_conf"].write_text(
        textwrap.dedent(
            """
            ---
            aws:
                - general:
                      account: '12345678910' # the AWS account to use for state storage
                      region: eu-west-1
                  credentials:
                      profile: terraform-states-profile # the AWS profile to use for state storage
                - name: aws_backend2
                  general:
                      account: '10987654321' # the AWS account to use for state storage
                      region: eu-west-2
                  credentials:
                      profile: terraform-states-profile2 # the AWS profile to use for state storage

            backend_parameters:
                state_snaphot: "false"
            """
        )
    )

    os.chdir(paths["stack_dir"])

    wrapper_config = deepcopy(vars(default_args))
    parents_count = tfwrapper.detect_config_dir(wrapper_config)
    tfwrapper.detect_stack(wrapper_config, parents_count)
    tfwrapper.load_wrapper_config(wrapper_config)
    assert wrapper_config["account"] == "testaccount"
    assert wrapper_config["environment"] == "testenvironment"
    assert wrapper_config["region"] == "testregion"
    assert wrapper_config["stack"] == "teststack"
    assert wrapper_config["state"]["aws"]["account"] == "12345678910"
    assert wrapper_config["state"]["aws"]["region"] == "eu-west-1"
    assert wrapper_config["state"]["aws"]["state_account"] == "12345678910"
    assert wrapper_config["state"]["aws"]["state_region"] == "eu-west-1"
    assert wrapper_config["state"]["aws"]["state_profile"] == "terraform-states-profile"
    assert wrapper_config["state"]["aws"]["state_backend_parameters"]["state_snaphot"] == "false"
    assert wrapper_config["state"]["aws_backend2"]["account"] == "10987654321"
    assert wrapper_config["state"]["aws_backend2"]["region"] == "eu-west-2"
    assert wrapper_config["state"]["aws_backend2"]["state_account"] == "10987654321"
    assert wrapper_config["state"]["aws_backend2"]["state_region"] == "eu-west-2"
    assert wrapper_config["state"]["aws_backend2"]["state_profile"] == "terraform-states-profile2"
    assert wrapper_config["state"]["aws_backend2"]["state_backend_parameters"]["state_snaphot"] == "false"


def test_load_wrapper_config_old_map(tmp_working_dir_regional, default_args):
    paths = tmp_working_dir_regional

    paths["state_conf"].write_text(
        textwrap.dedent(
            """
            ---
            aws:
                general:
                    account: '12345678910' # the AWS account to use for state storage
                    region: eu-west-1
                credentials:
                    profile: terraform-states-profile # the AWS profile to use for state storage

            backend_parameters:
                state_snaphot: "false"
            """
        )
    )

    os.chdir(paths["stack_dir"])

    wrapper_config = deepcopy(vars(default_args))
    parents_count = tfwrapper.detect_config_dir(wrapper_config)
    tfwrapper.detect_stack(wrapper_config, parents_count)
    tfwrapper.load_wrapper_config(wrapper_config)
    assert wrapper_config["account"] == "testaccount"
    assert wrapper_config["environment"] == "testenvironment"
    assert wrapper_config["region"] == "testregion"
    assert wrapper_config["stack"] == "teststack"
    assert wrapper_config["state"]["aws"]["state_account"] == "12345678910"
    assert wrapper_config["state"]["aws"]["state_region"] == "eu-west-1"
    assert wrapper_config["state"]["aws"]["state_profile"] == "terraform-states-profile"
    assert wrapper_config["state"]["aws"]["account"] == "12345678910"
    assert wrapper_config["state"]["aws"]["region"] == "eu-west-1"
    assert wrapper_config["state"]["aws"]["state_backend_parameters"]["state_snaphot"] == "false"
