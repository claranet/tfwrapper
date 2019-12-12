from importlib.machinery import SourceFileLoader
from unittest.mock import MagicMock, patch
import colorlog
import subprocess
import os

tfwrapper = SourceFileLoader("tfwrapper", "bin/tfwrapper").load_module()


@patch('pathlib.Path.is_file')
def test_dot_kubeconfig_refresh(mock_is_file):
    logger = colorlog.getLogger()
    logger.info = MagicMock()
    logger.error = MagicMock()
    os.environ = {}

    adc_path = '/home/test/.config/gcloud/application_default_credentials.json'
    gke_name = 'gke-testproject'
    project = 'testproject'
    region = 'testregion'
    kubeconfig_path = '/home/test/.run/testaccount/testenvironment/{}/{}.kubeconfig'.format(region, gke_name)
    cmd_env = {}
    cmd_env['CLOUDSDK_CONTAINER_USE_APPLICATION_DEFAULT_CREDENTIALS'] = 'true'
    cmd_env['CLOUDSDK_AUTH_CREDENTIAL_FILE_OVERRIDE'] = adc_path
    cmd_env['KUBECONFIG'] = kubeconfig_path
    command = ['gcloud', 'container', 'clusters', 'get-credentials', gke_name,
               '--project', project,
               '--region', region]

    # never is old behavior, refresh only if file does not exist
    refresh_kubeconfig = 'never'
    mock_is_file.return_value = True
    subprocess.run = MagicMock()
    tfwrapper.adc_check_gke_credentials(adc_path, kubeconfig_path, gke_name, project, region=region, refresh_kubeconfig=refresh_kubeconfig)
    subprocess.run.assert_not_called()

    mock_is_file.return_value = False
    subprocess.run = MagicMock()
    tfwrapper.adc_check_gke_credentials(adc_path, kubeconfig_path, gke_name, project, region=region, refresh_kubeconfig=refresh_kubeconfig)
    subprocess.run.assert_called_with(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True, env=cmd_env)

    # always => we refresh no matter if kubeconfig_path exists
    refresh_kubeconfig = 'always'
    mock_is_file.return_value = True
    subprocess.run = MagicMock()
    tfwrapper.adc_check_gke_credentials(adc_path, kubeconfig_path, gke_name, project, region=region, refresh_kubeconfig=refresh_kubeconfig)
    subprocess.run.assert_called_with(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True, env=cmd_env)

    mock_is_file.return_value = False
    subprocess.run = MagicMock()
    tfwrapper.adc_check_gke_credentials(adc_path, kubeconfig_path, gke_name, project, region=region, refresh_kubeconfig=refresh_kubeconfig)
    subprocess.run.assert_called_with(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True, env=cmd_env)

    refresh_kubeconfig = 'invalid'
    subprocess.run = MagicMock()
    try:
        tfwrapper.adc_check_gke_credentials(adc_path, kubeconfig_path, gke_name, project, region=region, refresh_kubeconfig=refresh_kubeconfig)
    except SystemExit:
        subprocess.run.assert_not_called()
        logger.error.assert_called_with('refresh_kubeconfig must be one of "always", "never" but is invalid')

