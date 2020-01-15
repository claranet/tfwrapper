from email.utils import formatdate
from importlib.machinery import SourceFileLoader

import pook
import mock
from pook.interceptors.urllib3 import io

from test_search_on_github import terraform_releases_html_after_v0_13_0

tfwrapper = SourceFileLoader("tfwrapper", "bin/tfwrapper").load_module()


# This test uses pook instead of requests_mock because:
# - requests_mock intercepts requests at the Adapter level and thus prevents using
#   CacheControl at the same time as it also works at the Adapter level.
# - pook intercepts requests at a lower level by replacing urllib3.urlopen() by its
#   own handler. This allows to actually verify what network requests would happen.
# See https://github.com/h2non/pook/blob/v0.2.8/pook/interceptors/urllib3.py#L19-L20


class AutoclosingBytesIO(io.BytesIO):
    """
    CacheControl only flushes its buffer into its cache when the underlying IO
    is closed. pook uses io.BytesIO which does not automatically close itself when
    consumed so we need to subclass it and just do this.
    """

    def __init__(self, *args, **kwargs):
        return super(io.BytesIO, self).__init__(*args, **kwargs)

    def read(self, size=-1):
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
    tmp_working_dir, terraform_releases_html_after_v0_13_0,
):
    with mock.patch("io.BytesIO", AutoclosingBytesIO):
        with pook.use():
            repo = "hashicorp/terraform"
            releases_url = "https://github.com/{}/releases?after=v0.13.0".format(repo)

            # A volatile mock that can only be invoked once
            pook.get(
                releases_url,
                reply=200,
                response_type="text/plain",
                response_body=terraform_releases_html_after_v0_13_0,
                response_headers={
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


def test_search_on_github_cache_terraform_releases_does_not_cache_errors(
    tmp_working_dir, terraform_releases_html_after_v0_13_0,
):
    with mock.patch("io.BytesIO", AutoclosingBytesIO):
        with pook.use():
            repo = "hashicorp/terraform"
            releases_url = "https://github.com/{}/releases?after=v0.13.0".format(repo)

            # volatile mocks that can only be invoked once each
            pook.get(
                releases_url,
                reply=429,
                response_headers={
                    "Cache-Control": "max-age=0, private, must-revalidate",
                    "Date": formatdate(usegmt=True),
                    "Retry-After": "5",
                },
                times=1,
            )
            pook.get(
                releases_url,
                reply=200,
                response_type="text/plain",
                response_body=terraform_releases_html_after_v0_13_0,
                response_headers={
                    "Cache-Control": "max-age=0, private, must-revalidate",
                    "Date": formatdate(usegmt=True),
                },
                times=1,
            )

            patch_regex = r"[0-9]+(((-alpha|-beta|-rc)[0-9]+)|(?P<dev>-dev))?"

            patch = tfwrapper.search_on_github(repo, "0.12", patch_regex, "14")
            # TODO: handle retries
            assert patch is None

            patch = tfwrapper.search_on_github(repo, "0.12", patch_regex, "14")
            assert patch == "14"

            assert pook.isdone()
            assert not pook.pending_mocks()
            assert not pook.unmatched_requests()
