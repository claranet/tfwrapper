"""Test command line argument parsing."""

import re

import pytest

import claranet_tfwrapper as tfwrapper

from claranet_tfwrapper import HOME_DIR  # noqa: E402


def test_parse_args_help(capsys):
    with pytest.raises(SystemExit) as e:
        tfwrapper.parse_args([])
    assert e.value.code == 0
    captured = capsys.readouterr()
    assert "usage: tfwrapper [-h] [-d] [-V] [-c CONFDIR] [-a [ACCOUNT]]" in captured.err


def test_parse_args_no_args(capsys):
    with pytest.raises(SystemExit) as e:
        tfwrapper.parse_args([])
    assert e.value.code == 0
    captured = capsys.readouterr()
    assert "usage: tfwrapper [-h] [-d] [-V] [-c CONFDIR] [-a [ACCOUNT]]" in captured.err


def test_parse_args_init_help(capsys):
    with pytest.raises(SystemExit) as e:
        tfwrapper.parse_args(["init", "-h"])
    assert e.value.code == 0
    captured = capsys.readouterr()
    assert "usage: tfwrapper init [-h] [--backend {true,false}] ..." in captured.out


def test_parse_args_init_no_args():
    args = tfwrapper.parse_args(["init"])
    assert args.subcommand == "init"
    assert args.func == tfwrapper.terraform_init
    assert args.backend == "true"


def test_parse_args_init_backend_true():
    args = tfwrapper.parse_args(["init", "--backend", "true"])
    assert args.subcommand == "init"
    assert args.func == tfwrapper.terraform_init
    assert args.backend == "true"

    args = tfwrapper.parse_args(["init", "--backend=true"])
    assert args.subcommand == "init"
    assert args.func == tfwrapper.terraform_init
    assert args.backend == "true"


def test_parse_args_init_backend_false():
    args = tfwrapper.parse_args(["init", "--backend", "false"])
    assert args.subcommand == "init"
    assert args.func == tfwrapper.terraform_init
    assert args.backend == "false"

    args = tfwrapper.parse_args(["init", "--backend=false"])
    assert args.subcommand == "init"
    assert args.func == tfwrapper.terraform_init
    assert args.backend == "false"


def test_parse_args_foreach_help(capsys):
    with pytest.raises(SystemExit) as e:
        tfwrapper.parse_args(["foreach", "-h"])
    assert e.value.code == 0
    captured = capsys.readouterr()
    assert "usage: tfwrapper foreach [-h] [-S] ..." in captured.out


def test_parse_args_foreach_no_args():
    with pytest.raises(ValueError) as e:
        tfwrapper.parse_args(["foreach"])
    assert str(e.value) == "foreach: error: a command is required\n\nUse -h to show the help message"


def test_parse_args_foreach_shell_no_args():
    with pytest.raises(ValueError) as e:
        tfwrapper.parse_args(["foreach", "-S"])
    assert str(e.value) == "foreach: error: a command is required\n\nUse -h to show the help message"


def test_parse_args_foreach_shell_long_no_args():
    with pytest.raises(ValueError) as e:
        tfwrapper.parse_args(["foreach", "--shell"])
    assert str(e.value) == "foreach: error: a command is required\n\nUse -h to show the help message"


def test_parse_args_foreach_command_shell_too_many_args():
    with pytest.raises(ValueError) as e:
        tfwrapper.parse_args(["foreach", "-S", "ls", "-l"])
    assert (
        str(e.value) == "foreach: error: -S/--shell must be followed by a single argument (hint: use quotes)\n\n"
        "Use -h to show the help message"
    )


def test_parse_args_foreach_command(monkeypatch):
    monkeypatch.setenv("SHELL", "mybash")
    args = tfwrapper.parse_args(["foreach", "--", "ls", "-l"])
    assert args.subcommand == "foreach"
    assert args.func == tfwrapper.foreach
    assert args.shell is False
    assert args.executable is None
    assert args.command == ["ls", "-l"]


def test_parse_args_foreach_command_shell(monkeypatch):
    monkeypatch.setenv("SHELL", "mybash")
    args = tfwrapper.parse_args(["foreach", "-S", "ls -l | head -1"])
    assert args.subcommand == "foreach"
    assert args.func == tfwrapper.foreach
    assert args.shell is True
    assert args.executable == "mybash"
    assert args.command == ["ls -l | head -1"]


def test_parse_args_foreach_command_shell_long(monkeypatch):
    monkeypatch.setenv("SHELL", "mybash")
    args = tfwrapper.parse_args(["foreach", "--shell", "ls -l | head -1"])
    assert args.subcommand == "foreach"
    assert args.func == tfwrapper.foreach
    assert args.shell is True
    assert args.executable == "mybash"
    assert args.command == ["ls -l | head -1"]


def test_parse_args_http_cache_dir():
    args = tfwrapper.parse_args(["--http-cache-dir", ".webcache", "init"])
    assert args.subcommand == "init"
    assert args.func == tfwrapper.terraform_init
    assert args.http_cache_dir == ".webcache"


def test_parse_args_init_plugin_cache_dir_default(monkeypatch):
    monkeypatch.delenv("TF_PLUGIN_CACHE_DIR", raising=False)
    args = tfwrapper.parse_args(["init"])
    assert args.subcommand == "init"
    assert args.func == tfwrapper.terraform_init
    assert args.plugin_cache_dir == "{}/.terraform.d/plugin-cache".format(HOME_DIR)


def test_parse_args_init_plugin_cache_dir_arg(monkeypatch):
    monkeypatch.delenv("TF_PLUGIN_CACHE_DIR", raising=False)
    args = tfwrapper.parse_args(["--plugin-cache-dir=/tmp/plugin-cache-dir", "init"])
    assert args.subcommand == "init"
    assert args.func == tfwrapper.terraform_init
    assert args.plugin_cache_dir == "/tmp/plugin-cache-dir"


def test_parse_args_init_plugin_cache_dir_env(monkeypatch):
    monkeypatch.setenv("TF_PLUGIN_CACHE_DIR", "/tmp/plugin-cache-dir")
    args = tfwrapper.parse_args(["init"])
    assert args.subcommand == "init"
    assert args.func == tfwrapper.terraform_init
    assert args.plugin_cache_dir == "/tmp/plugin-cache-dir"


def test_parse_args_init_plugin_cache_dir_arg_and_env(monkeypatch):
    monkeypatch.setenv("TF_PLUGIN_CACHE_DIR", "/tmp/plugin-cache-dir")
    args = tfwrapper.parse_args(["--plugin-cache-dir=/tmp/plugin-cache-dir-arg", "init"])
    assert args.subcommand == "init"
    assert args.func == tfwrapper.terraform_init
    assert args.plugin_cache_dir == "/tmp/plugin-cache-dir-arg"


def test_parse_args_version(capsys):
    with pytest.raises(SystemExit) as e:
        tfwrapper.parse_args(["-V"])
    assert e.value.code == 0
    captured = capsys.readouterr()
    assert re.match(r"^tfwrapper v\d+\.\d+\.\d+", captured.err)
