# tfwrapper

tfwrapper is a python wrapper for [Terraform](https://www.terraform.io/) which aims to simplify Terraform usage and enforce best practices.

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

## Dependencies

- Make
- Python `>= 3.5`
- python-pip
- python-virtualenv
- Terraform `>= 0.10`
- An AWS S3 bucket and DynamoDB table for state centralization in AWS.
- An Azure Storage blob container for state centralization in Azure.

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

The following files are required:

- `templates/{provider}/common/state.tf.jinja2`: AWS S3 or Azure Storage state backend configuration template.
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
    storage_account_name = "tfstatesprodclara"
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

### Stacks configurations

Stacks configuration files use the following naming convention:

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

Here is an example for a stack on Azure configuration using user mode:

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

Here is an example for a stack on Azure configuration using Service Principal mode:

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

### tfwrapper activation

```bash
# this will initialize a virtualenv and update your PATH in a new instance of your current SHELL
make
# if you don't want to install Azure CLI dependencies for a non Azure repository, you may want to use:
make -e with_azure_deps=false

tfwrapper -h

# when you are done using the tfwrapper you can leave the virtualenv
exit
```

### Stack bootstrap

After creating a `conf/${account}_${environment}_${region}_${stack}.yml` stack configuration file you can bootstrap it.

```bash
# you can bootstrap using the templates/{provider}/basic stack
tfwrapper -a ${account} -e ${environment} -r ${region} -s ${stack} bootstrap

# or another stack template, for example: templates/aws/foobar
tfwrapper -a ${account} -e ${environment} -r ${region} -s ${stack} bootstrap aws/foobar
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
