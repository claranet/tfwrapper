"""Test terraform commands behavior."""

import os

import pytest

import claranet_tfwrapper as tfwrapper


def test_terraform_1_0_0_commands(tmp_working_dir_regional_valid):  # noqa: D103
    for command in [
        ["apply", "--unsafe"],
        ["console"],
        ["destroy"],
        ["fmt"],
        # ["force-unlock"], # Commented out as it requires valid input
        ["get"],
        ["graph"],
        # ["import"], # Commented out as it requires valid input
        ["init"],
        ["output"],
        ["plan"],
        ["providers"],
        ["refresh"],
        ["show"],
        ["state", "list"],
        # ["taint"], # Commented out as it requires valid input
        # ["untaint"], # Commented out as it requires valid input
        ["validate"],
        ["version"],
        ["workspace", "list"],
    ]:
        print(f"Testing terraform command: {command}")
        paths = tmp_working_dir_regional_valid
        os.chdir(paths["stack_dir"])

        with pytest.raises(SystemExit) as e:
            tfwrapper.main(command)

        assert e.type == SystemExit
        assert e.value.code == 0


def test_terraform_invalid_command(tmp_working_dir_regional_valid):  # noqa: D103
    paths = tmp_working_dir_regional_valid
    os.chdir(paths["stack_dir"])

    with pytest.raises(SystemExit) as e:
        tfwrapper.main(["some_invalid_command"])

    assert e.type == SystemExit
    assert e.value.code == 2
