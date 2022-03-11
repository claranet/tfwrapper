"""Test GCP/GKE configuration parsing."""

import os
import subprocess
import textwrap

from copy import deepcopy

import pytest

from unittest.mock import MagicMock, patch

import claranet_tfwrapper as tfwrapper


@patch("pathlib.Path.is_file")
def test_dot_kubeconfig_refresh(mock_is_file, monkeypatch, caplog):
    adc_path = "/home/test/.config/gcloud/application_default_credentials.json"
    gke_name = "gke-testproject"
    project = "testproject"
    region = "testregion"
    kubeconfig_path = "/home/test/.run/testaccount/testenvironment/{}/{}.kubeconfig".format(region, gke_name)
    cmd_env = deepcopy(os.environ)
    cmd_env["CLOUDSDK_CONTAINER_USE_APPLICATION_DEFAULT_CREDENTIALS"] = "true"
    cmd_env["CLOUDSDK_AUTH_CREDENTIAL_FILE_OVERRIDE"] = adc_path
    cmd_env["KUBECONFIG"] = kubeconfig_path
    command = [
        "gcloud",
        "container",
        "clusters",
        "get-credentials",
        gke_name,
        "--project",
        project,
        "--region",
        region,
    ]

    # never is old behavior, refresh only if file does not exist
    refresh_kubeconfig = "never"
    mock_is_file.return_value = True
    monkeypatch.setattr(subprocess, "run", MagicMock())
    tfwrapper.adc_check_gke_credentials(
        adc_path,
        kubeconfig_path,
        gke_name,
        project,
        region=region,
        refresh_kubeconfig=refresh_kubeconfig,
    )
    subprocess.run.assert_not_called()

    mock_is_file.return_value = False
    monkeypatch.setattr(subprocess, "run", MagicMock())
    tfwrapper.adc_check_gke_credentials(
        adc_path,
        kubeconfig_path,
        gke_name,
        project,
        region=region,
        refresh_kubeconfig=refresh_kubeconfig,
    )
    subprocess.run.assert_called_with(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
        env=cmd_env,
    )

    # always => we refresh no matter if kubeconfig_path exists
    refresh_kubeconfig = "always"
    mock_is_file.return_value = True
    monkeypatch.setattr(subprocess, "run", MagicMock())
    tfwrapper.adc_check_gke_credentials(
        adc_path,
        kubeconfig_path,
        gke_name,
        project,
        region=region,
        refresh_kubeconfig=refresh_kubeconfig,
    )
    subprocess.run.assert_called_with(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
        env=cmd_env,
    )

    mock_is_file.return_value = False
    monkeypatch.setattr(subprocess, "run", MagicMock())
    tfwrapper.adc_check_gke_credentials(
        adc_path,
        kubeconfig_path,
        gke_name,
        project,
        region=region,
        refresh_kubeconfig=refresh_kubeconfig,
    )
    subprocess.run.assert_called_with(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=True,
        env=cmd_env,
    )

    refresh_kubeconfig = "invalid"
    monkeypatch.setattr(subprocess, "run", MagicMock())
    try:
        tfwrapper.adc_check_gke_credentials(
            adc_path,
            kubeconfig_path,
            gke_name,
            project,
            region=region,
            refresh_kubeconfig=refresh_kubeconfig,
        )
    except SystemExit:
        subprocess.run.assert_not_called()
        assert 'refresh_kubeconfig must be one of "always", "never" but is invalid' in caplog.text


def test_refresh_kubeconfig_invalid_setting(tmp_working_dir_empty_conf, caplog):
    paths = tmp_working_dir_empty_conf
    stack_config_file = paths["conf_dir"] / "testaccount_testenvironment_testregion_teststack.yml"
    stack_config_file.write_text(
        textwrap.dedent(
            """
            ---
            gcp:
              general:
                mode: adc-user
                project: &gcp_project testproject
              gke:
              - nae: gke-testproject2
                zone: europe-west1-b
                refresh_kubeconfig: invalid
            terraform:
              vars:
                client_name: claranet
            """
        )
    )

    with pytest.raises(SystemExit):
        tfwrapper.load_stack_config_from_file(stack_config_file)
    assert "Or('always', 'never') did not validate 'invalid'" in caplog.text


def test_refresh_kubeconfig_setting(tmp_working_dir_empty_conf):
    paths = tmp_working_dir_empty_conf
    stack_config_file = paths["conf_dir"] / "testaccount_testenvironment_testregion_teststack.yml"

    stack_config_file.write_text(
        textwrap.dedent(
            """
            ---
            gcp:
              general:
                mode: adc-user
                project: &gcp_project testproject
              gke:
              - name: gke-testproject
                zone: europe-west1-b
            terraform:
              vars:
                client_name: claranet
            """
        )
    )

    expected_stack_result = {
        "gcp": {
            "general": {"mode": "adc-user", "project": "testproject"},
            "gke": [{"name": "gke-testproject", "zone": "europe-west1-b"}],
        },
        "terraform": {"vars": {"client_name": "claranet"}},
    }

    stack_config = tfwrapper.load_stack_config_from_file(stack_config_file)
    assert stack_config == expected_stack_result

    stack_config_file.write_text(
        textwrap.dedent(
            """
            ---
            gcp:
              general:
                mode: adc-user
                project: &gcp_project testproject
              gke:
              - name: gke-testproject
                zone: europe-west1-b
                refresh_kubeconfig: always
            terraform:
              vars:
                client_name: claranet
            """
        )
    )

    expected_stack_result = {
        "gcp": {
            "general": {"mode": "adc-user", "project": "testproject"},
            "gke": [{"name": "gke-testproject", "zone": "europe-west1-b", "refresh_kubeconfig": "always"}],
        },
        "terraform": {"vars": {"client_name": "claranet"}},
    }

    stack_config = tfwrapper.load_stack_config_from_file(stack_config_file)
    assert stack_config == expected_stack_result

    stack_config_file.write_text(
        textwrap.dedent(
            """
            ---
            gcp:
              general:
                mode: adc-user
                project: &gcp_project testproject
              gke:
              - name: gke-testproject
                zone: europe-west1-b
                refresh_kubeconfig: never
            terraform:
              vars:
                client_name: claranet
            """
        )
    )

    expected_stack_result = {
        "gcp": {
            "general": {"mode": "adc-user", "project": "testproject"},
            "gke": [{"name": "gke-testproject", "zone": "europe-west1-b", "refresh_kubeconfig": "never"}],
        },
        "terraform": {"vars": {"client_name": "claranet"}},
    }

    stack_config = tfwrapper.load_stack_config_from_file(stack_config_file)
    assert stack_config == expected_stack_result
