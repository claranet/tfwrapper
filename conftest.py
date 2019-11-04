import argparse
import os

import pytest


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
    # use path with more than 5 directories to avoid getting an unrelated conf dir outside tmp_path
    working_dir = tmp_path / "a" / "b" / "c" / "d" / "e"
    working_dir.mkdir(parents=True)
    os.chdir(working_dir)
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
