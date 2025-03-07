"""Test HTTP(S) requests caching."""

from email.utils import formatdate

import pook
import mock
from pook.interceptors.urllib3 import io
import pytest


import claranet_tfwrapper as tfwrapper


@pytest.fixture
def terraform_releases_html_after_v0_13_0():
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


# This test uses pook instead of requests_mock because:
# - requests_mock intercepts requests at the Adapter level and thus prevents using
#   CacheControl at the same time as it also works at the Adapter level.
# - pook intercepts requests at a lower level by replacing urllib3.urlopen() by its
#   own handler. This allows to actually verify what network requests would happen.
# See https://github.com/h2non/pook/blob/v1.0.2/pook/interceptors/urllib3.py#L24-L27


class AutoclosingBytesIO(io.BytesIO):
    """AutoclosingBytesIO extends io.BytesIO to autoclose itself.

    CacheControl only flushes its buffer into its cache when the underlying IO
    is closed. pook uses io.BytesIO which does not automatically close itself when
    consumed so we need to subclass it and just do this.
    """

    def __init__(self, *args, **kwargs):
        """Initialize the bytes I/O stream."""
        return super(io.BytesIO, self).__init__(*args, **kwargs)

    def read(self, size=-1):
        """Read and, if at end, close the bytes I/O stream."""
        data = super(AutoclosingBytesIO, self).read(size)
        pos = self.tell()
        if not super(AutoclosingBytesIO, self).read():
            # If there is no more data to read, close the stream
            self.close()
        else:
            # Otherwise restore position
            self.seek(pos)
        return data


def test_search_on_github_cache_terraform_releases_200(
    tmp_working_dir,
    terraform_releases_html_after_v0_13_0,
):
    with mock.patch("io.BytesIO", AutoclosingBytesIO):
        with pook.use():
            repo = "hashicorp/terraform"
            releases_url = "https://github.com/{}/tags?after=v0.13.0".format(repo)

            # A volatile mock that can only be invoked once
            pook.get(
                releases_url,
                reply=200,
                response_type="text/plain",
                response_body=terraform_releases_html_after_v0_13_0,
                response_headers={
                    "Status": "200 OK",
                    "ETag": 'W/"df0474ebd25f223a95926ba58e11e77b"',
                    "Cache-Control": "max-age=0, private, must-revalidate",
                    "Date": formatdate(usegmt=True),
                },
                times=1,
            )

            patch_regex = r"[0-9]+(((-alpha|-beta|-rc)[0-9]+)|(?P<dev>-dev))?"

            patch = tfwrapper.search_on_github(repo, "0.12", patch_regex, "14")
            assert patch == "14"

            patch = tfwrapper.search_on_github(repo, "0.12", patch_regex, "")
            assert patch == "19"

            assert pook.isdone()
            assert not pook.pending_mocks()
            assert not pook.unmatched_requests()
    assert not pook.isactive()


def test_search_on_github_cache_terraform_releases_does_not_cache_error_429(
    tmp_working_dir, terraform_releases_html_after_v0_13_0
):
    with mock.patch("io.BytesIO", AutoclosingBytesIO):
        with pook.use():
            repo = "hashicorp/terraform"
            releases_url = "https://github.com/{}/tags?after=v0.13.0".format(repo)

            # volatile mocks that can only be invoked once each
            pook.get(
                releases_url,
                reply=429,
                response_headers={"Status": "429 Too Many Requests", "Date": formatdate(usegmt=True), "Retry-After": "120"},
                times=1,
            )
            pook.get(
                releases_url,
                reply=200,
                response_type="text/plain",
                response_body=terraform_releases_html_after_v0_13_0,
                response_headers={
                    "Status": "200 OK",
                    "ETag": 'W/"df0474ebd25f223a95926ba58e11e77b"',
                    "Cache-Control": "max-age=0, private, must-revalidate",
                    "Date": formatdate(usegmt=True),
                },
                times=1,
            )

            patch_regex = r"[0-9]+(((-alpha|-beta|-rc)[0-9]+)|(?P<dev>-dev))?"

            # pook does not implement urllib3's retry logic so this first request will always return None during tests
            patch = tfwrapper.search_on_github(repo, "0.12", patch_regex, "14")
            assert patch is None

            patch = tfwrapper.search_on_github(repo, "0.12", patch_regex, "14")
            assert patch == "14"

            patch = tfwrapper.search_on_github(repo, "0.12", patch_regex, "")
            assert patch == "19"

            assert pook.isdone()
            assert not pook.pending_mocks()
            assert not pook.unmatched_requests()
    assert not pook.isactive()


def test_search_on_github_cache_terraform_releases_does_not_cache_error_403(
    tmp_working_dir,
    terraform_releases_html_after_v0_13_0,
):
    with mock.patch("io.BytesIO", AutoclosingBytesIO):
        with pook.use():
            repo = "hashicorp/terraform"
            releases_url = "https://github.com/{}/tags?after=v0.13.0".format(repo)

            # volatile mocks that can only be invoked once each
            pook.get(
                releases_url,
                reply=403,
                response_headers={"Status": "403 Forbidden", "Date": formatdate(usegmt=True)},
                times=1,
            )
            pook.get(
                releases_url,
                reply=200,
                response_type="text/plain",
                response_body=terraform_releases_html_after_v0_13_0,
                response_headers={
                    "Status": "200 OK",
                    "ETag": 'W/"df0474ebd25f223a95926ba58e11e77b"',
                    "Cache-Control": "max-age=0, private, must-revalidate",
                    "Date": formatdate(usegmt=True),
                },
                times=1,
            )

            patch_regex = r"[0-9]+(((-alpha|-beta|-rc)[0-9]+)|(?P<dev>-dev))?"

            # pook does not implement urllib3's retry logic so this first request will always return None during tests
            patch = tfwrapper.search_on_github(repo, "0.12", patch_regex, "14")
            assert patch is None

            patch = tfwrapper.search_on_github(repo, "0.12", patch_regex, "14")
            assert patch == "14"

            patch = tfwrapper.search_on_github(repo, "0.12", patch_regex, "")
            assert patch == "19"

            assert pook.isdone()
            assert not pook.pending_mocks()
            assert not pook.unmatched_requests()
    assert not pook.isactive()


def test_search_on_github_cache_terraform_releases_does_not_cache_error_404(
    tmp_working_dir,
    terraform_releases_html_after_v0_13_0,
):
    with mock.patch("io.BytesIO", AutoclosingBytesIO):
        with pook.use():
            repo = "hashicorp/terraform"
            releases_url = "https://github.com/{}/tags?after=v0.13.0".format(repo)

            # volatile mocks that can only be invoked once each
            pook.get(
                releases_url,
                reply=404,
                response_headers={"Status": "404 Not found", "Date": formatdate(usegmt=True)},
                times=1,
            )
            pook.get(
                releases_url,
                reply=200,
                response_type="text/plain",
                response_body=terraform_releases_html_after_v0_13_0,
                response_headers={
                    "Status": "200 OK",
                    "ETag": 'W/"df0474ebd25f223a95926ba58e11e77b"',
                    "Cache-Control": "max-age=0, private, must-revalidate",
                    "Date": formatdate(usegmt=True),
                },
                times=1,
            )

            patch_regex = r"[0-9]+(((-alpha|-beta|-rc)[0-9]+)|(?P<dev>-dev))?"

            # pook does not implement urllib3's retry logic so this first request will always return None during tests
            patch = tfwrapper.search_on_github(repo, "0.12", patch_regex, "14")
            assert patch is None

            patch = tfwrapper.search_on_github(repo, "0.12", patch_regex, "14")
            assert patch == "14"

            patch = tfwrapper.search_on_github(repo, "0.12", patch_regex, "")
            assert patch == "19"

            assert pook.isdone()
            assert not pook.pending_mocks()
            assert not pook.unmatched_requests()
    assert not pook.isactive()
