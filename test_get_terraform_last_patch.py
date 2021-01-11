"""Test hashicorp terraform last patch searching."""

from importlib.machinery import SourceFileLoader

import os
import pytest

tfwrapper = SourceFileLoader("tfwrapper", "bin/tfwrapper").load_module()

releases_url = "https://releases.hashicorp.com/terraform/index.json"
patch_regex = r"[0-9]+(((-alpha|-beta|-rc)[0-9]+)|(?P<dev>-dev))?"


@pytest.fixture
def terraform_versions_json():  # noqa: D103
    with open(os.path.join(os.path.dirname(__file__), "test_terraform_versions.json")) as f:
        return f.read()


@pytest.fixture
def terraform_versions_json_error():  # noqa: D103
    return """
{"name":"terraform","versions":""}
"""


def test_get_terraform_last_patch(
    requests_mock,
    terraform_versions_json,
):  # noqa: D103
    requests_mock.get(
        releases_url,
        complete_qs=True,
        text=terraform_versions_json,
    )

    patch = tfwrapper.get_terraform_last_patch("0.14", patch_regex)
    assert patch == "4"

    patch = tfwrapper.get_terraform_last_patch("0.13", patch_regex)
    assert patch == "6"

    patch = tfwrapper.get_terraform_last_patch("0.12", patch_regex)
    assert patch == "30"

    patch = tfwrapper.get_terraform_last_patch("0.11", patch_regex)
    assert patch == "14"

    patch = tfwrapper.get_terraform_last_patch("0.10", patch_regex)
    assert patch == "8"

    patch = tfwrapper.get_terraform_last_patch("0.9", patch_regex)
    assert patch == "11"

    patch = tfwrapper.get_terraform_last_patch("0.8", patch_regex)
    assert patch == "8"

    patch = tfwrapper.get_terraform_last_patch("0.7", patch_regex)
    assert patch == "13"

    patch = tfwrapper.get_terraform_last_patch("0.6", patch_regex)
    assert patch == "16"

    patch = tfwrapper.get_terraform_last_patch("0.5", patch_regex)
    assert patch == "3"

    with pytest.raises(ValueError) as e:
        tfwrapper.get_terraform_last_patch("0.666", patch_regex)
    assert "The terraform minor version 0.666 does not exist" in str(e)


def test_get_terraform_last_patch_error(
    requests_mock,
    terraform_versions_json_error,
):  # noqa: D103
    requests_mock.get(
        releases_url,
        complete_qs=True,
        text=terraform_versions_json_error,
    )

    patch = tfwrapper.get_terraform_last_patch("0.12", patch_regex)
    assert patch is None
