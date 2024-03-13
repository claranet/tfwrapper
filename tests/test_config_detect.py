"""Test stack configuration is detected based on working directory."""

from copy import deepcopy

import os

import pytest

import claranet_tfwrapper as tfwrapper


def test_detect_config_dir_confdir_not_found(tmp_working_dir, default_args):
    wrapper_config = deepcopy(vars(default_args))

    parents_count = tfwrapper.detect_config_dir(wrapper_config)
    assert parents_count == 0


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


def test_detect_stack_regional_no_error_if_missing(tmp_working_dir_regional, default_args):
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
