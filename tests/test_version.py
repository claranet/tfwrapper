"""Test version management."""

import toml
from pathlib import Path
import claranet_tfwrapper as tfwrapper


def test_versions_are_in_sync():
    """Checks if the pyproject.toml and package.__init__.py __version__ are in sync."""
    path = Path(__file__).resolve().parents[1] / "pyproject.toml"
    pyproject = toml.loads(open(str(path)).read())
    pyproject_version = pyproject["project"]["version"]

    package_init_version = tfwrapper.__version__

    assert package_init_version == pyproject_version.replace("-alpha.", "a").replace("-beta.", "b").replace("-rc.", "rc")
