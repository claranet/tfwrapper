"""Test config is loaded depending on cmd line arguments."""


import os
import textwrap

import pytest

import claranet_tfwrapper as tfwrapper


@pytest.fixture
def tmp_working_dir_regional_valid(tmp_working_dir_regional):  # noqa: D103
    paths = tmp_working_dir_regional

    paths["state_conf"].write_text("---")
    paths["stack_conf"] = paths["conf_dir"] / "testaccount_testenvironment_testregion_teststack.yml"
    paths["stack_conf"].write_text(
        textwrap.dedent(
            """
            ---
            terraform:
              vars:
                myvar: myvalue
                version: "1.0.3"
            """
        )
    )
    paths["terraform_conf"] = paths["stack_dir"] / "test.tf"
    paths["terraform_conf"].write_text(
        textwrap.dedent(
            """
            # Empty terraform configuration
            """
        )
    )

    return paths


def test_config_load_help():  # noqa: D103
    with pytest.raises(SystemExit) as e:
        tfwrapper.parse_args([])
    assert e.value.code == 0


def test_config_load_init_missing_config(tmp_working_dir_regional):  # noqa: D103
    paths = tmp_working_dir_regional
    os.chdir(paths["stack_dir"])

    with pytest.raises(FileNotFoundError) as e:
        tfwrapper.main(["init"])

    assert "No such file or directory" in str(e)


def test_config_load_init_valid_config(tmp_working_dir_regional_valid):  # noqa: D103
    paths = tmp_working_dir_regional_valid
    os.chdir(paths["stack_dir"])

    with pytest.raises(SystemExit) as e:
        tfwrapper.main(["init"])

    assert e.type == SystemExit
    assert e.value.code == 0


def test_config_load_plan_missing_config(tmp_working_dir_regional):  # noqa: D103
    paths = tmp_working_dir_regional
    os.chdir(paths["stack_dir"])

    with pytest.raises(FileNotFoundError) as e:
        tfwrapper.main(["plan"])

    assert "No such file or directory" in str(e)


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
    monkeypatch.delenv("AZURE_ACCESS_TOKEN_FILE", raising=False)

    with pytest.raises(SystemExit) as e:
        tfwrapper.main(["init"])
    assert e.type == SystemExit
    assert e.value.code == 0

    assert os.environ.get("AZURE_CONFIG_DIR").endswith("/a/b/c/d/e/.run/azure")
    assert os.environ.get("AZURE_ACCESS_TOKEN_FILE").endswith("/a/b/c/d/e/.run/azure/accessTokens.json")


def test_config_load_init_with_use_local_azure_session_directory_true(monkeypatch, tmp_working_dir_regional_valid):  # noqa: D103
    paths = tmp_working_dir_regional_valid
    os.chdir(paths["stack_dir"])

    # Ensure those environment variables are not set
    monkeypatch.delenv("AZURE_CONFIG_DIR", raising=False)
    monkeypatch.delenv("AZURE_ACCESS_TOKEN_FILE", raising=False)

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
    assert os.environ.get("AZURE_ACCESS_TOKEN_FILE").endswith("/a/b/c/d/e/.run/azure/accessTokens.json")


def test_config_load_init_with_use_local_azure_session_directory_false(monkeypatch, tmp_working_dir_regional_valid):  # noqa: D103
    paths = tmp_working_dir_regional_valid
    os.chdir(paths["stack_dir"])

    # Ensure those environment variables are not set
    monkeypatch.delenv("AZURE_CONFIG_DIR", raising=False)
    monkeypatch.delenv("AZURE_ACCESS_TOKEN_FILE", raising=False)

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
    assert os.environ.get("AZURE_ACCESS_TOKEN_FILE") is None
