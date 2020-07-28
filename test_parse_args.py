"""Test command line argument parsing."""

from importlib.machinery import SourceFileLoader

import os

import pytest

tfwrapper = SourceFileLoader("tfwrapper", "bin/tfwrapper").load_module()

from tfwrapper import home_dir  # noqa: E402


def test_parse_args_help(capsys):  # noqa: D103
    with pytest.raises(SystemExit) as e:
        tfwrapper.parse_args([])
    assert e.value.code == 0
    captured = capsys.readouterr()
    assert "usage: tfwrapper [-h] [-d] [-c CONFDIR] [-a [ACCOUNT]]" in captured.err


def test_parse_args_no_args(capsys):  # noqa: D103
    with pytest.raises(SystemExit) as e:
        tfwrapper.parse_args([])
    assert e.value.code == 0
    captured = capsys.readouterr()
    assert "usage: tfwrapper [-h] [-d] [-c CONFDIR] [-a [ACCOUNT]]" in captured.err


def test_parse_args_switchver_help(capsys):  # noqa: D103
    with pytest.raises(SystemExit) as e:
        tfwrapper.parse_args(["switchver", "-h"])
    assert e.value.code == 0
    captured = capsys.readouterr()
    assert "usage: tfwrapper switchver [-h] version" in captured.out


def test_parse_args_foreach_help(capsys):  # noqa: D103
    with pytest.raises(SystemExit) as e:
        tfwrapper.parse_args(["foreach", "-h"])
    assert e.value.code == 0
    captured = capsys.readouterr()
    assert "usage: tfwrapper foreach [-h] [-c] ..." in captured.out


def test_parse_args_foreach_no_args():  # noqa: D103
    with pytest.raises(ValueError) as e:
        tfwrapper.parse_args(["foreach"])
    assert str(e.value) == "foreach: error: a command is required"


def test_parse_args_foreach_shell_no_args():  # noqa: D103
    with pytest.raises(ValueError) as e:
        tfwrapper.parse_args(["foreach", "-c"])
    assert str(e.value) == "foreach: error: a command is required"


def test_parse_args_foreach_command_shell_too_many_args():  # noqa: D103
    with pytest.raises(ValueError) as e:
        tfwrapper.parse_args(["foreach", "-c", "ls", "-l"])
    assert str(e.value) == "foreach: error: -c must be followed by a single argument (hint: use quotes)"


def test_parse_args_foreach_command():  # noqa: D103
    os.environ["SHELL"] = "mybash"
    args = tfwrapper.parse_args(["foreach", "--", "ls", "-l"])
    assert args.subcommand == "foreach"
    assert args.func == tfwrapper.foreach
    assert args.shell is False
    assert args.executable is None
    assert args.command == ["ls", "-l"]


def test_parse_args_foreach_command_shell():  # noqa: D103
    os.environ["SHELL"] = "mybash"
    args = tfwrapper.parse_args(["foreach", "-c", "ls -l | head -1"])
    assert args.subcommand == "foreach"
    assert args.func == tfwrapper.foreach
    assert args.shell is True
    assert args.executable == "mybash"
    assert args.command == ["ls -l | head -1"]


def test_parse_args_http_cache_dir():  # noqa: D103
    args = tfwrapper.parse_args(["--http-cache-dir", ".webcache", "init"])
    assert args.subcommand == "init"
    assert args.func == tfwrapper.terraform_init
    assert args.http_cache_dir == ".webcache"


def test_parse_args_init_plugin_cache_dir_default():  # noqa: D103
    os.environ.pop("TF_PLUGIN_CACHE_DIR", None)
    args = tfwrapper.parse_args(["init"])
    assert args.subcommand == "init"
    assert args.func == tfwrapper.terraform_init
    assert args.plugin_cache_dir == "{}/.terraform.d/plugin-cache".format(home_dir)


def test_parse_args_init_plugin_cache_dir_arg():  # noqa: D103
    os.environ.pop("TF_PLUGIN_CACHE_DIR", None)
    args = tfwrapper.parse_args(["--plugin-cache-dir=/tmp/plugin-cache-dir", "init"])
    assert args.subcommand == "init"
    assert args.func == tfwrapper.terraform_init
    assert args.plugin_cache_dir == "/tmp/plugin-cache-dir"


def test_parse_args_init_plugin_cache_dir_env():  # noqa: D103
    os.environ["TF_PLUGIN_CACHE_DIR"] = "/tmp/plugin-cache-dir"
    args = tfwrapper.parse_args(["init"])
    assert args.subcommand == "init"
    assert args.func == tfwrapper.terraform_init
    assert args.plugin_cache_dir == "/tmp/plugin-cache-dir"


def test_parse_args_init_plugin_cache_dir_arg_and_env():  # noqa: D103
    os.environ["TF_PLUGIN_CACHE_DIR"] = "/tmp/plugin-cache-dir-env"
    args = tfwrapper.parse_args(["--plugin-cache-dir=/tmp/plugin-cache-dir-arg", "init"])
    assert args.subcommand == "init"
    assert args.func == tfwrapper.terraform_init
    assert args.plugin_cache_dir == "/tmp/plugin-cache-dir-arg"
