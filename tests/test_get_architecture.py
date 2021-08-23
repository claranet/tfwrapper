"""Test terraform binary architecture mapping."""

from unittest.mock import MagicMock

import platform

import tfwrapper


def test_get_architecture_arm():  # noqa: D103
    platform.machine = MagicMock(return_value="arm")

    assert tfwrapper.get_architecture() == "arm"


def test_get_architecture_aarch():  # noqa: D103
    platform.machine = MagicMock(return_value="aarch")

    assert tfwrapper.get_architecture() == "arm"


def test_get_architecture_arm64():  # noqa: D103
    platform.machine = MagicMock(return_value="arm64")

    assert tfwrapper.get_architecture() == "arm64"


def test_get_architecture_aarch64():  # noqa: D103
    platform.machine = MagicMock(return_value="aarch64")

    assert tfwrapper.get_architecture() == "arm64"


def test_get_architecture_x86_64():  # noqa: D103
    platform.machine = MagicMock(return_value="x86_64")

    assert tfwrapper.get_architecture() == "amd64"


def test_get_architecture_amd64():  # noqa: D103
    platform.machine = MagicMock(return_value="amd64")

    assert tfwrapper.get_architecture() == "amd64"


def test_get_architecture_386():  # noqa: D103
    platform.machine = MagicMock(return_value="386")

    assert tfwrapper.get_architecture() == "386"


def test_get_architecture_i386():  # noqa: D103
    platform.machine = MagicMock(return_value="i386")

    assert tfwrapper.get_architecture() == "386"


def test_get_architecture_default():  # noqa: D103
    platform.machine = MagicMock(return_value="dummy")

    assert tfwrapper.get_architecture() == "386"
