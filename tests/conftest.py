"""Provide fixtures to all test_*.py files."""

import argparse
import os
import textwrap

import pytest

from unittest import mock


import claranet_tfwrapper as tfwrapper


@pytest.fixture(autouse=True)
def mock_environment_variables():
    # ensure external environment variables do not infer with tests,
    # and that the ones that are set by tfwrapper are cleared between tests
    path = os.environ["PATH"]
    with mock.patch.dict(os.environ, {"PATH": path}, clear=True):
        yield


@pytest.fixture
def default_args():
    parser = argparse.ArgumentParser()
    args = parser.parse_args([])
    args.confdir = "conf"
    args.account = None
    args.environment = None
    args.region = None
    args.stack = None
    return args


@pytest.fixture
def tmp_working_dir(tmp_path):
    # alter default HTTP cache dir to ensure all tests have their own empty cache
    tfwrapper.DEFAULT_HTTP_CACHE_DIR = str(tmp_path / ".terraform.d/http-cache")
    tfwrapper.CachedRequestsSession.set_cache_dir(tfwrapper.DEFAULT_HTTP_CACHE_DIR)

    # use path with more than 5 directories to avoid getting an unrelated conf dir outside tmp_path
    working_dir = tmp_path / "a" / "b" / "c" / "d" / "e"
    working_dir.mkdir(parents=True)
    os.chdir(working_dir)
    os.mkdir(".run")
    return {
        "working_dir": working_dir,
    }


@pytest.fixture
def tmp_working_dir_empty_conf(tmp_working_dir, default_args):
    paths = tmp_working_dir
    paths["conf_dir"] = paths["working_dir"] / default_args.confdir
    paths["conf_dir"].mkdir()
    paths["state_conf"] = paths["conf_dir"] / "state.yml"
    paths["wrapper_conf"] = paths["conf_dir"] / "config.yml"

    return paths


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


@pytest.fixture
def tmp_working_dir_regional_valid(tmp_working_dir_regional):
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
                version: "1.6.0"
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


@pytest.fixture
def tmp_working_dir_regional_valid_legacy(tmp_working_dir_regional):
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
                version: "1.1.4"
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
