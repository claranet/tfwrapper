"""Test foreach command behavior."""

import os
import textwrap

import pytest

import claranet_tfwrapper as tfwrapper


def test_bootstrap_from_stack_dir_without_stack_config_nor_stack_directory_nor_state_config_nor_template(
    tmp_working_dir_regional, default_args, caplog
):
    paths = tmp_working_dir_regional
    os.chdir(paths["stack_dir"])

    with pytest.raises(SystemExit) as e:
        tfwrapper.main(
            [
                "bootstrap",
            ]
        )

    assert e.type is SystemExit
    assert e.value.code == 1
    assert (
        "A valid stack configuration file ../../../../conf/testaccount_testenvironment_testregion_teststack.yml"
        " is required for bootstrap subcommand, aborting." in caplog.text
    )


def test_bootstrap_from_stack_dir_with_stack_config_but_no_state_config_nor_template(
    tmp_working_dir_regional, default_args, caplog
):
    paths = tmp_working_dir_regional
    os.chdir(paths["stack_dir"])
    stack_conf = paths["conf_dir"] / "testaccount_testenvironment_testregion_teststack.yml"
    stack_conf.write_text(
        textwrap.dedent(
            """
            ---
            terraform:
                vars:
                    client_name: testclient
            """
        )
    )

    with pytest.raises(SystemExit) as e:
        tfwrapper.main(
            [
                "bootstrap",
            ]
        )

    assert e.type is SystemExit
    assert e.value.code == 0
    assert "No template specified and no cloud provider defined in configuration, skipping." in caplog.text
    assert "No state backend configuration found, skipping state configuration file state.tf generation." in caplog.text
    stack_dir = paths["working_dir"] / "testaccount" / "testenvironment" / "testregion" / "teststack"
    assert os.path.isdir(stack_dir)
    assert len(os.listdir(stack_dir)) == 0


def test_bootstrap_from_stack_dir_with_stack_config_and_template_but_no_state_config(
    tmp_working_dir_regional, default_args, caplog
):
    paths = tmp_working_dir_regional
    os.chdir(paths["stack_dir"])

    stack_conf = paths["conf_dir"] / "testaccount_testenvironment_testregion_teststack.yml"
    stack_conf.write_text(
        textwrap.dedent(
            """
            ---
            aws:
                general:
                    account: &aws_account "123456789012"
                    region: &aws_region eu-west-3
                credentials:
                    profile: &aws_account_alias testaccount

            terraform:
                vars:
                    aws_account: *aws_account
                    aws_account_alias: *aws_account_alias
                    aws_region: *aws_region
                    client_name: testclient
                    version: "1.1.7"
            """
        )
    )
    aws_templates_dir = paths["working_dir"] / "templates" / "aws"
    aws_basic_template_dir = aws_templates_dir / "basic"
    aws_common_template_dir = aws_templates_dir / "common"
    aws_basic_template_dir.mkdir(parents=True)
    aws_basic_tf = aws_basic_template_dir / "terraform.tf"
    aws_basic_tf.write_text(
        textwrap.dedent(
            """
            terraform {
                required_version = "~> 1.0"
            }
            """
        )
    )

    aws_common_template_dir.mkdir(parents=True)
    state_tf_jinja2 = aws_common_template_dir / "state.tf.jinja2"
    state_tf_jinja2.write_text(
        textwrap.dedent(
            """
            {% if region is not none %}
            {% set region = '/' + region + '/' %}
            {% else %}
            {% set region = '/' %}
            {% endif %}

            terraform {
                backend "s3" {
                    bucket = "mybucket"
                    key    = "{{ client_name }}/{{ account }}/{{ environment }}{{ region }}{{ stack }}/terraform.state"
                    region = "eu-west-1"

                    dynamodb_table = "terraform-states-lock"
                }
            }
            """
        )
    )

    with pytest.raises(SystemExit) as e:
        tfwrapper.main(
            [
                "-d",
                "bootstrap",
                "aws/basic",
            ]
        )

    assert e.type is SystemExit
    assert e.value.code == 0
    assert "Bootstrapped stack using template aws/basic." in caplog.text
    assert "No state backend configuration found, skipping state configuration file state.tf generation." in caplog.text
    stack_dir = paths["working_dir"] / "testaccount" / "testenvironment" / "testregion" / "teststack"
    assert os.path.isdir(stack_dir)
    assert len(os.listdir(stack_dir)) == 1
    assert not os.path.exists(stack_dir / "state.tf")
    assert os.path.exists(stack_dir / "terraform.tf")


def test_bootstrap_from_stack_dir_with_stack_config_and_state_config_and_template(tmp_working_dir_regional, default_args, caplog):
    paths = tmp_working_dir_regional
    os.chdir(paths["stack_dir"])

    state_conf = paths["conf_dir"] / "state.yml"
    state_conf.write_text(
        textwrap.dedent(
            """
            ---
            aws:
                general:
                    account: '123456789012'
                    region: eu-west-1
                credentials:
                    profile: stateaccount
            """
        )
    )
    stack_conf = paths["conf_dir"] / "testaccount_testenvironment_testregion_teststack.yml"
    stack_conf.write_text(
        textwrap.dedent(
            """
            ---
            aws:
                general:
                    account: &aws_account "123456789012"
                    region: &aws_region eu-west-3
                credentials:
                    profile: &aws_account_alias testaccount

            terraform:
                vars:
                    aws_account: *aws_account
                    aws_account_alias: *aws_account_alias
                    aws_region: *aws_region
                    client_name: testclient
                    version: "1.1.7"
            """
        )
    )
    aws_templates_dir = paths["working_dir"] / "templates" / "aws"
    aws_basic_template_dir = aws_templates_dir / "basic"
    aws_common_template_dir = aws_templates_dir / "common"
    aws_basic_template_dir.mkdir(parents=True)
    aws_basic_tf = aws_basic_template_dir / "terraform.tf"
    aws_basic_tf.write_text(
        textwrap.dedent(
            """
            terraform {
                required_version = "~> 1.0"
            }
            """
        )
    )

    aws_common_template_dir.mkdir(parents=True)
    state_tf_jinja2 = aws_common_template_dir / "state.tf.jinja2"
    state_tf_jinja2.write_text(
        textwrap.dedent(
            """
            {% if region is not none %}
            {% set region = '/' + region + '/' %}
            {% else %}
            {% set region = '/' %}
            {% endif %}

            terraform {
                backend "s3" {
                    bucket = "mybucket"
                    key    = "{{ client_name }}/{{ account }}/{{ environment }}{{ region }}{{ stack }}/terraform.state"
                    region = "eu-west-1"

                    dynamodb_table = "terraform-states-lock"
                }
            }
            """
        )
    )

    with pytest.raises(SystemExit) as e:
        tfwrapper.main(
            [
                "bootstrap",
                "aws/basic",
            ]
        )

    assert e.type is SystemExit
    assert e.value.code == 0
    assert "Bootstrapped stack using template aws/basic." in caplog.text
    assert 'Generated state.tf file with "aws" backend type configured.' in caplog.text
    stack_dir = paths["working_dir"] / "testaccount" / "testenvironment" / "testregion" / "teststack"
    assert os.path.isdir(stack_dir)
    assert len(os.listdir(stack_dir)) == 2
    assert os.path.exists(stack_dir / "state.tf")
    assert (stack_dir / "state.tf").read_text() == textwrap.dedent(
        """

        terraform {
            backend "s3" {
                bucket = "mybucket"
                key    = "testclient/testaccount/testenvironment/testregion/teststack/terraform.state"
                region = "eu-west-1"

                dynamodb_table = "terraform-states-lock"
            }
        }"""
    )
    assert os.path.exists(stack_dir / "terraform.tf")


def test_bootstrap_from_stack_dir_with_stack_config_and_state_config_and_empty_stack_directory_and_template(
    tmp_working_dir_regional, default_args, caplog
):
    paths = tmp_working_dir_regional
    os.chdir(paths["stack_dir"])

    state_conf = paths["conf_dir"] / "state.yml"
    state_conf.write_text(
        textwrap.dedent(
            """
            ---
            aws:
                general:
                    account: '123456789012'
                    region: eu-west-1
                credentials:
                    profile: stateaccount
            """
        )
    )
    stack_conf = paths["conf_dir"] / "testaccount_testenvironment_testregion_teststack.yml"
    stack_conf.write_text(
        textwrap.dedent(
            """
            ---
            aws:
                general:
                    account: &aws_account "123456789012"
                    region: &aws_region eu-west-3
                credentials:
                    profile: &aws_account_alias testaccount

            terraform:
                vars:
                    aws_account: *aws_account
                    aws_account_alias: *aws_account_alias
                    aws_region: *aws_region
                    client_name: testclient
                    version: "1.1.7"
            """
        )
    )
    aws_templates_dir = paths["working_dir"] / "templates" / "aws"
    aws_basic_template_dir = aws_templates_dir / "basic"
    aws_common_template_dir = aws_templates_dir / "common"
    aws_basic_template_dir.mkdir(parents=True)
    aws_basic_tf = aws_basic_template_dir / "terraform.tf"
    aws_basic_tf.write_text(
        textwrap.dedent(
            """
            terraform {
                required_version = "~> 1.0"
            }
            """
        )
    )

    aws_common_template_dir.mkdir(parents=True)
    state_tf_jinja2 = aws_common_template_dir / "state.tf.jinja2"
    state_tf_jinja2.write_text(
        textwrap.dedent(
            """
            {% if region is not none %}
            {% set region = '/' + region + '/' %}
            {% else %}
            {% set region = '/' %}
            {% endif %}

            terraform {
                backend "s3" {
                    bucket = "mybucket"
                    key    = "{{ client_name }}/{{ account }}/{{ environment }}{{ region }}{{ stack }}/terraform.state"
                    region = "eu-west-1"

                    dynamodb_table = "terraform-states-lock"
                }
            }
            """
        )
    )

    with pytest.raises(SystemExit) as e:
        tfwrapper.main(
            [
                "bootstrap",
                "aws/basic",
            ]
        )

    assert e.type is SystemExit
    assert e.value.code == 0
    assert "Bootstrapped stack using template aws/basic." in caplog.text
    assert 'Generated state.tf file with "aws" backend type configured.' in caplog.text
    assert len(os.listdir(paths["stack_dir"])) == 2
    assert os.path.exists(paths["stack_dir"] / "state.tf")
    assert (paths["stack_dir"] / "state.tf").read_text() == textwrap.dedent(
        """

        terraform {
            backend "s3" {
                bucket = "mybucket"
                key    = "testclient/testaccount/testenvironment/testregion/teststack/terraform.state"
                region = "eu-west-1"

                dynamodb_table = "terraform-states-lock"
            }
        }"""
    )
    assert os.path.exists(paths["stack_dir"] / "terraform.tf")


def test_bootstrap_from_stack_dir_with_stack_config_and_non_empty_stack_directory_and_template_but_no_stack_tf(
    tmp_working_dir_regional, default_args, caplog
):
    paths = tmp_working_dir_regional
    os.chdir(paths["stack_dir"])

    state_conf = paths["conf_dir"] / "state.yml"
    state_conf.write_text(
        textwrap.dedent(
            """
            ---
            aws:
                general:
                    account: '123456789012'
                    region: eu-west-1
                credentials:
                    profile: stateaccount
            """
        )
    )
    stack_conf = paths["conf_dir"] / "testaccount_testenvironment_testregion_teststack.yml"
    stack_conf.write_text(
        textwrap.dedent(
            """
            ---
            aws:
                general:
                    account: &aws_account "123456789012"
                    region: &aws_region eu-west-3
                credentials:
                    profile: &aws_account_alias testaccount

            terraform:
                vars:
                    aws_account: *aws_account
                    aws_account_alias: *aws_account_alias
                    aws_region: *aws_region
                    client_name: testclient
                    version: "1.1.7"
            """
        )
    )
    aws_templates_dir = paths["working_dir"] / "templates" / "aws"
    aws_basic_template_dir = aws_templates_dir / "basic"
    aws_common_template_dir = aws_templates_dir / "common"
    aws_basic_template_dir.mkdir(parents=True)
    aws_basic_tf = aws_basic_template_dir / "terraform.tf"
    aws_basic_tf.write_text(
        textwrap.dedent(
            """
            terraform {
                required_version = "~> 1.0"
            }
            """
        )
    )
    already_existing_file = paths["stack_dir"] / "already_existing_file.tf"
    already_existing_file.write_text(
        textwrap.dedent(
            """

            """
        )
    )

    aws_common_template_dir.mkdir(parents=True)
    state_tf_jinja2 = aws_common_template_dir / "state.tf.jinja2"
    state_tf_jinja2.write_text(
        textwrap.dedent(
            """
            {% if region is not none %}
            {% set region = '/' + region + '/' %}
            {% else %}
            {% set region = '/' %}
            {% endif %}

            terraform {
                backend "s3" {
                    bucket = "mybucket"
                    key    = "{{ client_name }}/{{ account }}/{{ environment }}{{ region }}{{ stack }}/terraform.state"
                    region = "eu-west-1"

                    dynamodb_table = "terraform-states-lock"
                }
            }
            """
        )
    )

    with pytest.raises(SystemExit) as e:
        tfwrapper.main(
            [
                "bootstrap",
                "aws/basic",
            ]
        )

    assert e.type is SystemExit
    assert e.value.code == 0
    assert (
        f"Stack path {paths['stack_dir']} already exists and is not empty, skipping stack bootstrapping from template."
        in caplog.text
    )
    assert 'Generated state.tf file with "aws" backend type configured.' in caplog.text
    assert len(os.listdir(paths["stack_dir"])) == 2
    assert os.path.exists(paths["stack_dir"] / "state.tf")
    assert (paths["stack_dir"] / "state.tf").read_text() == textwrap.dedent(
        """

        terraform {
            backend "s3" {
                bucket = "mybucket"
                key    = "testclient/testaccount/testenvironment/testregion/teststack/terraform.state"
                region = "eu-west-1"

                dynamodb_table = "terraform-states-lock"
            }
        }"""
    )
    assert os.path.exists(paths["stack_dir"] / "already_existing_file.tf")
