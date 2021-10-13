# claranet-tfwrapper

[![Changelog](https://img.shields.io/badge/changelog-release-blue.svg)](CHANGELOG.md) [![Mozilla Public License](https://img.shields.io/badge/license-mozilla-orange.svg)](LICENSE) [![Pypi](https://img.shields.io/badge/python-pypi-green.svg)](https://pypi.org/project/claranet-tfwrapper/)

`tfwrapper` is a python wrapper for [Terraform](https://www.terraform.io/) which aims to simplify Terraform usage and enforce best practices.

## Table Of Contents

<!--TOC-->

- [claranet-tfwrapper](#claranet-tfwrapper)
  - [Table Of Contents](#table-of-contents)
  - [Features](#features)
  - [Drawbacks](#drawbacks)
  - [Setup Dependencies](#setup-dependencies)
  - [Runtime Dependencies](#runtime-dependencies)
  - [Recommended setup](#recommended-setup)
  - [Installation](#installation)
  - [Upgrade from tfwrapper v7 or older](#upgrade-from-tfwrapper-v7-or-older)
    - [Required files](#required-files)
  - [Configuration](#configuration)
    - [tfwrapper configuration](#tfwrapper-configuration)
    - [Stacks configurations](#stacks-configurations)
    - [States centralization configuration](#states-centralization-configuration)
    - [How to migrate from one backend to another for state centralization](#how-to-migrate-from-one-backend-to-another-for-state-centralization)
  - [Stacks file structure](#stacks-file-structure)
  - [Usage](#usage)
    - [Stack bootstrap](#stack-bootstrap)
    - [Working on stacks](#working-on-stacks)
    - [Passing options](#passing-options)
  - [Environment](#environment)
    - [S3 state backend credentials](#s3-state-backend-credentials)
    - [Azure storage state backend credentials](#azure-storage-state-backend-credentials)
    - [Azure Service Principal credentials](#azure-service-principal-credentials)
    - [GCP configuration](#gcp-configuration)
    - [GKE configurations](#gke-configurations)
    - [Stack configurations and credentials](#stack-configurations-and-credentials)
    - [Stack path](#stack-path)
- [Development](#development)
  - [Tests](#tests)
  - [Python code formatting](#python-code-formatting)
  - [Checks](#checks)
  - [README TOC](#readme-toc)
  - [Using terraform development builds](#using-terraform-development-builds)
  - [git pre-commit hooks](#git-pre-commit-hooks)
  - [Publishing new releases to PyPI](#publishing-new-releases-to-pypi)

<!--TOC-->

## Features

- Terraform behaviour overriding
- State centralization enforcement
- Standardized file structure
- Stack initialization from templates
- AWS credentials caching
- Azure credentials loading (both Service Principal or User)
- GCP and GKE user ADC support
- Plugins caching

## Drawbacks

- AWS oriented (even if other cloud providers do work)
- Setup overhead

## Setup Dependencies

- `build-essential` (provides C/C++ compilers)
- `libffi-dev`
- `libssl-dev`
- `python3` `>= 3.6.2 <4.0` (3.8+ recommended)
- `python3-dev`
- `python3-venv`

## Runtime Dependencies

- `terraform` `>= 0.10`

## Recommended setup

- Terraform 1.0+
- An AWS S3 bucket and DynamoDB table for state centralization in AWS.
- An Azure Blob Storage container for state centralization in Azure.

## Installation

tfwrapper should installed using pipx (recommended) or pip:

```bash
pipx install claranet-tfwrapper
```

If targeting Azure, you should instead install `claranet-tfwrapper` with its `azure` extras:

```bash
pipx install claranet-tfwrapper[azure]
```

With zsh, you need to escape brackets:

```zsh
pipx install 'claranet-tfwrapper[azure]'
```

## Upgrade from tfwrapper v7 or older

If you used versions of the wrapper older than v8, there is not much to do when upgrading to v8
except a little cleanup.
Indeed, the wrapper is no longer installed as a git submodule of your project like it used to be instructed and there is no longer any `Makefile` to activate it.

Just clean up each project by destroying the `.wrapper` submodule:

```bash
git rm -f Makefile
git submodule deinit .wrapper
rm -rf .git/modules/.wrapper
git rm -f .wrapper
```

Then check the staged changes and commit them.

### Required files

tfwrapper expects multiple files and directories at the root of a project.

#### conf

Stacks configurations are stored in the `conf` directory.

#### templates

The `templates` directory is used to store the state backend configuration template and the Terraform stack templates used to initialize new stacks. Using a git submodule is recommended.

The following files are required:

- `templates/{provider}/common/state.tf.jinja2`: AWS S3 or Azure Blob Storage state backend configuration template.
- `templates/{provider}/basic/main.tf`: the default Terraform configuration for new stacks. The whole `template/{provider}/basic` directory is copied on stack initialization.

For example with AWS:

```bash
mkdir -p templates/aws/common templates/aws/basic

# create state configuration template with AWS backend
cat << 'EOF' > templates/aws/common/state.tf.jinja2
{% if region is not none %}
{% set region = '/' + region + '/' %}
{% else %}
{% set region = '/' %}
{% endif %}

terraform {
  backend "s3" {
    bucket = "my-centralized-terraform-states-bucket"
    key    = "{{ client_name }}/{{ account }}/{{ environment }}{{ region }}{{ stack }}/terraform.state"
    region = "eu-west-1"

    lock_table = "my-terraform-states-lock-table"
  }
}

resource "null_resource" "state-test" {}
EOF

# create a default stack templates with support for AWS assume role
cat << 'EOF' > templates/aws/basic/main.tf
provider "aws" {
  region     = "${var.aws_region}"
  access_key = "${var.aws_access_key}"
  secret_key = "${var.aws_secret_key}"
  token      = "${var.aws_token}"
}
EOF
```

For example with Azure:

```bash
mkdir -p templates/azure/common templates/azure/basic

# create state configuration template with Azure backend
cat << 'EOF' > templates/azure/common/state.tf.jinja2
{% if region is not none %}
{% set region = '/' + region + '/' %}
{% else %}
{% set region = '/' %}
{% endif %}

terraform {
  backend "azurerm" {
    storage_account_name = "my-centralized-terraform-states-account"
    container_name       = "terraform-states"

    key = "{{ client_name }}/{{ account }}/{{ environment }}{{ region }}{{ stack }}/terraform.state"
  }
}
EOF

# create a default stack templates with support for Azure credentials
cat << 'EOF' > templates/azure/basic/main.tf
provider "azurerm" {
  subscription_id = "${var.azure_subscription_id}"
  tenant_id       = "${var.azure_tenant_id}"
}
EOF
```

#### .run

The `.run` directory is used for credentials caching and plan storage.

```bash
mkdir .run
cat << 'EOF' > .run/.gitignore
*
!.gitignore
EOF
```

#### .gitignore

Adding the following `.gitignore` at the root of your project is recommended:

```bash
cat << 'EOF' > .gitignore
*/**/terraform.tfstate
*/**/terraform.tfstate.backup
*/**/terraform.tfvars
*/**/.terraform/modules
*/**/.terraform/plugins
EOF
```

## Configuration

tfwrapper uses yaml files stored in the `conf` directory of the project.

### tfwrapper configuration

tfwrapper uses some default behaviors that can be overridden or modified via a `config.yml` file in the `conf` directory.

```yaml
---
install_azure_dependencies: True # Install all needed Azure dependencies in the loaded shell (azure-cli, azure python SDK)
always_trigger_init: False # Always trigger `terraform init` first when launching `plan` or `apply` commands
pipe_plan_command: "cat" # Default command used when you're invoking tfwrapper with `--pipe-plan`
use_local_azure_session_directory: False # Use the current user's Azure configuration in `~/.azure`. By default, the wrapper stores `azure-cli` session and configuration in the local `.run` directory.
```

### Stacks configurations

Stacks configuration files use the following naming convention:

```bash
conf/${account}_${environment}_${region}_${stack}.yml
```

Here is an example for an AWS stack configuration:

```yaml
---
state_configuration_name: "aws" # use "aws" backend state configuration
aws:
  general:
    account: &aws_account "xxxxxxxxxxx" # aws account for this stack
    region: &aws_region eu-west-1 # aws region for this stack
  credentials:
    profile: my-aws-profile # should be configured in .aws/config

terraform:
  vars: # variables passed to terraform
    aws_account: *aws_account
    aws_region: *aws_region
    client_name: my-client-name # arbitrary client name
```

Here is an example for a stack on Azure configuration using user mode and AWS S3 backend for state storage:

```yaml
---
state_configuration_name: "aws-demo" # use "aws" backend state configuration
azure:
  general:
    mode: user # Uses personal credentials with MFA
    directory_id: &directory_id "aaaaaaaa-bbbb-cccc-dddd-zzzzzzzzzzzz" # Azure Tenant/Directory UID
    subscription_id: &subscription_id "aaaaaaaa-bbbb-cccc-dddd-zzzzzzzzzzzz" # Azure Subscription UID

terraform:
  vars:
    subscription_id: *subscription_id
    directory_id: *directory_id
    client_name: client-name #Replace it with the name of your client
    #version: "0.10"  # Terraform version like "0.10" or "0.10.5" - optional
```

It is using your account linked to a Microsoft Account. You must have access to the Azure Subscription if you want to use Terraform.

Here is an example for a stack on Azure configuration using Service Principal mode:

```yaml
---
azure:
  general:
    mode: service_principal # Uses an Azure tenant Service Principal account
    directory_id: &directory_id "aaaaaaaa-bbbb-cccc-dddd-zzzzzzzzzzzz" # Azure Tenant/Directory UID
    subscription_id: &subscription_id "aaaaaaaa-bbbb-cccc-dddd-zzzzzzzzzzzz" # Azure Subscription UID

  credential:
    profile: azurerm-account-profile # To stay coherent, create an AzureRM profile with the same name than the account-alias. Please checkout `azurerm_config.yml.sample` file for configuration structure.

terraform:
  vars:
    subscription_id: *subscription_id
    directory_id: *directory_id
    client_name: client-name # Replace it with the name of your client
    #version: "0.10"  # Terraform version like "0.10" or "0.10.5" - optional
```

It is using the Service Principal's credentials to connect the Azure Subscription. This SP must have access to the subscription.
The wrapper loads client_id and client_secret from your `config.yml` located in `~/.azurem/config.yml`.
Please check the example here: [https://git.fr.clara.net/claranet/cloudnative/projects/terraform/base-template/tree/master/conf](https://git.fr.clara.net/claranet/cloudnative/projects/terraform/base-template/tree/master/conf)

Here is an example for a GCP/GKE stack with user ADC and multiple GKE instances:

```yaml
---
gcp:
  general:
    mode: adc-user
    project: &gcp_project project-name
  gke:
    - name: kubernetes-1
      zone: europe-west1-c
    - name: kubernetes-2
      region: europe-west1

terraform:
  vars:
    gcp_region: europe-west1
    gcp_zone: europe-west1-c
    gcp_project: *gcp_project
    client_name: client-name
    #version: "0.11"  # Terraform version like "0.10" or "0.10.5" - optional
```

### States centralization configuration

The `conf/state.yml` configuration file defines the configurations used to connect to state backend account.
It can be an AWS (S3) or Azure (Storage Account) backend type.

You can use other backends (e.g. Google GCS or Hashicorp Consul) not specifically supported by the wrapper if you them manage yourself and omit the `conf/state.yml` file or make it empty:

```yaml
---
```

Example configuration with both AWS and Azure backends defined:

```yaml
---
aws:
  name: "aws-demo"
  general:
    account: "xxxxxxxxxxx"
    region: eu-west-1
  credentials:
    profile: my-state-aws-profile # should be configured in .aws/config

azure:
  name: "azure-alternative"
  general:
    subscription_uid: "xxxxxxx" # the Azure account to use for state storage
    resource_group_name: "tfstates-xxxxx-rg" # The Azure resource group with state storage
    storage_account_name: "tfstatesxxxxx"

backend_parameters: # Parameters or options which can be used by `state.j2.tf` template file
  state_snaphot: "false" # Example of Azure storage backend option
```

Note: the first backend will be the default one for stacks not defining `state_backend_type`.

### How to migrate from one backend to another for state centralization

If for example you have both an AWS and Azure state backend configured in your `conf/state.yml` file,
you can migrate your stack state from one backend to another.

Here is a quick howto:

1. Make sure your stack is clean:

```bash
$ cd account/path/env/your_stack
$ tfwrapper init
$ tfwrapper plan
# should return no changes
```

2. Change your backend in the stack configuration yaml file:

```yaml
---
#state_configuration_name: 'aws-demo' # previous backend
state_configuration_name: "azure-alternative" # new backend to use
```

3. Back in your stack directory, you can perform the change:

```bash
$ cd account/path/env/your_stack
$ rm -v state.tf # removing old state backend configuration
$ tfwrapper bootstrap # regen a new state backend configuration based on the stack yaml config file
$ tfwrapper init # Terraform will detect the new backend and propose to migrate it
$ tfwrapper plan
# should return the same changes diff as before
```

## Stacks file structure

Terraform stacks are organized based on their:

- account: an account alias which may reference one or multiple providers accounts. `aws-production`, `azure-dev`, etc…
- environment: `production`, `preproduction`, `dev`, etc…
- region: `eu-west-1`, `westeurope`, `global`, etc…
- stack: defaults to `default`. `web`, `admin`, `tools`, etc…

The following file structure is enforced:

```
# enforced file structure
└── account
    └── environment
        └── region
            └── stack

# real-life example
├── aws-account-1
│   └── production
│       ├── eu-central-1
│       │   └── web
│       │       └── main.tf
│       └── eu-west-1
│           ├── default
│           │   └── main.t
│           └── tools
│               └── main.tf
└── aws-account-2
    └── backup
        └── eu-west-1
            └── backup
                └── main.tf
```

## Usage

### Stack bootstrap

After creating a `conf/${account}_${environment}_${region}_${stack}.yml` stack configuration file you can bootstrap it.

```bash
# you can bootstrap using the templates/{provider}/basic stack
tfwrapper -a ${account} -e ${environment} -r ${region} -s ${stack} bootstrap

# or another stack template, for example: templates/aws/foobar
tfwrapper -a ${account} -e ${environment} -r ${region} -s ${stack} bootstrap aws/foobar
```

### Working on stacks

You can work on stacks from their directory or from the root of the project.

```bash
# working from the root of the project
tfwrapper -a ${account} -e ${environment} -r ${region} -s ${stack} plan

# working from the root of a stack
cd ${account}/${environment}/${region}/${stack}
tfwrapper plan
```

You can also work on several stacks sequentially with the `foreach` subcommand from any directory under the root of the project.
By default, `foreach` selects all stacks under the current directory,
so if called from the root of the project without any filter,
it will select all stacks and execute the specified command in them, one after another:

```bash
# working from the root of the project
tfwrapper foreach -- tfwrapper init
```

Any combination of the `-a`, `-e`, `-r` and `-s` arguments can be used to select specific stacks,
e.g. all stacks for an account across all environments but in a specific region:

```bash
# working from the root of the project
tfwrapper -a ${account} -r ${region} foreach -- tfwrapper plan
```

The same can be achieved with:

```bash
# working from an account directory
cd ${account}
tfwrapper -r ${region} foreach -- tfwrapper plan
```

Complex commands can be executed in a sub-shell with the `-c` argument, e.g.:

```bash
# working from an environment directory
cd ${account}/${environment}
tfwrapper foreach -c 'pwd && tfwrapper init >/dev/null 2>&1 && tfwrapper plan 2>/dev/null -- -no-color | grep "^Plan: "'
```

### Passing options

You can pass anything you want to `terraform` using `--`.

```bash
tfwrapper plan -- -target resource1 -target resource2
```

## Environment

tfwrapper sets the following environment variables.

### S3 state backend credentials

The default AWS credentials of the environment are set to point to the S3 state backend. Those credentials are acquired from the profile defined in `conf/state.yml`

- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_SESSION_TOKEN`

### Azure storage state backend credentials

When using Azure storage (container blob), needed credentials are set in the environment. Those credentials are acquired from the profile defined in `conf/state.yml`

- `ARM_ACCESS_KEY`

### Azure Service Principal credentials

Those AzureRM credentials are loaded only if you are using the Service Principal mode. They are acquired from the profile defined in `~/.azurerm/config.yml`

- `ARM_CLIENT_ID`
- `ARM_CLIENT_SECRET`

### GCP configuration

Those GCP related variables are available from the environment when using the example configuration:

- `TF_VAR_gcp_region`
- `TF_VAR_gcp_gcp_zone`
- `TF_VAR_gcp_gcp_project`

### GKE configurations

Each GKE instance has its own kubeconfig, the path to each configuration is available from the environment:

- `TF_VAR_gke_kubeconfig_${gke_cluster_name}`

kubeconfig is automatically fetched by the wrapper (using gcloud) and stored inside the `.run` directory of your project.
It is refreshed automatically at every run to ensure you point to correct Kubernetes endpoint.
You can disable this behaviour by setting `refresh_kubeconfig: never` in your cluster settings.

```yaml
---
gcp:
  general:
    mode: adc-user
    project: &gcp_project project-name
  gke:
    - name: kubernetes-1
      zone: europe-west1-c
      refresh_kubeconfig: never
```

### Stack configurations and credentials

The `terraform['vars']` dictionary from the stack configuration is accessible as Terraform variables.

The profile defined in the stack configuration is used to acquire credentials accessible from Terraform.
There is two supported providers, the variables which will be loaded depends on the used provider.

- `TF_VAR_client_name`
- `TF_VAR_aws_account`
- `TF_VAR_aws_region`
- `TF_VAR_aws_access_key`
- `TF_VAR_aws_secret_key`
- `TF_VAR_aws_token`
- `TF_VAR_azurerm_region`
- `TF_VAR_azure_region`
- `TF_VAR_azure_subscription_id`
- `TF_VAR_azure_tenant_id`
- `TF_VAR_azure_state_access_key`

### Stack path

The stack path is passed to Terraform. This is especially useful for resource naming and tagging.

- `TF_VAR_account`
- `TF_VAR_environment`
- `TF_VAR_region`
- `TF_VAR_stack`

# Development

## Tests

All new code contributions should come with unit and/or integrations tests.

To run those tests locally, use [tox](https://github.com/tox-dev/tox).

## Python code formatting

Our code is formatted with [black](https://github.com/psf/black/).

Make sure to format all your code contributions with `black ${filename}`.

Hint: enable auto-format on save with `black` in your [favorite IDE](https://black.readthedocs.io/en/stable/editor_integration.html).

## Checks

To run code and documentation style checks, run `tox -e lint`.

In addition to `black --check`, code is also checked with:

- [flake8](https://gitlab.com/pycqa/flake8), a wrapper for [pycodestyle](https://github.com/PyCQA/pycodestyle) and [pyflakes](https://github.com/PyCQA/pyflakes).
- [flake8-docstrings](https://gitlab.com/pycqa/flake8-docstrings), a wrapper for [pydocstyle](https://github.com/PyCQA/pydocstyle).

## README TOC

This [README's table of content](#table-of-contents) is formatted with [md_toc](https://github.com/frnmst/md-toc).

Keep in mind to update it with `md_toc --in-place github README.md`.

## Using terraform development builds

To build and use development versions of terraform, manually put them in a `~/.terraform.d/versions/X.Y/X.Y.Z-dev/` folder:

```bash
# cd ~/go/src/github.com/hashicorp/terraform
# make XC_ARCH=amd64 XC_OS=linux bin
# ./bin/terraform version
Terraform v0.12.9-dev
# mkdir -p ~/.terraform.d/versions/0.12/0.12.9-dev
# mv ./bin/terraform ~/.terraform.d/versions/0.12/0.12.9-dev/
```

## git pre-commit hooks

Some git pre-commit hooks are configured in `.pre-commit-config.yaml` for use with the [pre-commit tool](https://pre-commit.com).

Using them helps avoiding to push changes that will fail the CI.

They can be installed locally with:

```bash
# pre-commit install
```

If updating hooks configuration, run checks against all files to make sure everything is fine:

```bash
# pre-commit run --all-files --show-diff-on-failure
```

Note: the `pre-commit` tool itself can be installed with `pip` or `pipx`.

## Publishing new releases to PyPI

Bump the version with poetry:

```bash
# poetry version [patch|minor|major|prepatch|preminor|premajor|prerelease]
```

Commit, tag and push this change to Github, then publish the release to test.pypi.org for validation:

```bash
# poetry config repositories.testpypi https://test.pypi.org/legacy/
# poetry publish --build --repository testpypi
```

If all is ok, publish to pypi.org:

```bash
# poetry publish --build
```

Bump the version with poetry again in master to mark it for development:

```bash
# poetry version prerelease
```

TODO: automate this process with Github Actions
