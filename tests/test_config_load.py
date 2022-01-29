"""Test config is loaded depending on cmd line arguments."""


import os
import textwrap

import pytest

import claranet_tfwrapper as tfwrapper


def test_config_load_help():  # noqa: D103
    with pytest.raises(SystemExit) as e:
        tfwrapper.parse_args([])
    assert e.value.code == 0


def test_config_load_init_not_in_stack(tmp_working_dir_regional):  # noqa: D103
    with pytest.raises(SystemExit) as e:
        tfwrapper.main(["init"])

    assert e.type == SystemExit
    assert e.value.code == 0


def test_config_load_init_missing_config(tmp_working_dir_regional):  # noqa: D103
    paths = tmp_working_dir_regional
    os.chdir(paths["stack_dir"])

    with pytest.raises(SystemExit) as e:
        tfwrapper.main(["init"])

    assert e.type == SystemExit
    assert e.value.code == 0


def test_config_load_init_valid_config(tmp_working_dir_regional_valid):  # noqa: D103
    paths = tmp_working_dir_regional_valid
    os.chdir(paths["stack_dir"])

    with pytest.raises(SystemExit) as e:
        tfwrapper.main(["init"])

    assert e.type == SystemExit
    assert e.value.code == 0


def test_config_load_plan_not_in_stack(tmp_working_dir_regional):  # noqa: D103
    with pytest.raises(SystemExit) as e:
        tfwrapper.main(["plan"])

    assert e.type == SystemExit
    assert e.value.code == 1


def test_config_load_plan_missing_config(tmp_working_dir_regional):  # noqa: D103
    paths = tmp_working_dir_regional
    os.chdir(paths["stack_dir"])

    with pytest.raises(SystemExit) as e:
        tfwrapper.main(["plan"])

    assert e.type == SystemExit
    assert e.value.code == 1


def test_config_load_plan_valid_config(tmp_working_dir_regional_valid):  # noqa: D103
    paths = tmp_working_dir_regional_valid
    os.chdir(paths["stack_dir"])

    with pytest.raises(SystemExit) as e:
        tfwrapper.main(["plan"])

    assert e.type == SystemExit
    assert e.value.code == 0


def test_config_load_init_with_use_local_azure_session_directory_default(  # noqa: D103
    monkeypatch, tmp_working_dir_regional_valid
):
    paths = tmp_working_dir_regional_valid
    os.chdir(paths["stack_dir"])

    # Ensure those environment variables are not set
    monkeypatch.delenv("AZURE_CONFIG_DIR", raising=False)

    with pytest.raises(SystemExit) as e:
        tfwrapper.main(["init"])
    assert e.type == SystemExit
    assert e.value.code == 0

    assert os.environ.get("AZURE_CONFIG_DIR").endswith("/a/b/c/d/e/.run/azure")


def test_config_load_init_with_use_local_azure_session_directory_true(monkeypatch, tmp_working_dir_regional_valid):  # noqa: D103
    paths = tmp_working_dir_regional_valid
    os.chdir(paths["stack_dir"])

    # Ensure those environment variables are not set
    monkeypatch.delenv("AZURE_CONFIG_DIR", raising=False)

    paths["wrapper_conf"].write_text(
        textwrap.dedent(
            """
            use_local_azure_session_directory: true
            """
        )
    )

    with pytest.raises(SystemExit) as e:
        tfwrapper.main(["init"])
    assert e.type == SystemExit
    assert e.value.code == 0

    assert os.environ.get("AZURE_CONFIG_DIR").endswith("/a/b/c/d/e/.run/azure")


def test_config_load_init_with_use_local_azure_session_directory_false(monkeypatch, tmp_working_dir_regional_valid):  # noqa: D103
    paths = tmp_working_dir_regional_valid
    os.chdir(paths["stack_dir"])

    # Ensure those environment variables are not set
    monkeypatch.delenv("AZURE_CONFIG_DIR", raising=False)

    paths["wrapper_conf"].write_text(
        textwrap.dedent(
            """
            use_local_azure_session_directory: false
            """
        )
    )

    with pytest.raises(SystemExit) as e:
        tfwrapper.main(["init"])
    assert e.type == SystemExit
    assert e.value.code == 0

    assert os.environ.get("AZURE_CONFIG_DIR") is None
