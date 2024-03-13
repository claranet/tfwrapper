"""Test some helper functions."""

import claranet_tfwrapper as tfwrapper


def test_get_stack_dir(tmp_working_dir):
    working_dir = tmp_working_dir["working_dir"]
    for account, environment, region, stack, expected in [
        (
            "testaccount",
            "global",
            None,
            "teststack",
            working_dir / "testaccount/_global/teststack",
        ),
        (
            "testaccount",
            "testenvironment",
            "testregion",
            "teststack",
            working_dir / "testaccount/testenvironment/testregion/teststack",
        ),
    ]:
        assert tfwrapper.get_stack_dir(working_dir, account, environment, region, stack) == str(expected)


def test_get_stack_config_filename():
    for account, environment, region, stack, expected in [
        (
            "*",
            "global",
            None,
            "*",
            "*_global_*.yml",
        ),
        (
            "*",
            "*",
            "*",
            "*",
            "*_*_*_*.yml",
        ),
        (
            "testaccount",
            "global",
            None,
            "teststack",
            "testaccount_global_teststack.yml",
        ),
        (
            "testaccount",
            "testenvironment",
            "testregion",
            "teststack",
            "testaccount_testenvironment_testregion_teststack.yml",
        ),
    ]:
        assert tfwrapper.get_stack_config_filename(account, environment, region, stack) == str(expected)


def test_get_stack_config_path(tmp_working_dir_empty_conf):
    conf_dir = tmp_working_dir_empty_conf["conf_dir"]
    for account, environment, region, stack, expected in [
        (
            "testaccount",
            "global",
            None,
            "teststack",
            conf_dir / "testaccount_global_teststack.yml",
        ),
        (
            "testaccount",
            "testenvironment",
            "testregion",
            "teststack",
            conf_dir / "testaccount_testenvironment_testregion_teststack.yml",
        ),
    ]:
        assert tfwrapper.get_stack_config_path(conf_dir, account, environment, region, stack) == str(expected)


def test_get_stack_from_config_path(tmp_working_dir_empty_conf):
    conf_dir = tmp_working_dir_empty_conf["conf_dir"]
    for config_path, expected in [
        (
            conf_dir / "testaccount_global_teststack.yml",
            ("testaccount", "global", None, "teststack"),
        ),
        (
            conf_dir / "testaccount_testenvironment_testregion_teststack.yml",
            ("testaccount", "testenvironment", "testregion", "teststack"),
        ),
        (
            "conf/testaccount_global_teststack.yml",
            ("testaccount", "global", None, "teststack"),
        ),
        (
            "conf/testaccount_testenvironment_testregion_teststack.yml",
            ("testaccount", "testenvironment", "testregion", "teststack"),
        ),
    ]:
        assert tfwrapper.get_stack_from_config_path(str(config_path)) == expected
