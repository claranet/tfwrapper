from importlib.machinery import SourceFileLoader

import pytest
import requests

tfwrapper = SourceFileLoader("tfwrapper", "bin/tfwrapper").load_module()


RESPONSE_TEXT_VALUE = """
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


def test_search_on_github_terraform_releases(requests_mock):
    request_invocations = 0

    def text_callback(request, context):
        nonlocal request_invocations
        request_invocations += 1
        return RESPONSE_TEXT_VALUE

    terraform_releases_response_200 = {
        "status_code": 200,
        "headers": {"Cache-Control": "max-age=0, private, must-revalidate"},
        "text": text_callback,
    }

    repo = "hashicorp/terraform"

    releases_url = "https://github.com/{}/releases".format(repo)

    requests_mock.get(releases_url, **terraform_releases_response_200)

    response = requests.get(releases_url)
    assert terraform_releases_response_200["status_code"] == response.status_code
    assert terraform_releases_response_200["headers"] == response.headers
    assert RESPONSE_TEXT_VALUE == response.text
    assert request_invocations == 1
    request_invocations = 0

    patch_regex = r"[0-9]+(((-alpha|-beta|-rc)[0-9]+)|(?P<dev>-dev))?"
    patch = tfwrapper.search_on_github(repo, "0.12", patch_regex, "14")
    assert patch == "14"

    patch = tfwrapper.search_on_github(repo, "0.12", patch_regex, "")
    assert patch == "19"

    assert request_invocations == 1
