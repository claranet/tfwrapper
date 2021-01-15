# 7.10.0 (15/01/2021)

UPDATES:

  * TER-441: Use hashicorp API to locate terraform versions
  * TER-347: Update dependencies

FIXED:

  * TER-465: Wrapper cannot find terraform 0.12.30 & 0.13.6

# 7.9.5 (08/01/2021)

UPDATES:

  * TER-464: Pass state.yml configuration object to state.j2.tf template

# 7.9.4 (19/10/2020)

FIXED:

  * TER-463: Fix yaml unsafe load warning when using Azure profile

# 7.9.3 (29/09/2020)

FIXED:

  * TER-458: Fix `terraform version` ouput matching and parse

# 7.9.2 (17/09/2020)

UPDATES:

  * TER-439: Bump `azure-cli` to latest `2.11.1` and upgrade AWS/boto dependencies

# 7.9.1 (28/07/2020)

FIXED:

  * TER-456: Fix env for "each" process when using `foreach` (we must extend current `os.environ`)

# 7.9.0 (30/06/2020)

UPDATES:

  * TER-456: Export TFWRAPPER env variables when using `foreach`
  * TER-455: Handle Azure session check via Tenant ID

FIXED:

  * TER-458: terraform 0.13 no longer supports -v, use version subcommand

# 7.8.0 (25/05/2020)

UPDATES:

  * TER-454: support missing or empty state yml
  * TER-439: Bump `azure-cli` to latest `2.6.0` and upgrade AWS/boto dependencies

# 7.7.0 (29/04/2020)

UPDATES:

  * TER-450: CI - add python 3.6 and 3.8 to tested versions
  * TER-451: Update dependencies

FIXED:

  * TER-453: Don't load stack config for wrapper local commands (like `switchver`)

# 7.6.1 (20/02/2020)

FIXED:

  * TER-331: Allow `<patch>[0-9]` suffixes to custom provider release version

# 7.6.0 (20/02/2020)

ADDED:

  * TER-271: Cache github HTTP responses
  * TER-443: Pass `TF_PLUGIN_CACHE_DIR` environment variable to terraform if available
  * TER-444: Pre commit hooks and use `flake8`

UPDATES:

  * TER-442: Format code with black
  * TER-439: Bump `azure-cli` to `2.1.0`

# 7.5.1 (08/01/2020)

UPDATES:

  * TER-347: Bump Python/boto dependencies

# 7.5.0 (06/01/2020)

ADDED:

  * Add new wrapper option to refresh kubeconfig tokens

UPDATES:

  * Improve README with TOC
  * TER-439: Bump `azure-cli` to `2.0.77`

# 7.4.1 (09/12/2019)

FIXED:

  * TER-423: Fix directories path detection in Makefile for exported variables

# 7.4.0 (06/12/2019)

ADDED:

  * TER-438: Add support for .tar.gz, .tar.bz2 (not tested) and version number starting with "v"

UPDATES:

  * TER-343: Improve README documentation for kubeconfig management

# 7.3.0 (06/12/2019)

ADDED:

  * TER-35: Add `foreach` subcommand to execute arbitrary commands on several stacks at once

FIXED:

  * TER-35: fix foreach when -c is not specified

# 7.2.0 (29/10/2019)

ADDED:

  * TER-423: Option to override `azure-cli` session and config directory

UPDATES:

  * TER-419: Always check if a `terraform-wrapper` env is already activated and always update virtualenv

FIXED:

  * TER-417: Start search from the next incremented minor version

# 7.1.1 (25/09/2019)

FIXED:

  * TER-418: Fix switchver regression with short version (TER-415)

# 7.1.0 (18/09/2019)

ADDED:

  * TER-415: Support custom development builds of terraform

UPDATES:

  * TER-347: Bump Python/boto dependencies
  * TER-364: Bump `azure-cli` to `2.0.73`

# 7.0.0 (10/07/2019)

ADDED:

  * TER-391: New `-l`/`--pipe-plan` arguments to pipe the `plan` output to the command of your choice. That command can be specified with the new `--pipe-plan-command` argument or configured in the `config.yml` file as `pipe_plan_command: "my custom command"`.
  * TER-396: Allow mutiple states backends. We can now choose per stack which state backend to use

UPDATES:

  * TER-46: Bump Python dependencies
  * TER-364: Upgrade `azure cli` pip package to .64
  * TER-393: Support terraform release candidates
  * TER-395: Prioritize bootstrap template parameter, allow to bootstrap a non cloud template
  * TER-404: Make `init` optional via config when triggering `plan` or `apply`
  * TER-406: Update README documentation

BREAKING:

  * TER-388: Improve `bootstrap` behavior, no longer trigger `terraform init` automatically (old behavior is available via TER-404, can be set in config)

# 6.5.0 (18/03/2019)

ADDED:

  * TER-364: Support Azure Blob Storage as a terraform state backend
  * TER-382: Add `-d`/`--debug` output option

UPDATES:

  * TER-323: Do not use Github API to avoid rate limiting
  * TER-347: Upgrade core pip dependencies and split Azure CLI dependencies
  * TER-352: Update README
  * TER-354: Support downloading terraform and providers binaries for other platforms (`darwin`, `freebsd`, `linux`, `openbsd` and `windows`) and architectures (`amd64`, `arm` and `386`)
  * TER-358: Support terraform and providers pre-releases with version switching feature
  * TER-368: Split stack templates per cloud provider
  * TER-369: Refactoring
  * TER-377: Support AWS profiles without assume role
  * TER-381: Update `pyyaml` to 5.1 and use `yaml.safe_load`
  * TER-383: Improve `version` and `providers` subcommands

# 6.4.1 (25/01/2019)

UPDATES:

  * GITHUB-4: More robust shell detection in makefile.

# 6.4.0 (04/10/2018)

UPDATES:

  * TER-323: Display error message when Github API rate limit is in effect.
  * TER-342: Add basic Gitlab CI.
  * TER-343: Add support for GCP/GKE.
  * TER-347: Update `pip` dependencies.

# 6.3.0 (10/09/2018)

UPDATES:

  * TER-336: Add terraform version and providers commands support to the wrapper.
  * TER-331: Support download of custom providers from Github.
  * TER-319: Make subscription id check case insensitive.
  * GITHUB-1: Add lstrip_blocks=True and trim_blocks=True for jinja2 env.

# 6.2.1 (09/07/2018)

UPDATES:

  * TER-301: Fix bootstrap.

# 6.2.0 (06/07/2018)

UPDATES:

  * TER-253: Fix Azure language dependant date format
  * TER-241: Streamline wrapper output.
  * TER-284: Fix Ctrl+C.
  * TER-274: Always make sure that we use correct Terraform version.

# 6.1.1 (15/03/2018)

UPDATES:

  * GITHUB-1: Remove unused attribute in AWS configuration schema.

# 6.1.0 (14/03/2018)

UPDATES:

  * TER-214: Enhance Azure user mode error handling.
  * TER-225: Enhance Azure documentation.
  * TER-226: Enhance Azure configuration handling.
  * TER-228: Add basic schema validation to stack configuration.
  * TER-231: Switch from `azurerm_region` to `azure_region`.

# 6.0.0 (27/02/2018)

UPDATES:

  * TER-159: Terraform version siwtching support.
  * TER-28: azurerm token support update.

# 5.0.0 (08/01/2017)

UPDATES:

  * TER-28: Add support for Azure stacks.

# 4.1.0 (22/11/2017)

UPDATES:

  * TER-188: Use AWS profile as part of the pickle session cache filename.
  * TER-190: Initialize returncode.
  * TER-192: Update `README.md`.

# 4.0.1 (13/10/2017)

UPDATES:

  * TER-176: Add license file.

# 4.0.0 (11/10/2017)

NOTES:

  * Terraform subcommands error codes are now correctly returned.
  * Terraform 0.10.x is now supported with centralized provider caching.

UPDATES:

  * TER-46: Update requirements.txt to be compatible with Python 3.6.
  * TER-132: Enable provider caching.
  * TER-135: Remove unnecessary reference to role.
  * TER-139: Return Terraform's return code.
  * TER-174: Make sure that we pass pycodestyle check.


# 3.1.0 (13/07/2017)

NOTES:

  * Wrapper messages are now outputted to `stderr`

UPDATES:

  * TER-104: Output wrapper messages on `stderr`
  * TER-105: Catch some usual exceptions

# 3.0.2 (22/05/2017)

UPDATES:

  * TER-99: Update terraform subcommands.

# 3.0.1 (10/05/2017)

NOTES:

  * This version mitigates https://github.com/hashicorp/terraform/issues/14298. For long runs, clear the cached credentials in `.run`.
  * Runs taking more than 1 hr cannot be supported from terraform `0.9.0` to at least `0.9.4`, so try to make good use of `target`.

UPDATES:

  * TER-96: Add 15 minutes margin to AssumeRole renewal.

# 3.0.0 (27/04/2017)

NOTES:

  * Upgrade instructions: https://confluence.fr.clara.net/display/MT/Upgrade+to+Terraform+0.9

UPDATES:

  * TER-85: Support Terraform 0.9.
  * TER-87: Windows 10 compatibility.

# 2.0.0 (10/02/2017)

UPDATES:

  * TER-17: Add apply confirmation.
  * TER-19: Implement soft state locking.
  * TER-33: Fix stack detection for global environment.
  * TER-39: Force -update on a terraform get.
  * TER-57: do not fail to bootstrap when bootstrap is implicit.
  * TER-59: Support ACLs for statefiles.

# 1.1.1 (19/12/2016)

UPDATES:

  * Add default value to template.

# 1.1.0 (14/12/2016)

UPDATES:

  * TER-30: Add support for template parameter during bootstrap.

# 1.0.0 (25/11/2016)

UPDATES:

  * TER-9: Support wrapper execution from anywhere.

# 0.0.3 (22/08/2016)

UPDATES:

  * Fix untaint parser.

# 0.0.2 (05/08/2016)

UPDATES:

  * Bootstrap remote state before plan or apply if needed.

# 0.0.1 (05/08/2016)

  * First Release
