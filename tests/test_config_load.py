"""Test config is loaded depending on cmd line arguments."""

import os

import pytest

import claranet_tfwrapper as tfwrapper


def test_config_load_help():
    with pytest.raises(SystemExit) as e:
        tfwrapper.parse_args([])
    assert e.value.code == 0


def test_config_load_init_not_in_stack(tmp_working_dir_regional):
    with pytest.raises(SystemExit) as e:
        tfwrapper.main(["init"])

    assert e.type is SystemExit
    assert e.value.code == 1


def test_config_load_init_missing_config(tmp_working_dir_regional):
    paths = tmp_working_dir_regional
    os.chdir(paths["stack_dir"])

    with pytest.raises(SystemExit) as e:
        tfwrapper.main(["init"])

    assert e.type is SystemExit
    assert e.value.code == 1


def test_config_load_init_valid_config(tmp_working_dir_regional_valid):
    paths = tmp_working_dir_regional_valid
    os.chdir(paths["stack_dir"])

    with pytest.raises(SystemExit) as e:
        tfwrapper.main(["init"])

    assert e.type is SystemExit
    assert e.value.code == 0


def test_config_load_init_valid_legacy_config(tmp_working_dir_regional_valid_legacy):
    paths = tmp_working_dir_regional_valid_legacy
    os.chdir(paths["stack_dir"])

    with pytest.raises(SystemExit) as e:
        tfwrapper.main(["init"])

    assert e.type is SystemExit
    assert e.value.code == 0


def test_config_load_plan_not_in_stack(tmp_working_dir_regional):
    with pytest.raises(SystemExit) as e:
        tfwrapper.main(["plan"])

    assert e.type is SystemExit
    assert e.value.code == 1


def test_config_load_plan_missing_config(tmp_working_dir_regional):
    paths = tmp_working_dir_regional
    os.chdir(paths["stack_dir"])

    with pytest.raises(SystemExit) as e:
        tfwrapper.main(["plan"])

    assert e.type is SystemExit
    assert e.value.code == 1


def test_config_load_plan_valid_config(tmp_working_dir_regional_valid):
    paths = tmp_working_dir_regional_valid
    os.chdir(paths["stack_dir"])

    with pytest.raises(SystemExit) as e:
        tfwrapper.main(["plan"])

    assert e.type is SystemExit
    assert e.value.code == 0


def test_config_load_init_with_use_local_azure_session_directory_default(monkeypatch, tmp_working_dir_regional_valid):
    paths = tmp_working_dir_regional_valid
    os.chdir(paths["stack_dir"])

    with pytest.raises(SystemExit) as e:
        tfwrapper.main(["init"])
    assert e.type is SystemExit
    assert e.value.code == 0
