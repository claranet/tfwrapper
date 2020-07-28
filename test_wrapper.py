"""First unit tests."""

from importlib.machinery import SourceFileLoader
from unittest.mock import MagicMock

import platform

tfwrapper = SourceFileLoader("tfwrapper", "bin/tfwrapper").load_module()


def test_get_architecture_arm():  # noqa: D103
    platform.machine = MagicMock(return_value="arm")

    assert tfwrapper.get_architecture() == "arm"


def test_get_architecture_darwin():  # noqa: D103
    platform.machine = MagicMock(return_value="darwin")

    assert tfwrapper.get_architecture() == "amd64"


def test_get_architecture_x86_64():  # noqa: D103
    platform.machine = MagicMock(return_value="x86_64")

    assert tfwrapper.get_architecture() == "amd64"


def test_get_architecture_default():  # noqa: D103
    platform.machine = MagicMock(return_value="dummy")

    assert tfwrapper.get_architecture() == "386"
