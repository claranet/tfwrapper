"""Test custom providers configuration parsing."""

from importlib.machinery import SourceFileLoader

import pytest
import textwrap

tfwrapper = SourceFileLoader("tfwrapper", "bin/tfwrapper").load_module()


# Not used yet: this method will be used by the mock to replace requests.get
def mocked_requests_get(*args, **kwargs):  # noqa: D103
    from tfwrapper import GITHUB_RELEASES

    class MockResponse:
        def __init__(self, text, status_code):
            self.text = text
            self.status_code = status_code

        def text(self):
            return self.text

        def iter_content(self, chunk_size):
            # smallest valid zip file
            return [
                b"PK\x05\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00",
                b"\x00\x00",
            ]

    if args[0] == "https://github.com/claranet/terraform-provider-test":
        return MockResponse({}, 200)
    elif (
        args[0]
        == GITHUB_RELEASES.format("claranet/terraform-provider-test")
        + "/download/v2.2.0/claranet_terraform_provider_test_linux_amd64.zip"
    ):
        return MockResponse("", 200)

    return MockResponse("", 404)


def test_stack_config_parsing(tmp_working_dir_empty_conf):  # noqa: D103
    paths = tmp_working_dir_empty_conf
    stack_config = paths["conf_dir"] / "testaccount_testenvironment_testregion_teststack.yml"

    stack_config.write_text(
        textwrap.dedent(
            """
            ---
            terraform:
                vars:
                    client_name: claranet
                    version: 0.11.14
                custom-providers:
                    claranet/terraform-provider-gitlab: '2.1'
            """
        )
    )

    expected_stack_result = {
        "terraform": {
            "custom-providers": {"claranet/terraform-provider-gitlab": "2.1"},
            "vars": {"client_name": "claranet", "version": "0.11.14"},
        }
    }
    stack_config = tfwrapper.load_stack_config(paths["conf_dir"], "testaccount", "testenvironment", "testregion", "teststack")
    assert stack_config == expected_stack_result


def test_stack_config_parsing_extended_custom_provider(
    tmp_working_dir_empty_conf,
):  # noqa: D103
    paths = tmp_working_dir_empty_conf
    stack_config = paths["conf_dir"] / "testaccount_testenvironment_testregion_teststack.yml"

    stack_config.write_text(
        textwrap.dedent(
            """
            ---
            terraform:
                vars:
                    client_name: claranet
                    version: 0.11.14
                custom-providers:
                    claranet/terraform-provider-gitlab: '2.1'
                    custom/terraform-custom-provider:
                        version: '1.1.1'
                        extension: 'tar.gz'
            """
        )
    )

    expected_stack_result = {
        "terraform": {
            "custom-providers": {
                "claranet/terraform-provider-gitlab": "2.1",
                "custom/terraform-custom-provider": {"version": "1.1.1", "extension": "tar.gz"},
            },
            "vars": {"client_name": "claranet", "version": "0.11.14"},
        }
    }
    stack_config = tfwrapper.load_stack_config(paths["conf_dir"], "testaccount", "testenvironment", "testregion", "teststack")
    assert stack_config == expected_stack_result


def test_stack_config_parsing_invalid_custom_provider_missing_extension(tmp_working_dir_empty_conf, caplog):  # noqa: D103
    paths = tmp_working_dir_empty_conf
    stack_config = paths["conf_dir"] / "testaccount_testenvironment_testregion_teststack.yml"

    stack_config.write_text(
        textwrap.dedent(
            """
            ---
            terraform:
                vars:
                    client_name: claranet
                    version: 0.11.14
                custom-providers:
                    claranet/terraform-provider-gitlab: '2.1'
                    custom/terraform-custom-provider:
                        version: '1.1.1'
            """
        )
    )

    with pytest.raises(SystemExit):
        stack_config = tfwrapper.load_stack_config(
            paths["conf_dir"],
            "testaccount",
            "testenvironment",
            "testregion",
            "teststack",
        )
    assert "Missing key: 'extension'" in caplog.text


def test_stack_config_parsing_invalid_custom_provider_missing_version(tmp_working_dir_empty_conf, caplog):  # noqa: D103
    paths = tmp_working_dir_empty_conf
    stack_config = paths["conf_dir"] / "testaccount_testenvironment_testregion_teststack.yml"

    stack_config.write_text(
        textwrap.dedent(
            """
            ---
            terraform:
                vars:
                    client_name: claranet
                    version: 0.11.14
                custom-providers:
                    claranet/terraform-provider-gitlab: '2.1'
                    custom/terraform-custom-provider:
                        extension: '.zip'
            """
        )
    )

    with pytest.raises(SystemExit):
        stack_config = tfwrapper.load_stack_config(
            paths["conf_dir"],
            "testaccount",
            "testenvironment",
            "testregion",
            "teststack",
        )
    assert "Missing key: 'version'" in caplog.text
