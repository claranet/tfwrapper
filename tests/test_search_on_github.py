"""Test github releases searching."""

import pytest
import requests

import claranet_tfwrapper as tfwrapper


@pytest.fixture
def provider_releases_html_after_v2_6_0():
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
def provider_releases_html_after_v1_3_0():
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
):
    from claranet_tfwrapper import GITHUB_RELEASES

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
