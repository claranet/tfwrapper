"""Test config is loaded depending on cmd line arguments."""


import os
import textwrap

import pytest

import tfwrapper


def test_config_load_help():  # noqa: D103
    with pytest.raises(SystemExit) as e:
        tfwrapper.parse_args([])
    assert e.value.code == 0


def test_config_load_switchver():  # noqa: D103
    with pytest.raises(SystemExit) as e:
        tfwrapper.main(["switchver"])
    assert e.value.code == 2


def test_config_load_init(tmp_working_dir_regional):  # noqa: D103
    paths = tmp_working_dir_regional
    os.chdir(paths["stack_dir"])

    with pytest.raises(FileNotFoundError) as e:
        tfwrapper.main(["init"])
    assert "No such file or directory" in str(e)

    paths["state_conf"].write_text("---")
    paths["state_conf"].write_text("---")
    paths["stack_conf"] = paths["conf_dir"] / "testaccount_testenvironment_testregion_teststack.yml"
    paths["stack_conf"].write_text(
        textwrap.dedent(
            """
            ---
            terraform:
              vars:
                myvar: myvalue
            """
        )
    )
    paths["terraform_conf"] = paths["stack_dir"] / "test.tf"

    with pytest.raises(SystemExit) as e:
        tfwrapper.main(["init"])
    assert e.type == SystemExit
    assert e.value.code == 0


def test_config_load_plan(tmp_working_dir_regional):  # noqa: D103
    paths = tmp_working_dir_regional
    os.chdir(paths["stack_dir"])

    with pytest.raises(FileNotFoundError) as e:
        tfwrapper.main(["plan"])
    assert "No such file or directory" in str(e)

    paths["state_conf"].write_text("---")
    paths["stack_conf"] = paths["conf_dir"] / "testaccount_testenvironment_testregion_teststack.yml"
    paths["stack_conf"].write_text(
        textwrap.dedent(
            """
            ---
            terraform:
              vars:
                myvar: myvalue
            """
        )
    )
    paths["terraform_conf"] = paths["stack_dir"] / "test.tf"

    with pytest.raises(SystemExit) as e:
        tfwrapper.main(["plan"])
    assert e.type == SystemExit
    assert e.value.code == 0
