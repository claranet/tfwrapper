"""Test wrapper configuration."""

from copy import deepcopy

import os
import textwrap

import claranet_tfwrapper as tfwrapper


def test_load_wrapper_config_empty_confdir(tmp_working_dir_regional, default_args):
    paths = tmp_working_dir_regional

    os.chdir(paths["stack_dir"])
    wrapper_config = deepcopy(vars(default_args))
    tfwrapper.detect_config_dir(wrapper_config)
    tfwrapper.load_wrapper_config(wrapper_config)
    assert wrapper_config["state"] == {}


def test_load_wrapper_config_confdir_empty(tmp_working_dir_regional, default_args):
    paths = tmp_working_dir_regional

    os.chdir(paths["stack_dir"])
    wrapper_config = deepcopy(vars(default_args))
    tfwrapper.detect_config_dir(wrapper_config)
    tfwrapper.load_wrapper_config(wrapper_config)
    assert wrapper_config["state"] == {}

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


def test_load_wrapper_config_empty_wrapper_config(tmp_working_dir_regional, default_args):
    paths = tmp_working_dir_regional

    os.chdir(paths["stack_dir"])
    wrapper_config = deepcopy(vars(default_args))
    tfwrapper.detect_config_dir(wrapper_config)
    tfwrapper.load_wrapper_config(wrapper_config)
    assert wrapper_config["state"] == {}

    paths["wrapper_conf"].write_text("")
    wrapper_config = deepcopy(vars(default_args))
    tfwrapper.detect_config_dir(wrapper_config)
    tfwrapper.load_wrapper_config(wrapper_config)
    assert wrapper_config["state"] == {}

    paths["wrapper_conf"].write_text("#")
    wrapper_config = deepcopy(vars(default_args))
    tfwrapper.detect_config_dir(wrapper_config)
    tfwrapper.load_wrapper_config(wrapper_config)
    assert wrapper_config["state"] == {}

    paths["wrapper_conf"].write_text("{}")
    wrapper_config = deepcopy(vars(default_args))
    tfwrapper.detect_config_dir(wrapper_config)
    tfwrapper.load_wrapper_config(wrapper_config)
    assert wrapper_config["state"] == {}

    paths["wrapper_conf"].write_text("---")
    wrapper_config = deepcopy(vars(default_args))
    tfwrapper.detect_config_dir(wrapper_config)
    tfwrapper.load_wrapper_config(wrapper_config)
    assert wrapper_config["state"] == {}


def test_load_wrapper_config_use_local_azure_session_directory(tmp_working_dir_regional, default_args):
    paths = tmp_working_dir_regional

    os.chdir(paths["stack_dir"])
    wrapper_config = deepcopy(vars(default_args))
    tfwrapper.detect_config_dir(wrapper_config)
    tfwrapper.load_wrapper_config(wrapper_config)
    assert wrapper_config["config"]["use_local_azure_session_directory"] is True

    paths["wrapper_conf"].write_text("")
    wrapper_config = deepcopy(vars(default_args))
    tfwrapper.detect_config_dir(wrapper_config)
    tfwrapper.load_wrapper_config(wrapper_config)
    assert wrapper_config["config"]["use_local_azure_session_directory"] is True

    paths["wrapper_conf"].write_text("#")
    wrapper_config = deepcopy(vars(default_args))
    tfwrapper.detect_config_dir(wrapper_config)
    tfwrapper.load_wrapper_config(wrapper_config)
    assert wrapper_config["config"]["use_local_azure_session_directory"] is True

    paths["wrapper_conf"].write_text("{}")
    wrapper_config = deepcopy(vars(default_args))
    tfwrapper.detect_config_dir(wrapper_config)
    tfwrapper.load_wrapper_config(wrapper_config)
    assert wrapper_config["config"]["use_local_azure_session_directory"] is True

    paths["wrapper_conf"].write_text("---")
    wrapper_config = deepcopy(vars(default_args))
    tfwrapper.detect_config_dir(wrapper_config)
    tfwrapper.load_wrapper_config(wrapper_config)
    assert wrapper_config["config"]["use_local_azure_session_directory"] is True

    paths["wrapper_conf"].write_text("use_local_azure_session_directory: true")
    wrapper_config = deepcopy(vars(default_args))

    tfwrapper.detect_config_dir(wrapper_config)
    tfwrapper.load_wrapper_config(wrapper_config)
    assert wrapper_config["config"]["use_local_azure_session_directory"] is True

    paths["wrapper_conf"].write_text("use_local_azure_session_directory: false")
    wrapper_config = deepcopy(vars(default_args))
    tfwrapper.detect_config_dir(wrapper_config)
    tfwrapper.load_wrapper_config(wrapper_config)
    assert wrapper_config["config"]["use_local_azure_session_directory"] is False


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
    assert wrapper_config["state"]["aws"]["state_backend_parameters"]["state_snaphot"] == "false"
