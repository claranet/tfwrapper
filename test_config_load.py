"""Test config is loaded depending on cmd line arguments."""

from importlib.machinery import SourceFileLoader

import pytest

tfwrapper = SourceFileLoader("tfwrapper", "bin/tfwrapper").load_module()


def test_config_load_help():  # noqa: D103
    with pytest.raises(SystemExit) as e:
        tfwrapper.parse_args([])
    assert e.value.code == 0


def test_config_load_switchver():  # noqa: D103
    with pytest.raises(SystemExit) as e:
        tfwrapper.main(["switchver"])
    assert e.value.code == 2


def test_config_load_init(capsys):  # noqa: D103
    with pytest.raises(FileNotFoundError) as e:
        tfwrapper.main(["init"])
    assert "No such file or directory" in str(e)


def test_config_load_plan(capsys):  # noqa: D103
    with pytest.raises(FileNotFoundError) as e:
        tfwrapper.main(["plan"])
    assert "No such file or directory" in str(e)
