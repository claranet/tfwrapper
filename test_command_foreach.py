"""Test foreach command behavior."""

from importlib.machinery import SourceFileLoader

from copy import deepcopy

import os
import pathlib
import textwrap

import pytest

tfwrapper = SourceFileLoader("tfwrapper", "bin/tfwrapper").load_module()


@pytest.fixture
def multiple_stacks():  # noqa: D103
    return [
        ("account0", "global", None, "default"),
        ("account0", "preprod", "eu-west-1", "default"),
        ("account0", "preprod", "eu-west-1", "infra"),
        ("account0", "preprod", "eu-west-2", "default"),
        ("account0", "preprod", "eu-west-2", "infra"),
        ("account0", "prod", "eu-west-1", "default"),
        ("account0", "prod", "eu-west-1", "infra"),
        ("account0", "prod", "eu-west-4", "default"),
        ("account0", "prod", "eu-west-4", "infra"),
        ("account0", "test", "eu-west-1", "default"),
        ("account0", "test", "eu-west-1", "infra"),
        ("account0", "test", "eu-west-2", "default"),
        ("account0", "test", "eu-west-2", "infra"),
        ("account0", "test", "eu-west-3", "default"),
        ("account1", "global", None, "default"),
        ("account1", "preprod", "eu-west-1", "default"),
        ("account1", "preprod", "eu-west-1", "infra"),
        ("account1", "preprod", "eu-west-2", "default"),
        ("account1", "preprod", "eu-west-2", "infra"),
        ("account1", "prod", "eu-west-1", "default"),
        ("account1", "prod", "eu-west-1", "infra"),
        ("account1", "prod", "eu-west-4", "default"),
        ("account1", "prod", "eu-west-4", "infra"),
    ]


@pytest.fixture
def tmp_working_dir_multiple_stacks(tmp_working_dir_empty_conf, multiple_stacks):
    """
    Provide a somewhat representative directory tree with multiple stacks, regional and global.

    .
    ├── account0
    │   ├── _global
    │   │   └── default
    │   ├── preprod
    │   │   ├── eu-west-1
    │   │   │   ├── default
    │   │   │   └── infra
    │   │   └── eu-west-2
    │   │       ├── default
    │   │       └── infra
    │   ├── prod
    │   │   ├── eu-west-1
    │   │   │   ├── default
    │   │   │   └── infra
    │   │   └── eu-west-4
    │   │       ├── default
    │   │       └── infra
    │   └── test
    │       ├── eu-west-1
    │       │   ├── default
    │       │   └── infra
    │       ├── eu-west-2
    │       │   ├── default
    │       │   └── infra
    │       └── eu-west-3
    │           └── default
    ├── account1
    │   ├── _global
    │   │   └── default
    │   ├── preprod
    │   │   ├── eu-west-1
    │   │   │   ├── default
    │   │   │   └── infra
    │   │   └── eu-west-2
    │   │       ├── default
    │   │       └── infra
    │   └── prod
    │       ├── eu-west-1
    │       │   ├── default
    │       │   └── infra
    │       └── eu-west-4
    │           ├── default
    │           └── infra
    └── conf
    """
    paths = tmp_working_dir_empty_conf
    dummy_conf = textwrap.dedent(
        """
            ---
            terraform:
              vars:
                myvar: myvalue
            """
    )

    for account, environment, region, stack in multiple_stacks:
        pathlib.Path(tfwrapper.get_stack_dir(paths["working_dir"], account, environment, region, stack)).mkdir(parents=True)
        pathlib.Path(tfwrapper.get_stack_config_path(paths["conf_dir"], account, environment, region, stack)).write_text(
            dummy_conf
        )

    # Stack with no matching directory
    pathlib.Path(tfwrapper.get_stack_config_path(paths["conf_dir"], "account2", "global", None, "default")).write_text(dummy_conf)

    return paths


def test_foreach_select_all_stacks(tmp_working_dir_multiple_stacks, multiple_stacks, default_args, caplog):  # noqa: D103
    wrapper_config = deepcopy(vars(default_args))
    parents_count = tfwrapper.detect_config_dir(wrapper_config)
    tfwrapper.detect_stack(wrapper_config, parents_count, raise_on_missing=False)

    stacks_with_configs = tfwrapper.foreach_select_stacks(wrapper_config)
    for stack_path, stack_config in stacks_with_configs.items():
        wrapper_stack_config = deepcopy(wrapper_config)
        parents_count = tfwrapper.detect_config_dir(wrapper_stack_config, dir=stack_path)
        tfwrapper.detect_stack(wrapper_stack_config, parents_count, raise_on_missing=False, dir=stack_path)
        stack_env = tfwrapper.get_stack_envvars(stack_config, wrapper_stack_config)
        assert "PATH" in stack_env
        assert stack_env["TFWRAPPER_TF_myvar"] == "myvalue"
        assert stack_env["TFWRAPPER_account"] == wrapper_stack_config["account"]
        assert stack_env["TFWRAPPER_environment"] == wrapper_stack_config["environment"]
        assert stack_env["TFWRAPPER_stack"] == wrapper_stack_config["stack"]
        assert stack_env["TFWRAPPER_region"] == (wrapper_stack_config["region"] or "")

    stacks = [*stacks_with_configs]
    for i in range(len(stacks)):
        assert str(stacks[i]) == tfwrapper.get_stack_dir(wrapper_config["rootdir"], *multiple_stacks[i])
    assert len(stacks) == len(multiple_stacks)
    assert "Stack config conf/account2_global_default.yml has no matching directory at" in caplog.text


def test_foreach_select_from_dir_account0(tmp_working_dir_multiple_stacks, multiple_stacks, default_args):  # noqa: D103
    paths = tmp_working_dir_multiple_stacks

    os.chdir((paths["working_dir"] / "account0"))

    wrapper_config = deepcopy(vars(default_args))
    parents_count = tfwrapper.detect_config_dir(wrapper_config)
    tfwrapper.detect_stack(wrapper_config, parents_count, raise_on_missing=False)

    stacks = [*tfwrapper.foreach_select_stacks(wrapper_config)]

    expected_stacks = [
        ("account0", "global", None, "default"),
        ("account0", "preprod", "eu-west-1", "default"),
        ("account0", "preprod", "eu-west-1", "infra"),
        ("account0", "preprod", "eu-west-2", "default"),
        ("account0", "preprod", "eu-west-2", "infra"),
        ("account0", "prod", "eu-west-1", "default"),
        ("account0", "prod", "eu-west-1", "infra"),
        ("account0", "prod", "eu-west-4", "default"),
        ("account0", "prod", "eu-west-4", "infra"),
        ("account0", "test", "eu-west-1", "default"),
        ("account0", "test", "eu-west-1", "infra"),
        ("account0", "test", "eu-west-2", "default"),
        ("account0", "test", "eu-west-2", "infra"),
        ("account0", "test", "eu-west-3", "default"),
    ]
    for i in range(len(stacks)):
        assert str(stacks[i]) == tfwrapper.get_stack_dir(wrapper_config["rootdir"], *expected_stacks[i])
    assert len(stacks) == len(expected_stacks)


def test_foreach_select_from_dir_account0_prod(tmp_working_dir_multiple_stacks, multiple_stacks, default_args):  # noqa: D103
    paths = tmp_working_dir_multiple_stacks

    os.chdir((paths["working_dir"] / "account0/prod"))

    wrapper_config = deepcopy(vars(default_args))
    parents_count = tfwrapper.detect_config_dir(wrapper_config)
    tfwrapper.detect_stack(wrapper_config, parents_count, raise_on_missing=False)

    stacks = [*tfwrapper.foreach_select_stacks(wrapper_config)]

    expected_stacks = [
        ("account0", "prod", "eu-west-1", "default"),
        ("account0", "prod", "eu-west-1", "infra"),
        ("account0", "prod", "eu-west-4", "default"),
        ("account0", "prod", "eu-west-4", "infra"),
    ]
    for i in range(len(stacks)):
        assert str(stacks[i]) == tfwrapper.get_stack_dir(wrapper_config["rootdir"], *expected_stacks[i])
    assert len(stacks) == len(expected_stacks)


def test_foreach_select_from_dir_account0_prod_euw1(tmp_working_dir_multiple_stacks, multiple_stacks, default_args):  # noqa: D103
    paths = tmp_working_dir_multiple_stacks

    os.chdir((paths["working_dir"] / "account0/prod/eu-west-1"))

    wrapper_config = deepcopy(vars(default_args))
    parents_count = tfwrapper.detect_config_dir(wrapper_config)
    tfwrapper.detect_stack(wrapper_config, parents_count, raise_on_missing=False)

    stacks = [*tfwrapper.foreach_select_stacks(wrapper_config)]

    expected_stacks = [
        ("account0", "prod", "eu-west-1", "default"),
        ("account0", "prod", "eu-west-1", "infra"),
    ]
    for i in range(len(stacks)):
        assert str(stacks[i]) == tfwrapper.get_stack_dir(wrapper_config["rootdir"], *expected_stacks[i])
    assert len(stacks) == len(expected_stacks)


def test_foreach_select_from_args_account0(tmp_working_dir_multiple_stacks, multiple_stacks, default_args):  # noqa: D103
    default_args.account = "account0"

    wrapper_config = deepcopy(vars(default_args))
    parents_count = tfwrapper.detect_config_dir(wrapper_config)
    tfwrapper.detect_stack(wrapper_config, parents_count, raise_on_missing=False)

    stacks = [*tfwrapper.foreach_select_stacks(wrapper_config)]

    expected_stacks = [
        ("account0", "global", None, "default"),
        ("account0", "preprod", "eu-west-1", "default"),
        ("account0", "preprod", "eu-west-1", "infra"),
        ("account0", "preprod", "eu-west-2", "default"),
        ("account0", "preprod", "eu-west-2", "infra"),
        ("account0", "prod", "eu-west-1", "default"),
        ("account0", "prod", "eu-west-1", "infra"),
        ("account0", "prod", "eu-west-4", "default"),
        ("account0", "prod", "eu-west-4", "infra"),
        ("account0", "test", "eu-west-1", "default"),
        ("account0", "test", "eu-west-1", "infra"),
        ("account0", "test", "eu-west-2", "default"),
        ("account0", "test", "eu-west-2", "infra"),
        ("account0", "test", "eu-west-3", "default"),
    ]
    for i in range(len(stacks)):
        assert str(stacks[i]) == tfwrapper.get_stack_dir(wrapper_config["rootdir"], *expected_stacks[i])
    assert len(stacks) == len(expected_stacks)


def test_foreach_select_from_args_env_preprod(tmp_working_dir_multiple_stacks, multiple_stacks, default_args):  # noqa: D103
    default_args.environment = "preprod"

    wrapper_config = deepcopy(vars(default_args))
    parents_count = tfwrapper.detect_config_dir(wrapper_config)
    tfwrapper.detect_stack(wrapper_config, parents_count, raise_on_missing=False)

    stacks = [*tfwrapper.foreach_select_stacks(wrapper_config)]

    expected_stacks = [
        ("account0", "preprod", "eu-west-1", "default"),
        ("account0", "preprod", "eu-west-1", "infra"),
        ("account0", "preprod", "eu-west-2", "default"),
        ("account0", "preprod", "eu-west-2", "infra"),
        ("account1", "preprod", "eu-west-1", "default"),
        ("account1", "preprod", "eu-west-1", "infra"),
        ("account1", "preprod", "eu-west-2", "default"),
        ("account1", "preprod", "eu-west-2", "infra"),
    ]
    for i in range(len(stacks)):
        assert str(stacks[i]) == tfwrapper.get_stack_dir(wrapper_config["rootdir"], *expected_stacks[i])
    assert len(stacks) == len(expected_stacks)


def test_foreach_select_from_args_region_euw1(tmp_working_dir_multiple_stacks, multiple_stacks, default_args):  # noqa: D103
    default_args.region = "eu-west-1"

    wrapper_config = deepcopy(vars(default_args))
    parents_count = tfwrapper.detect_config_dir(wrapper_config)
    tfwrapper.detect_stack(wrapper_config, parents_count, raise_on_missing=False)

    stacks = [*tfwrapper.foreach_select_stacks(wrapper_config)]

    expected_stacks = [
        ("account0", "preprod", "eu-west-1", "default"),
        ("account0", "preprod", "eu-west-1", "infra"),
        ("account0", "prod", "eu-west-1", "default"),
        ("account0", "prod", "eu-west-1", "infra"),
        ("account0", "test", "eu-west-1", "default"),
        ("account0", "test", "eu-west-1", "infra"),
        ("account1", "preprod", "eu-west-1", "default"),
        ("account1", "preprod", "eu-west-1", "infra"),
        ("account1", "prod", "eu-west-1", "default"),
        ("account1", "prod", "eu-west-1", "infra"),
    ]
    for i in range(len(stacks)):
        assert str(stacks[i]) == tfwrapper.get_stack_dir(wrapper_config["rootdir"], *expected_stacks[i])
    assert len(stacks) == len(expected_stacks)


def test_foreach_select_from_args_stack_default(tmp_working_dir_multiple_stacks, multiple_stacks, default_args):  # noqa: D103
    default_args.stack = "default"

    wrapper_config = deepcopy(vars(default_args))
    parents_count = tfwrapper.detect_config_dir(wrapper_config)
    tfwrapper.detect_stack(wrapper_config, parents_count, raise_on_missing=False)

    stacks = [*tfwrapper.foreach_select_stacks(wrapper_config)]

    expected_stacks = [
        ("account0", "global", None, "default"),
        ("account0", "preprod", "eu-west-1", "default"),
        ("account0", "preprod", "eu-west-2", "default"),
        ("account0", "prod", "eu-west-1", "default"),
        ("account0", "prod", "eu-west-4", "default"),
        ("account0", "test", "eu-west-1", "default"),
        ("account0", "test", "eu-west-2", "default"),
        ("account0", "test", "eu-west-3", "default"),
        ("account1", "global", None, "default"),
        ("account1", "preprod", "eu-west-1", "default"),
        ("account1", "preprod", "eu-west-2", "default"),
        ("account1", "prod", "eu-west-1", "default"),
        ("account1", "prod", "eu-west-4", "default"),
    ]
    for i in range(len(stacks)):
        assert str(stacks[i]) == tfwrapper.get_stack_dir(wrapper_config["rootdir"], *expected_stacks[i])
    assert len(stacks) == len(expected_stacks)


def test_foreach_select_from_args_env_preprod_stack_default(
    tmp_working_dir_multiple_stacks, multiple_stacks, default_args
):  # noqa: D103
    default_args.environment = "preprod"
    default_args.stack = "default"

    wrapper_config = deepcopy(vars(default_args))
    parents_count = tfwrapper.detect_config_dir(wrapper_config)
    tfwrapper.detect_stack(wrapper_config, parents_count, raise_on_missing=False)

    stacks = [*tfwrapper.foreach_select_stacks(wrapper_config)]

    expected_stacks = [
        ("account0", "preprod", "eu-west-1", "default"),
        ("account0", "preprod", "eu-west-2", "default"),
        ("account1", "preprod", "eu-west-1", "default"),
        ("account1", "preprod", "eu-west-2", "default"),
    ]
    for i in range(len(stacks)):
        assert str(stacks[i]) == tfwrapper.get_stack_dir(wrapper_config["rootdir"], *expected_stacks[i])
    assert len(stacks) == len(expected_stacks)
