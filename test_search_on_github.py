"""Test github releases searching."""

from importlib.machinery import SourceFileLoader

import pytest
import requests

tfwrapper = SourceFileLoader("tfwrapper", "bin/tfwrapper").load_module()


@pytest.fixture
def terraform_releases_html_after_v0_13_0():  # noqa: D103
    return """
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
    </head>

    <body>
        <div class="release-header">
            <a href="/hashicorp/terraform/releases/tag/v0.12.19">v0.12.19</a>
            <a href="/hashicorp/terraform/releases/tag/v0.12.18">v0.12.18</a>
            <a href="/hashicorp/terraform/releases/tag/v0.12.17">v0.12.17</a>
            <a href="/hashicorp/terraform/releases/tag/v0.12.16">v0.12.16</a>
            <a href="/hashicorp/terraform/releases/tag/v0.12.15">v0.12.15</a>
            <a href="/hashicorp/terraform/releases/tag/v0.12.14">v0.12.14</a>
            <a href="/hashicorp/terraform/releases/tag/v0.12.13">v0.12.13</a>
            <a href="/hashicorp/terraform/releases/tag/v0.12.12">v0.12.12</a>
            <a href="/hashicorp/terraform/releases/tag/v0.12.11">v0.12.11</a>
            <a href="/hashicorp/terraform/releases/tag/v0.12.10">v0.12.10</a>
        </div>
    </body>
</html>
    """


@pytest.fixture
def terraform_releases_html_after_v0_12_10():  # noqa: D103
    return """
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
    </head>

    <body>
        <div class="release-header">
            <a href="/hashicorp/terraform/releases/tag/v0.12.9">v0.12.9</a>
            <a href="/hashicorp/terraform/releases/tag/v0.12.8">v0.12.8</a>
            <a href="/hashicorp/terraform/releases/tag/v0.12.7">v0.12.7</a>
            <a href="/hashicorp/terraform/releases/tag/v0.12.6">v0.12.6</a>
            <a href="/hashicorp/terraform/releases/tag/v0.12.5">v0.12.5</a>
            <a href="/hashicorp/terraform/releases/tag/v0.12.4">v0.12.4</a>
            <a href="/hashicorp/terraform/releases/tag/v0.12.3">v0.12.3</a>
            <a href="/hashicorp/terraform/releases/tag/v0.12.2">v0.12.2</a>
            <a href="/hashicorp/terraform/releases/tag/v0.12.1">v0.12.1</a>
            <a href="/hashicorp/terraform/releases/tag/v0.12.0">v0.12.0</a>
        </div>
    </body>
</html>
    """


@pytest.fixture
def terraform_releases_html_after_v0_12_0():  # noqa: D103
    return """
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
    </head>

    <body>
        <div class="release-header">
            <a href="/hashicorp/terraform/releases/tag/v0.12.0-dev20190520H16">v0.12.0-dev20190520H16</a>
            <a href="/hashicorp/terraform/releases/tag/v0.11.14">v0.11.14</a>
            <a href="/hashicorp/terraform/releases/tag/v0.12.0-rc1">v0.12.0-rc1</a>
            <a href="/hashicorp/terraform/releases/tag/v0.12.0-beta2">v0.12.0-beta2</a>
            <a href="/hashicorp/terraform/releases/tag/v0.11.13">v0.11.13</a>
            <a href="/hashicorp/terraform/releases/tag/v0.11.12">v0.11.12</a>
            <a href="/hashicorp/terraform/releases/tag/v0.12.0-beta1">v0.12.0-beta1</a>
            <a href="/hashicorp/terraform/releases/tag/v0.11.12-beta1">v0.11.12-beta1</a>
            <a href="/hashicorp/terraform/releases/tag/v0.11.11">v0.11.11</a>
            <a href="/hashicorp/terraform/releases/tag/v0.12.0-alpha4">v0.12.0-alpha4</a>
        </div>
    </body>
</html>
    """


def test_search_on_github_terraform_releases(
    requests_mock,
    terraform_releases_html_after_v0_13_0,
    terraform_releases_html_after_v0_12_10,
    terraform_releases_html_after_v0_12_0,
):  # noqa: D103
    repo = "hashicorp/terraform"

    releases_url = "https://github.com/{}/releases".format(repo)
    releases_url_after_v0_13_0 = releases_url + "?after=v0.13.0"
    releases_url_after_v0_12_10 = releases_url + "?after=v0.12.10"
    releases_url_after_v0_12_0 = releases_url + "?after=v0.12.0"

    requests_mock.get(
        releases_url_after_v0_13_0,
        complete_qs=True,
        text=terraform_releases_html_after_v0_13_0,
    )
    requests_mock.get(
        releases_url_after_v0_12_10,
        complete_qs=True,
        text=terraform_releases_html_after_v0_12_10,
    )
    requests_mock.get(
        releases_url_after_v0_12_0,
        complete_qs=True,
        text=terraform_releases_html_after_v0_12_0,
    )

    assert terraform_releases_html_after_v0_13_0 == requests.get(releases_url_after_v0_13_0).text
    assert terraform_releases_html_after_v0_12_10 == requests.get(releases_url_after_v0_12_10).text
    assert terraform_releases_html_after_v0_12_0 == requests.get(releases_url_after_v0_12_0).text

    patch_regex = r"[0-9]+(((-alpha|-beta|-rc)[0-9]+)|(?P<dev>-dev))?"
    patch = tfwrapper.search_on_github(repo, "0.12", patch_regex, "14")
    assert patch == "14"

    patch = tfwrapper.search_on_github(repo, "0.12", patch_regex, "")
    assert patch == "19"

    patch = tfwrapper.search_on_github(repo, "0.11", patch_regex, "11")
    assert patch == "11"

    patch = tfwrapper.search_on_github(repo, "0.11", patch_regex, "")
    assert patch == "14"


@pytest.fixture
def provider_releases_html_after_v2_6_0():  # noqa: D103
    return """
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
    </head>

    <body>
        <div class="release-header">
            <a href="/claranet/terraform-provider-gitlab/releases/tag/v2.5.0-claranet">v2.5.0-claranet</a>
            <a href="/claranet/terraform-provider-gitlab/releases/tag/v2.5.0">v2.5.0</a>
            <a href="/claranet/terraform-provider-gitlab/releases/tag/v2.4.0">v2.4.0</a>
            <a href="/claranet/terraform-provider-gitlab/releases/tag/v2.3.0-claranet">v2.3.0-claranet</a>
            <a href="/claranet/terraform-provider-gitlab/releases/tag/v2.3.0">v2.3.0</a>
            <a href="/claranet/terraform-provider-gitlab/releases/tag/v2.2.0">v2.2.0</a>
            <a href="/claranet/terraform-provider-gitlab/releases/tag/v2.1.0-claranet">v2.1.0-claranet</a>
            <a href="/claranet/terraform-provider-gitlab/releases/tag/v2.1.0">v2.1.0</a>
            <a href="/claranet/terraform-provider-gitlab/releases/tag/v2.0.0">v2.0.0</a>
            <a href="/claranet/terraform-provider-gitlab/releases/tag/v1.3.0">v1.3.0</a>
        </div>
    </body>
</html>
    """


@pytest.fixture
def provider_releases_html_after_v1_3_0():  # noqa: D103
    return """
<!DOCTYPE html>
<html lang="en">
    <head>
        <meta charset="utf-8">
    </head>

    <body>
        <div class="release-header">
            <a href="/claranet/terraform-provider-gitlab/releases/tag/v1.2.9-claranet">v1.2.9-claranet</a>
            <a href="/claranet/terraform-provider-gitlab/releases/tag/v1.2.0">v1.2.0</a>
            <a href="/claranet/terraform-provider-gitlab/releases/tag/v1.0.3-claranet">v1.0.3-claranet</a>
            <a href="/claranet/terraform-provider-gitlab/releases/tag/v1.0.2-claranet">v1.0.2-claranet</a>
            <a href="/claranet/terraform-provider-gitlab/releases/tag/v1.0.1-claranet">v1.0.1-claranet</a>
            <a href="/claranet/terraform-provider-gitlab/releases/tag/list">list</a>
            <a href="/claranet/terraform-provider-gitlab/releases/tag/v1.1.0">v1.1.0</a>
            <a href="/claranet/terraform-provider-gitlab/releases/tag/v1.0.0-claranet">v1.0.0-claranet</a>
            <a href="/claranet/terraform-provider-gitlab/releases/tag/v1.0.0">v1.0.0</a>
            <a href="/claranet/terraform-provider-gitlab/releases/tag/v0.1.0">v0.1.0</a>
        </div>
    </body>
</html>
    """


def test_search_on_github_provider_releases(
    requests_mock,
    provider_releases_html_after_v2_6_0,
    provider_releases_html_after_v1_3_0,
):  # noqa: D103
    from tfwrapper import GITHUB_RELEASES

    repo = "claranet/terraform-provider-gitlab"
    releases_url = GITHUB_RELEASES.format(repo)
    releases_url_after_v2_6_0 = releases_url + "?after=v2.6.0"
    releases_url_after_v1_3_0 = releases_url + "?after=v1.3.0"

    requests_mock.get(
        releases_url_after_v2_6_0,
        complete_qs=True,
        text=provider_releases_html_after_v2_6_0,
    )
    requests_mock.get(
        releases_url_after_v1_3_0,
        complete_qs=True,
        text=provider_releases_html_after_v1_3_0,
    )

    assert provider_releases_html_after_v2_6_0 == requests.get(releases_url_after_v2_6_0).text

    patch_regex = r"[0-9]+(((-alpha|-beta|-rc)[0-9]+)|(?P<dev>-dev))?"
    patch = tfwrapper.search_on_github(repo, "2.5", patch_regex, "")
    assert patch == "0"

    patch_regex = r"[0-9]+(((-alpha|-beta|-rc)[0-9]+)|(?P<dev>-dev))?"
    patch = tfwrapper.search_on_github(repo, "2.5", patch_regex, "0-claranet")
    assert patch == "0-claranet"

    patch_regex = r"[0-9]+(((-alpha|-beta|-rc)[0-9]+)|(?P<dev>-dev))?"
    patch = tfwrapper.search_on_github(repo, "1.2", patch_regex, "")
    assert patch == "0"

    patch_regex = r"[0-9]+(((-alpha|-beta|-rc)[0-9]+)|(?P<dev>-dev))?"
    patch = tfwrapper.search_on_github(repo, "1.2", patch_regex, "9-claranet")
    assert patch == "9-claranet"
