# tfwrapper

tfwrapper is a python wrapper for [Terraform](https://www.terraform.io/) which aims to simplify Terraform usage and enforce best practices.

## Features

- Terraform behaviour overriding
- State centralization enforcement
- Standardized file structure
- Stack initialization from templates
- AWS credentials caching
- Plugins caching

## Drawbacks

- AWS oriented (even if other providers do work)
- Setup overhead

## Dependencies

- Make
- Python `>= 3.5`
- python-pip
- python-virtualenv
- Terraform `>= 0.10`
- An AWS S3 bucket and DynamoDB table for state centralization.

## Installation

tfwrapper should be deployed as a git submodule in Terraform projects.

```bash
cd my_terraform_project
git submodule add git@github.com:claranet/terraform-wrapper.git .wrapper
```

If you plan to use tfwrapper for multiple projects, creating a new git repository including all the required files and tfwrapper as a git submodule is recommended. You then just need to clone this repository to start new projects.

### Required files

tfwrapper expects multiple files and directories at the root of its parent project.

#### Makefile

A `Makefile` symlink should point to tfwrapper's `Makefile`. this link allows users to setup and enable tfwrapper from the root of their project.

```bash
ln -s .wrapper/Makefile
```

#### conf

Stacks configurations are stored in the `conf` directory.

#### templates

The `templates` directory is used to store the state backend configuration template and the Terraform stack templates used to initialize new stack. Using a git submodule is recommended.

The following files are required :

- `templates/common/state.tf.jinja2` : S3 state backend configuration template.
- `templates/basic/main.tf` : the default Terraform configuration for new stacks. The whole `template/basic` directory is copied on stack initialization.

For example :

```bash
mkdir -p templates/common templates/basic

# create state configuration template
cat << EOF > templates/common/state.tf.jinja2
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
cat << EOF > templates/basic/main.tf
provider "aws" {
  region     = "${var.aws_region}"
  access_key = "${var.aws_access_key}"
  secret_key = "${var.aws_secret_key}"
  token      = "${var.aws_token}"
}
EOF
```

#### .run

The `.run` directory is used for credentials caching and plan storage.

```bash
mkdir .run
cat << EOF > .run/.gitignore
*
!.gitignore
EOF
```

#### .gitignore

Adding the following `.gitignore` at the root of your project is recommended :

```bash
cat << EOF > .gitignore
*/**/terraform.tfstate
*/**/terraform.tfstate.backup
*/**/terraform.tfvars
*/**/.terraform/modules
*/**/.terraform/plugins
EOF
```

## Configuration

tfwrapper uses yaml files stored in the `conf` directory of the project.

### Stacks configurations

Stacks configuration files use the following naming convention :

```bash
conf/${account}_${environment}_${region}_${stack}.yml
```

Here is an example stack configuration :

```yaml
---
aws:
  general:
    account: &aws_account 'xxxxxxxxxxx' # aws account for this stack
    region: &aws_region eu-west-1       # aws region for this stack
  credentials:
    profile: my-aws-profile         # should be configured in .aws/config

terraform:
  vars:                         # variables passed to terraform
    aws_account: *aws_account
    aws_region: *aws_region
    client_name: my-client-name # arbitrary client name  
```

### States centralization configuration

`conf/state.yml` defines the configuration used to connect to the S3 state backend's AWS account.

```yaml
---
aws:
  general:
    account: 'xxxxxxxxxxx'
    region: eu-west-1
  credentials:
    profile: my-state-aws-profile # should be configured in .aws/config
```

## Stacks file structure

Terraform stacks are organized based on their :

- account : an account alias which may reference one or multiple providers accounts. `aws-production`, `azure-dev`, etc…
- environment : `production`, `preproduction`, `dev`, etc…
- region : `eu-west-1`, `westeurope`, `global`, etc…
- stack : defaults to `default`. `web`, `admin`, `tools`, etc…

The following file structure is enforced :

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

### tfwrapper activation

```bash
# this will initialize a virtualenv and update your PATH in a new instance of your current SHELL
make
tfwrapper -h

# when you are done using the tfwrapper you can leave the virtualenv
exit
```

### Stack bootstrap

After creating a `conf/${account}_${environment}_${region}_${stack}.yml` stack configuration file you c bootstrap it.

```bash
# you can bootstrap using the templates/basic stack
tfwrapper -a ${account} -e ${environment} -r ${region} -s ${stack} bootstrap

# or another stack template, for example : templates/foobar
tfwrapper -a ${account} -e ${environment} -r ${region} -s ${stack} bootstrap foobar
```

### Working on a stack

You can work on stacks from theirs root or from the root of the project.

```bash
# working from the root of the project
tfwrapper -a ${account} -e ${environment} -r ${region} -s ${stack} plan

# working from the root of a stack
cd ${account}/${environment}/${region}/${stack}
tfwrapper plan
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

### Stack configurations and credentials

The `terraform['vars']` dictionary from the stack configuration is accessible as Terraform variables.

The profile defined in the stack configuration is used to acquire credentials accessible from Terraform.

- `TF_VAR_aws_account`
- `TF_VAR_aws_region`
- `TF_VAR_client_name`
- `TF_VAR_aws_access_key`
- `TF_VAR_aws_secret_key`
- `TF_VAR_aws_token`

### Stack path

The stack path is passed to Terraform. This is especially useful for resource naming and tagging.

- `TF_VAR_account`
- `TF_VAR_environment`
- `TF_VAR_region`
- `TF_VAR_stack`
