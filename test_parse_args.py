from importlib.machinery import SourceFileLoader

import os

import pytest

tfwrapper = SourceFileLoader("tfwrapper", "bin/tfwrapper").load_module()


def test_parse_args_help(capsys):
    with pytest.raises(SystemExit) as e:
        tfwrapper.parse_args([])
    assert e.value.code == 0
    captured = capsys.readouterr()
    assert "usage: tfwrapper [-h] [-d] [-c CONFDIR] [-a [ACCOUNT]]" in captured.err


def test_parse_args_no_args(capsys):
    with pytest.raises(SystemExit) as e:
        tfwrapper.parse_args([])
    assert e.value.code == 0
    captured = capsys.readouterr()
    assert "usage: tfwrapper [-h] [-d] [-c CONFDIR] [-a [ACCOUNT]]" in captured.err


def test_parse_args_foreach_help(capsys):
    with pytest.raises(SystemExit) as e:
        tfwrapper.parse_args(["foreach", "-h"])
    assert e.value.code == 0
    captured = capsys.readouterr()
    assert "usage: tfwrapper foreach [-h] [-c] ..." in captured.out


def test_parse_args_foreach_no_args():
    with pytest.raises(ValueError) as e:
        tfwrapper.parse_args(["foreach"])
    assert str(e.value) == "foreach: error: a command is required"


def test_parse_args_foreach_shell_no_args():
    with pytest.raises(ValueError) as e:
        tfwrapper.parse_args(["foreach", "-c"])
    assert str(e.value) == "foreach: error: a command is required"


def test_parse_args_foreach_command_shell_too_many_args():
    with pytest.raises(ValueError) as e:
        tfwrapper.parse_args(["foreach", "-c", "ls", "-l"])
    assert (
        str(e.value)
        == "foreach: error: -c must be followed by a single argument (hint: use quotes)"
    )


def test_parse_args_foreach_command():
    os.environ["SHELL"] = "mybash"
    args = tfwrapper.parse_args(["foreach", "--", "ls", "-l"])
    assert args.subcommand == "foreach"
    assert args.func == tfwrapper.foreach
    assert args.shell is False
    assert args.executable is None
    assert args.command == ["ls", "-l"]


def test_parse_args_foreach_command_shell():
    os.environ["SHELL"] = "mybash"
    args = tfwrapper.parse_args(["foreach", "-c", "ls -l | head -1"])
    assert args.subcommand == "foreach"
    assert args.func == tfwrapper.foreach
    assert args.shell is True
    assert args.executable == "mybash"
    assert args.command == ["ls -l | head -1"]
