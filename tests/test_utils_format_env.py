"""Test utils: format_env."""

from claranet_tfwrapper.utils import format_env


def test_format_env_empty():  # noqa: D103
    assert format_env({}) == ""


def test_format_env_single():  # noqa: D103
    assert format_env({"VAR": "VALUE"}) == "VAR=VALUE"


def test_format_env_multiple():  # noqa: D103
    assert format_env({"VAR1": "VALUE1", "VAR2": "VALUE2"}) == "VAR1=VALUE1 VAR2=VALUE2"
