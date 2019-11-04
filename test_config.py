from importlib.machinery import SourceFileLoader

from copy import deepcopy

import os
import textwrap

import pytest

tfwrapper = SourceFileLoader("tfwrapper", "bin/tfwrapper").load_module()


@pytest.fixture
def tmp_working_dir_regional(tmp_working_dir_empty_conf):
    paths = tmp_working_dir_empty_conf
    paths["account_dir"] = paths["working_dir"] / "testaccount"
    paths["environment_dir"] = paths["account_dir"] / "testenvironment"
    paths["region_dir"] = paths["environment_dir"] / "testregion"
    paths["stack_dir"] = paths["region_dir"] / "teststack"
    paths["stack_dir"].mkdir(parents=True)

    return paths


@pytest.fixture
def tmp_working_dir_global(tmp_working_dir_empty_conf):
    paths = tmp_working_dir_empty_conf
    paths["account_dir"] = paths["working_dir"] / "testaccount"
    paths["environment_dir"] = paths["account_dir"] / "_global"
    paths["stack_dir"] = paths["environment_dir"] / "teststack"
    paths["stack_dir"].mkdir(parents=True)

    return paths


def test_detect_config_dir_confdir_not_found(tmp_working_dir, default_args):
    wrapper_config = deepcopy(vars(default_args))

    with pytest.raises(ValueError) as e:
        wrapper_config = tfwrapper.detect_config_dir(wrapper_config)
    assert "Cannot find configuration directory" in str(e.value)


def test_detect_config_dir_empty(tmp_working_dir_empty_conf, default_args):
    wrapper_config = deepcopy(vars(default_args))

    parents_count = tfwrapper.detect_config_dir(wrapper_config)
    assert parents_count == 0


def test_detect_config_dir_regional(tmp_working_dir_regional, default_args):
    paths = tmp_working_dir_regional
    wrapper_config = deepcopy(vars(default_args))

    parents_count = tfwrapper.detect_config_dir(wrapper_config)
    assert parents_count == 0

    wrapper_config = deepcopy(vars(default_args))
    os.chdir(paths["account_dir"])

    parents_count = tfwrapper.detect_config_dir(wrapper_config)
    assert parents_count == 1

    wrapper_config = deepcopy(vars(default_args))
    os.chdir(paths["environment_dir"])

    parents_count = tfwrapper.detect_config_dir(wrapper_config)
    assert parents_count == 2

    wrapper_config = deepcopy(vars(default_args))
    os.chdir(paths["region_dir"])

    parents_count = tfwrapper.detect_config_dir(wrapper_config)
    assert parents_count == 3

    wrapper_config = deepcopy(vars(default_args))
    os.chdir(paths["stack_dir"])

    parents_count = tfwrapper.detect_config_dir(wrapper_config)
    assert parents_count == 4


def test_detect_config_dir_global(tmp_working_dir_global, default_args):
    paths = tmp_working_dir_global
    wrapper_config = deepcopy(vars(default_args))

    parents_count = tfwrapper.detect_config_dir(wrapper_config)
    assert parents_count == 0

    wrapper_config = deepcopy(vars(default_args))
    os.chdir(paths["account_dir"])

    parents_count = tfwrapper.detect_config_dir(wrapper_config)
    assert parents_count == 1

    wrapper_config = deepcopy(vars(default_args))
    os.chdir(paths["environment_dir"])

    parents_count = tfwrapper.detect_config_dir(wrapper_config)
    assert parents_count == 2

    wrapper_config = deepcopy(vars(default_args))
    os.chdir(paths["stack_dir"])

    parents_count = tfwrapper.detect_config_dir(wrapper_config)
    assert parents_count == 3


def test_detect_stack_regional(tmp_working_dir_regional, default_args):
    paths = tmp_working_dir_regional

    wrapper_config = deepcopy(vars(default_args))
    parents_count = tfwrapper.detect_config_dir(wrapper_config)
    with pytest.raises(ValueError) as e:
        tfwrapper.detect_stack(wrapper_config, parents_count)
    assert "account cannot be autodetected" in str(e.value)

    os.chdir(paths["account_dir"])
    wrapper_config = deepcopy(vars(default_args))
    parents_count = tfwrapper.detect_config_dir(wrapper_config)
    with pytest.raises(ValueError) as e:
        tfwrapper.detect_stack(wrapper_config, parents_count)
    assert "environment cannot be autodetected" in str(e.value)

    os.chdir(paths["environment_dir"])
    wrapper_config = deepcopy(vars(default_args))
    parents_count = tfwrapper.detect_config_dir(wrapper_config)
    with pytest.raises(ValueError) as e:
        tfwrapper.detect_stack(wrapper_config, parents_count)
    assert "region cannot be autodetected" in str(e.value)

    os.chdir(paths["region_dir"])
    wrapper_config = deepcopy(vars(default_args))
    parents_count = tfwrapper.detect_config_dir(wrapper_config)
    with pytest.raises(ValueError) as e:
        tfwrapper.detect_stack(wrapper_config, parents_count)
    assert "stack cannot be autodetected" in str(e.value)

    os.chdir(paths["stack_dir"])
    wrapper_config = deepcopy(vars(default_args))
    parents_count = tfwrapper.detect_config_dir(wrapper_config)
    tfwrapper.detect_stack(wrapper_config, parents_count)
    assert wrapper_config["account"] == "testaccount"
    assert wrapper_config["environment"] == "testenvironment"
    assert wrapper_config["region"] == "testregion"
    assert wrapper_config["stack"] == "teststack"


def test_detect_stack_global(tmp_working_dir_global, default_args):
    paths = tmp_working_dir_global

    wrapper_config = deepcopy(vars(default_args))
    parents_count = tfwrapper.detect_config_dir(wrapper_config)
    with pytest.raises(ValueError) as e:
        tfwrapper.detect_stack(wrapper_config, parents_count)
    assert "account cannot be autodetected" in str(e.value)

    os.chdir(paths["account_dir"])
    wrapper_config = deepcopy(vars(default_args))
    parents_count = tfwrapper.detect_config_dir(wrapper_config)
    with pytest.raises(ValueError) as e:
        tfwrapper.detect_stack(wrapper_config, parents_count)
    assert "environment cannot be autodetected" in str(e.value)

    os.chdir(paths["environment_dir"])
    wrapper_config = deepcopy(vars(default_args))
    parents_count = tfwrapper.detect_config_dir(wrapper_config)
    with pytest.raises(ValueError) as e:
        tfwrapper.detect_stack(wrapper_config, parents_count)
    assert "stack cannot be autodetected" in str(e.value)

    os.chdir(paths["stack_dir"])
    wrapper_config = deepcopy(vars(default_args))
    parents_count = tfwrapper.detect_config_dir(wrapper_config)
    tfwrapper.detect_stack(wrapper_config, parents_count)
    assert wrapper_config["account"] == "testaccount"
    assert wrapper_config["environment"] == "global"
    assert wrapper_config["region"] is None
    assert wrapper_config["stack"] == "teststack"


def test_detect_stack_regional_no_error_if_missing(
    tmp_working_dir_regional, default_args
):
    paths = tmp_working_dir_regional

    wrapper_config = deepcopy(vars(default_args))
    parents_count = tfwrapper.detect_config_dir(wrapper_config)
    tfwrapper.detect_stack(wrapper_config, parents_count, raise_on_missing=False)
    assert wrapper_config["account"] is None
    assert wrapper_config["environment"] is None
    assert wrapper_config["region"] is None
    assert wrapper_config["stack"] is None

    os.chdir(paths["account_dir"])
    wrapper_config = deepcopy(vars(default_args))
    parents_count = tfwrapper.detect_config_dir(wrapper_config)
    tfwrapper.detect_stack(wrapper_config, parents_count, raise_on_missing=False)
    assert wrapper_config["account"] == "testaccount"
    assert wrapper_config["environment"] is None
    assert wrapper_config["region"] is None
    assert wrapper_config["stack"] is None

    os.chdir(paths["environment_dir"])
    wrapper_config = deepcopy(vars(default_args))
    parents_count = tfwrapper.detect_config_dir(wrapper_config)
    tfwrapper.detect_stack(wrapper_config, parents_count, raise_on_missing=False)
    assert wrapper_config["account"] == "testaccount"
    assert wrapper_config["environment"] == "testenvironment"
    assert wrapper_config["region"] is None
    assert wrapper_config["stack"] is None

    os.chdir(paths["region_dir"])
    wrapper_config = deepcopy(vars(default_args))
    parents_count = tfwrapper.detect_config_dir(wrapper_config)
    tfwrapper.detect_stack(wrapper_config, parents_count, raise_on_missing=False)
    assert wrapper_config["account"] == "testaccount"
    assert wrapper_config["environment"] == "testenvironment"
    assert wrapper_config["region"] == "testregion"
    assert wrapper_config["stack"] is None

    os.chdir(paths["stack_dir"])
    wrapper_config = deepcopy(vars(default_args))
    parents_count = tfwrapper.detect_config_dir(wrapper_config)
    tfwrapper.detect_stack(wrapper_config, parents_count, raise_on_missing=False)
    assert wrapper_config["account"] == "testaccount"
    assert wrapper_config["environment"] == "testenvironment"
    assert wrapper_config["region"] == "testregion"
    assert wrapper_config["stack"] == "teststack"


def test_detect_stack_global_no_error_if_missing(tmp_working_dir_global, default_args):
    paths = tmp_working_dir_global

    wrapper_config = deepcopy(vars(default_args))
    parents_count = tfwrapper.detect_config_dir(wrapper_config)
    tfwrapper.detect_stack(wrapper_config, parents_count, raise_on_missing=False)
    assert wrapper_config["account"] is None
    assert wrapper_config["environment"] is None
    assert wrapper_config["region"] is None
    assert wrapper_config["stack"] is None

    os.chdir(paths["account_dir"])
    wrapper_config = deepcopy(vars(default_args))
    parents_count = tfwrapper.detect_config_dir(wrapper_config)
    tfwrapper.detect_stack(wrapper_config, parents_count, raise_on_missing=False)
    assert wrapper_config["account"] == "testaccount"
    assert wrapper_config["environment"] is None
    assert wrapper_config["region"] is None
    assert wrapper_config["stack"] is None

    os.chdir(paths["environment_dir"])
    wrapper_config = deepcopy(vars(default_args))
    parents_count = tfwrapper.detect_config_dir(wrapper_config)
    tfwrapper.detect_stack(wrapper_config, parents_count, raise_on_missing=False)
    assert wrapper_config["account"] == "testaccount"
    assert wrapper_config["environment"] == "global"
    assert wrapper_config["region"] is None
    assert wrapper_config["stack"] is None

    os.chdir(paths["stack_dir"])
    wrapper_config = deepcopy(vars(default_args))
    parents_count = tfwrapper.detect_config_dir(wrapper_config)
    tfwrapper.detect_stack(wrapper_config, parents_count, raise_on_missing=False)
    assert wrapper_config["account"] == "testaccount"
    assert wrapper_config["environment"] == "global"
    assert wrapper_config["region"] is None
    assert wrapper_config["stack"] == "teststack"


def test_load_wrapper_config_confdir_empty(tmp_working_dir_regional, default_args):
    paths = tmp_working_dir_regional

    os.chdir(paths["stack_dir"])
    wrapper_config = deepcopy(vars(default_args))
    tfwrapper.detect_config_dir(wrapper_config)
    with pytest.raises(FileNotFoundError) as e:
        tfwrapper.load_wrapper_config(wrapper_config)
    assert "No such file or directory: '../../../../conf/state.yml" in str(e.value)

    paths["state_conf"].write_text("")
    wrapper_config = deepcopy(vars(default_args))
    tfwrapper.detect_config_dir(wrapper_config)
    with pytest.raises(AttributeError) as e:
        tfwrapper.load_wrapper_config(wrapper_config)
    assert "'NoneType' object has no attribute 'items'" in str(e.value)

    paths["state_conf"].write_text("#")  # Invalid
    wrapper_config = deepcopy(vars(default_args))
    tfwrapper.detect_config_dir(wrapper_config)
    with pytest.raises(AttributeError) as e:
        tfwrapper.load_wrapper_config(wrapper_config)
    assert "'NoneType' object has no attribute 'items'" in str(e.value)

    paths["state_conf"].write_text("{}")
    wrapper_config = deepcopy(vars(default_args))
    tfwrapper.detect_config_dir(wrapper_config)
    tfwrapper.load_wrapper_config(wrapper_config)
    assert wrapper_config["state"] == {}


def test_load_wrapper_config_autodetect_regional(
    tmp_working_dir_regional, default_args
):
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
