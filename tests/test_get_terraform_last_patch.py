"""Test hashicorp terraform last patch searching."""

import os
import pytest

import claranet_tfwrapper as tfwrapper


@pytest.fixture
def terraform_versions_json():
    with open(os.path.join(os.path.dirname(__file__), "test_terraform_versions.json")) as f:
        return f.read()


@pytest.fixture
def terraform_versions_json_error():
    return """
{"name":"terraform","versions":""}
"""


def test_get_terraform_last_patch(
    requests_mock,
    terraform_versions_json,
):
    requests_mock.get(
        tfwrapper.TERRAFORM_RELEASES_URL,
        complete_qs=True,
        text=terraform_versions_json,
    )

    patch = tfwrapper.get_terraform_last_patch("0.15")
    assert patch == "0"

    patch = tfwrapper.get_terraform_last_patch("0.14")
    assert patch == "10"

    patch = tfwrapper.get_terraform_last_patch("0.13")
    assert patch == "6"

    patch = tfwrapper.get_terraform_last_patch("0.12")
    assert patch == "30"

    patch = tfwrapper.get_terraform_last_patch("0.11")
    assert patch == "14"

    patch = tfwrapper.get_terraform_last_patch("0.10")
    assert patch == "8"

    patch = tfwrapper.get_terraform_last_patch("0.9")
    assert patch == "11"

    patch = tfwrapper.get_terraform_last_patch("0.8")
    assert patch == "8"

    patch = tfwrapper.get_terraform_last_patch("0.7")
    assert patch == "13"

    patch = tfwrapper.get_terraform_last_patch("0.6")
    assert patch == "16"

    patch = tfwrapper.get_terraform_last_patch("0.5")
    assert patch == "3"

    with pytest.raises(ValueError) as e:
        tfwrapper.get_terraform_last_patch("0.666")
    assert "The terraform minor version 0.666 does not exist" in str(e)


def test_get_terraform_last_patch_error(
    requests_mock,
    terraform_versions_json_error,
):
    requests_mock.get(
        tfwrapper.TERRAFORM_RELEASES_URL,
        complete_qs=True,
        text=terraform_versions_json_error,
    )

    patch = tfwrapper.get_terraform_last_patch("0.12")
    assert patch is None
