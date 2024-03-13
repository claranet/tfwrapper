"""Test command line completion."""

import io
import os
import pytest

import claranet_tfwrapper as tfwrapper


def do_completion_test(monkeypatch, tmp_path, line, point=None):
    if point is None:
        point = len(line)

    # Trigger argcomplete and enable its debug logging
    monkeypatch.setenv("_ARGCOMPLETE", "1")
    monkeypatch.setenv("_ARC_DEBUG", "1")

    # Make argcomplete output completions to a file instead of file descriptor 8
    filename = str(tmp_path / "completions.txt")
    monkeypatch.setenv("_ARGCOMPLETE_STDOUT_FILENAME", filename)

    # Make argcomplete separate completions by a space
    monkeypatch.setenv("_ARGCOMPLETE_IFS", " ")

    # Define usual bash completion environment variables
    monkeypatch.setenv("COMP_LINE", line)
    monkeypatch.setenv("COMP_POINT", str(point))

    # Mock os.fdopen which is used by argcomplete to manipulate file descriptor 9
    monkeypatch.setattr(os, "fdopen", lambda fd, mode: fd == 9 and open(str(tmp_path / "debug.txt"), "w") or io.open(fd, mode))

    with pytest.raises(SystemExit) as e:
        tfwrapper.main([])

    assert e.value.code == 0

    with open(filename, "r") as f:
        return f.read()


def test_completion_no_args(monkeypatch, tmp_path):
    assert do_completion_test(
        monkeypatch,
        tmp_path,
        "tfwrapper ",
    ) == " ".join(
        [
            "-h",
            "--help",
            "-d",
            "--debug",
            "-V",
            "--version",
            "-c",
            "--confdir",
            "-a",
            "--account",
            "-e",
            "--environment",
            "-r",
            "--region",
            "-s",
            "--stack",
            "--http-cache-dir",
            "-p",
            "--plugin-cache-dir",
            "apply",
            "console",
            "destroy",
            "fmt",
            "force-unlock",
            "get",
            "graph",
            "import",
            "init",
            "output",
            "plan",
            "providers",
            "refresh",
            "show",
            "state",
            "taint",
            "untaint",
            "validate",
            "version",
            "workspace",
            "bootstrap",
            "foreach",
        ]
    )


def test_completion_arg_dash(monkeypatch, tmp_path):
    assert do_completion_test(
        monkeypatch,
        tmp_path,
        "tfwrapper -",
    ) == " ".join(
        [
            "-h",
            "--help",
            "-d",
            "--debug",
            "-V",
            "--version",
            "-c",
            "--confdir",
            "-a",
            "--account",
            "-e",
            "--environment",
            "-r",
            "--region",
            "-s",
            "--stack",
            "--http-cache-dir",
            "-p",
            "--plugin-cache-dir",
        ]
    )


def test_completion_arg_dash_d(monkeypatch, tmp_path):
    assert do_completion_test(
        monkeypatch,
        tmp_path,
        "tfwrapper -d",
    ) == " ".join(
        [
            "-d ",
        ]
    )


def test_completion_arg_work(monkeypatch, tmp_path):
    assert do_completion_test(
        monkeypatch,
        tmp_path,
        "tfwrapper work",
    ) == " ".join(
        [
            "workspace ",
        ]
    )


def test_completion_arg_workspace(monkeypatch, tmp_path):
    assert do_completion_test(
        monkeypatch,
        tmp_path,
        "tfwrapper workspace ",
    ) == " ".join(
        [
            "-h",
            "--help",
            "delete",
            "list",
            "new",
            "select",
            "show",
        ]
    )


def test_completion_arg_workspace_select(monkeypatch, tmp_path):
    assert do_completion_test(
        monkeypatch,
        tmp_path,
        "tfwrapper workspace select ",
    ) == " ".join(
        [
            "default ",
        ]
    )
