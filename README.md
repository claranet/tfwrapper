# tfwrapper

tfwrapper is a python wrapper for [Terraform](https://www.terraform.io/) which aims to simplify Terraform usage and enforce best practices.

## Features

- Terraform behaviour overriding
- State centralization enforcement
- Standardized file structure
- Stack initialization from templates
- AWS credentials caching
- Azure credentials loading
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
cat << 'EOF' > templates/common/state.tf.jinja2
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
cat << 'EOF' > templates/basic/main.tf
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
cat << 'EOF' > .run/.gitignore
*
!.gitignore
EOF
```

#### .gitignore

Adding the following `.gitignore` at the root of your project is recommended :

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

### Stacks configurations

Stacks configuration files use the following naming convention :

```bash
conf/${account}_${environment}_${region}_${stack}.yml
```

Here is an example for an AWS stack configuration:

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

Here is an example for an Azure stack configuration using user mode:

```yaml
---
azure:
  general:
    mode: user # Uses Claranet personal credentials with MFA
    directory_id: &directory_id 'aaaaaaaa-bbbb-cccc-dddd-zzzzzzzzzzzz' # Azure Tenant/Directory UID
    subscription_id: &subscription_id 'aaaaaaaa-bbbb-cccc-dddd-zzzzzzzzzzzz' # Azure Subscription UID

terraform:
  vars:
    subscription_id: *subscription_id
    directory_id: *directory_id
    client_name: client-name #Replace it with the name of your client
    #version: "0.10"  # Terraform version like "0.10" or "0.10.5" - optional
```

It is using your Claranet account linked to a Microsoft Account. You must have access to the Azure Subscription if you want to use Terraform.

Here is an example for an Azure stack configuration using Service Principal mode:

```yaml
---
azure:
  general:
    mode: service_principal # Uses a Azure tenant Service Principal account
    directory_id: &directory_id 'aaaaaaaa-bbbb-cccc-dddd-zzzzzzzzzzzz' # Azure Tenant/Directory UID
    subscription_id: &subscription_id 'aaaaaaaa-bbbb-cccc-dddd-zzzzzzzzzzzz' # Azure Subscription UID

  credential:
    profile: azurerm-account-profile # To stay coherent, create an AzureRM profile with the same name than the account-alias. Please checkout `azurerm_config.yml.sample` file for configuration structure.

terraform:
  vars:
    subscription_id: *subscription_id
    directory_id: *directory_id
    client_name: client-name #Replace it with the name of your client
    #version: "0.10"  # Terraform version like "0.10" or "0.10.5" - optional
```

It is using the Service Principal's credentials to connect the Azure Subscription. This SP must have access to the subscription.
The wrapper loads client_id and client_secret from your `azurerm_config.yml` located in `~/.azurem/config.yml`.
Please check the example here: [https://bitbucket.org/morea/terraform.base_template/src//conf/?at=master](https://bitbucket.org/morea/terraform.base_template/src//conf/?at=master)

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

### Azure Service Principal credentials

Those AzureRM credentials are loaded only if you are using the Service Principal mode. They are acquired from the profile defined in `~/.azurerm/config.yml`

- `ARM_CLIENT_ID`
- `ARM_CLIENT_SECRET`

### Stack configurations and credentials

The `terraform['vars']` dictionary from the stack configuration is accessible as Terraform variables.

The profile defined in the stack configuration is used to acquire credentials accessible from Terraform.
There is two supported providers, the variables which will be loaded depends on the used provider.

- `TF_VAR_aws_account`
- `TF_VAR_aws_region`
- `TF_VAR_client_name`
- `TF_VAR_aws_access_key`
- `TF_VAR_aws_secret_key`
- `TF_VAR_aws_token`
- `TF_VAR_azurerm_region`
- `TF_VAR_azure_region`
- `TF_VAR_azure_subscription_id`
- `TF_VAR_azure_tenant_id`

### Stack path

The stack path is passed to Terraform. This is especially useful for resource naming and tagging.

- `TF_VAR_account`
- `TF_VAR_environment`
- `TF_VAR_region`
- `TF_VAR_stack`
