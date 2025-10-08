# 14.0.3 (2025/10/08)

FIXES:

- fix: do not download tool for foreach command

BUILD:

- build: migrate from poetry to uv

UPDATES:

- chore(deps): lock file maintenance (#573)
- chore(deps): update actions/checkout action to v5
- chore(deps): update actions/download-artifact action to v5
- chore(deps): update actions/setup-python action to v6
- chore(deps): update dependency boto3 to v1.40.45 (#572)
- chore(deps): update dependency packaging to v25
- chore(deps): update dependency poetry to v2.2.1 (#571)
- chore(deps): update dependency python to v3.14.0 (#574)
- chore(deps): update dependency ruff to v0.14.0
- chore(deps): update dependency termcolor to v3
- chore(deps): update dependency tox to v4.30.3 (#575)
- chore(deps): update jdx/mise-action action to v3

# 14.0.2 (2025/09/30)

FIXES:

- fix: tolerate underscore character in stack names
- fix: create .run directory if missing

UPDATES:

- chore(deps): lock file maintenance (#563)
- chore(deps): lock file maintenance (#567)
- chore(deps): lock file maintenance (#569)
- chore(deps): update dependency boto3 to v1.40.30 (#562)
- chore(deps): update dependency coverage to v7.10.7 (#566)
- chore(deps): update dependency pytest-mock to v3.15.1 (#565)
- chore(deps): update dependency pyyaml to v6.0.3 (#568)
- chore(deps): update dependency tox to v4.30.2 (#570)
- chore(deps): update py-cov-action/python-coverage-comment-action action to v3.38 (#564)

# 14.0.1 (2025/09/08)

FIXES:

- TER-498: do not only rely on file modification time for cached credentials

UPDATES:

- chore(deps): lock file maintenance
- chore(deps): update actions/setup-python action to v5.6.0
- chore(deps): update dependency boto3 to v1.40.25
- chore(deps): update dependency coverage to v7.9.2
- chore(deps): update dependency pook to v2.1.4
- chore(deps): update dependency pre-commit to v4.3.0
- chore(deps): update dependency pytest to v8.4.2
- chore(deps): update dependency pytest-mock to v3.15.0
- chore(deps): update dependency python to v3.13.7
- chore(deps): update dependency requests to v2.32.5
- chore(deps): update dependency tox to v4.27.0
- chore(deps): update py-cov-action/python-coverage-comment-action action to v3.37

# 14.0.0 (2025/03/07)

BREAKING:

- Drop support for Python 3.8

ADDED:

- Add support for Python 3.13

UPDATES:

- Update pyproject syntax from poetry v1 to v2 respecting PEP-621
- Replace black and flake8 with ruff for linting and formatting

# 13.2.4 (2025/03/07)

FIXES:

- fix: GitHub releases page no longer support `after` parameter, use tags page

UPDATES:

- chore(deps): lock file maintenance
- chore(deps): update actions/setup-python action to v5.4.0
- chore(deps): update dependency argcomplete to v3.6.0
- chore(deps): update dependency black to v24.10.0
- chore(deps): update dependency boto3 to v1.37.4
- chore(deps): update dependency cachecontrol to v0.14.2
- chore(deps): update dependency certifi to 2024.7.4
- chore(deps): update dependency colorlog to v6.9.0
- chore(deps): update dependency coverage to v7.6.12
- chore(deps): update dependency flake8 to v7.1.2
- chore(deps): update dependency jinja2 to v3.1.5
- chore(deps): update dependency jinja2 to v3.1.6
- chore(deps): update dependency md-toc to v9.0.0
- chore(deps): update dependency mock to v5.2.0
- chore(deps): update dependency packaging to v24.2
- chore(deps): update dependency pook to v2.1.3
- chore(deps): update dependency pre-commit to v3.8.0
- chore(deps): update dependency pytest to v8.3.5
- chore(deps): update dependency python to v3.13.2
- chore(deps): update dependency schema to v0.7.7
- chore(deps): update dependency semver to v3.0.4
- chore(deps): update dependency setuptools to 70.0.0
- chore(deps): update dependency tox to v4.24.1
- chore(deps): update dependency urllib3 to 1.26.19
- chore(deps): update dependency zipp to 3.19.1
- chore(deps): update py-cov-action/python-coverage-comment-action action to v3.30

# 13.2.3 (2024/10/24)

FIXES:

- hotfix: GitHub release page no longer supports `after` parameter

UPDATES:

- chore(deps): lock file maintenance
- chore(deps): update actions/setup-python action to v5.2.0
- chore(deps): update dependency black to v24.8.0
- chore(deps): update dependency coverage to v7.6.1
- chore(deps): update dependency flake8 to v7.1.1
- chore(deps): update dependency pytest to v8.3.3
- chore(deps): update dependency pytest-mock to v3.14.0
- chore(deps): update dependency python to v3.13.0
- chore(deps): update dependency requests-mock to v1.12.1
- chore(deps): update dependency tox to v4.23.2
- chore(deps): update py-cov-action/python-coverage-comment-action action to v3.27
- fix(deps): update dependency argcomplete to v3.5.1
- fix(deps): update dependency boto3 to v1.35.47
- fix(deps): update dependency jinja2 to v3.1.4
- fix(deps): update dependency packaging to v24.1
- fix(deps): update dependency pyyaml to v6.0.2
- fix(deps): update dependency requests to v2.32.3

# 13.2.2 (2024/03/13)

UPDATES:

- fix: log stack config path in debug mode
- chore(deps): group boto3/botocore deps and only create PRs on Sunday evening
- chore(deps): lock file maintenance
- chore(deps): update dependency black to v24
- chore(deps): update dependency coverage to v7.4.3
- chore(deps): update dependency md-toc to v8.2.3
- chore(deps): update dependency pook to v1.4.2
- chore(deps): update dependency pook to v1.4.3
- chore(deps): update dependency pytest to v8
- chore(deps): update dependency tox to v4.14.1
- chore(deps): update py-cov-action/python-coverage-comment-action action to v3.23
- fix(deps): update dependency argcomplete to v3.2.3
- fix(deps): update dependency boto3 to v1.34.61
- fix(deps): update dependency cachecontrol to ^0.14.0
- fix(deps): update dependency packaging to v24

# 13.2.1 (2024/02/01)

UPDATES:

- chore(deps): update actions/upload-artifact action to v4
- chore(deps): update dependency coverage to v7.4.1
- chore(deps): update dependency python to v3.12.1
- chore(deps): update dependency tox to v4.12.1
- chore(deps): update py-cov-action/python-coverage-comment-action action to v3.21
- deps: support Python 3.12
- fix(deps): update dependency argcomplete to v3.2.2
- fix(deps): update dependency boto3 to v1.34.32
- fix(deps): update dependency colorlog to v6.8.2
- fix(deps): update dependency jinja2 to v3.1.3

# 13.2.0 (2024/01/10)

ADDED:

- feat(TER-520): support OpenTofu

UPDATES:

- build(deps): bump urllib3 from 1.26.17 to 1.26.18
- chore(deps): lock file maintenance
- chore(deps): update actions/setup-python action to v4.8.0
- chore(deps): update actions/setup-python action to v5
- chore(deps): update dependency black to v23.12.1
- chore(deps): update dependency coverage to v7.4.0
- chore(deps): update dependency flake8 to v7
- chore(deps): update dependency md-toc to v8.2.2
- chore(deps): update dependency pook to v1.4.0
- chore(deps): update dependency pytest-mock to v3.12.0
- chore(deps): update dependency pytest to v7.4.4
- chore(deps): update dependency tox to v4.11.4
- chore(deps): update py-cov-action/python-coverage-comment-action action to v3.20
- fix(deps): update dependency argcomplete to v3.2.1
- fix(deps): update dependency boto3 to v1.28.63
- fix(deps): update dependency boto3 to v1.34.15
- fix(deps): update dependency colorlog to v6.8.0
- fix(deps): update dependency termcolor to v2.4.0

# 13.1.2a15 (2023/10/13)

UPDATES:

- ci: use py-cov-action/python-coverage-comment-action@v3.15

# 13.1.2a13 (2023/10/11)

UPDATES:

- ci: Revert "ci: only run coverage action for pull requests"
- ci: test py-cov-action/python-coverage-comment-action@fix-285-push-tag

# 13.1.2a11 (2023/10/11)

FIXES:

- ci: only run coverage action for pull requests

UPDATES:

- ci: ewjoachim/python-coverage-comment-action@v3 is now py-cov-action/python-coverage-comment-action@v3

# 13.1.2a9 (2023/10/11)

FIXES:

- ci: fix permissions needed for workflows

# 13.1.2a7 (2023/10/10)

FIXES:

- ci: downloading of coverage artifacts

# 13.1.2a5 (2023/10/10)

FIXES:

- ci: fix posting of coverage messages to GitHub PRs

# 13.1.2a3 (2023/10/10)

FIXES:

- ci: fix creation of GitHub pre-releases

# 13.1.2a1 (2023/10/10)

UPDATES:

- doc: clarify account term usage, document global case, and remove obsolete information
- ci: authenticate to PyPI with OIDC for publishing artifacts
- ci: enable GitHub's Merge Queue
- ci: replace Dependabot by RenovateBot with automerge enabled

- deps: bump black from 23.7.0 to 23.9.1
- deps: bump coverage from 7.3.0 to 7.3.1
- deps: bump pytest from 7.4.1 to 7.4.2
- deps: bump tox from 4.11.1 to 4.11.3
- deps: lock file maintenance

# 13.1.1 (2023/09/11)

FIXES:

- deps: require filecache extra of CacheControl to ensure filelock is installed
- doc: fix poetry version in changelog

UPDATES:

- Update all dependencies

# 13.1.1a0 (2023/09/05)

FIXES:

- replace deprecated usage of set-output in Github Actions

# 13.1.0 (2023/09/05)

UPDATES:

- Use poetry 1.6.1 in CI
- Update all dependencies

# 13.0.0 (2023/06/13)

BREAKING:

- Drop support for Python 3.7

FIXES:

- fix(TER-515): Only lock and mirror sub-commands of providers sub-command do not require state access

ADDED:

- Add script to automate Dependabot PRs review and merge workflow

UPDATES:

- Use poetry 1.5.1 in CI
- Update all dependencies


# 12.2.0 (2023/02/16)

FIXES:

- TER-504: fix exit code management on Ctrl-C during plan

UPDATES:

- Bump actions/setup-python from 4.3.0 to 4.5.0
- Bump black from 22.10.0 to 23.1.0
- Bump certifi from 2021.10.8 to 2022.12.7
- Bump coverage from 6.5.0 to 7.1.0
- Bump ewjoachim/python-coverage-comment-action from 2 to 3
- Bump flake8-docstrings from 1.6.0 to 1.7.0
- Bump md-toc from 8.1.5 to 8.1.9
- Bump mock from 4.0.3 to 5.0.1
- Bump packaging from 21.3 to 23.0
- Bump poetry from 1.1.13 to 1.3.2
- Bump pook from 1.0.2 to 1.1.1
- Bump pytest from 7.2.0 to 7.2.1
- Bump requests from 2.28.1 to 2.28.2
- Bump termcolor from 2.1.0 to 2.2.0

# 12.1.0 (2022/11/21)

ADDED:

- TER-515: no need to load backend configuration for terraform providers command

# 12.0.0 (2022/11/07)

BREAKING:

- TER-505: drop support for python 3.6 and use python 3.10 as main target version everywhere

ADDED:

- TER-510: When bootstrapping a stack from an existent one, do not copy the state.tf file and .terraform folder
- TER-511: Fix environment variable set like documented in README, `account` and `region` are now always set (not only for AWS context).
- TER-513: Fix azurerm backend initialization

UPDATES

- Bump actions/download-artifact from 2 to 3
- Bump actions/setup-python from 3 to 4.3.0
- Bump actions/upload-artifact from 2 to 3
- Bump argcomplete from 1.12.3 to 2.0.0
- Bump black from 22.1.0 to 22.10.0
- Bump boto3 from 1.22.0 to 1.26.1
- Bump colorlog from 6.6.0 to 6.7.0
- Bump coverage from 6.3.2 to 6.5.0
- Bump flake8 from 4.0.1 to 5.0.4
- Bump jinja2 from 3.1.1 to 3.1.2
- Bump md-toc from 8.1.1 to 8.1.5
- Bump natsort from 8.1.0 to 8.2.0
- Bump pytest from 7.1.2 to 7.2.0
- Bump requests from 2.27.1 to 2.28.1
- Bump requests-mock from 1.9.3 to 1.10.0
- Bump termcolor from 1.1.0 to 2.1.0

# 11.0.0 (2022/04/08)

BREAKING:

- TER-493: Remove Azure SDK dependencies, use Azure CLI, and fall back to a [standard usage of azure backend configuration](https://www.terraform.io/language/settings/backends/azurerm).
  - Specific installation procedure with azure dependencies does not exist anymore, more details in [installation instructions](https://github.com/claranet/terraform-wrapper#installation).
  - Previous Azure backend state and data remote states configurations files may now be incomplete. It is necessary to define `subscription_id` and `resource_group_name` attributes if not present. See [azurerm backend documentation ](https://www.terraform.io/language/settings/backends/azurerm).

ADDED

- TER-468: Allow templates outside templates directory
- TER-492: Allow multiple states configuration for a same backend type, see [states centralization configuration](https://github.com/claranet/terraform-wrapper#states-centralization-configuration).
- TER-497: Allow multiple providers declaration in stack configuration. Only supported for Azure stacks for now, see [stacks-configurations](https://github.com/claranet/terraform-wrapper#stacks-configurations).
- TER-499: Fix regressions on `bootstrap` and `foreach` introduced in v9.2.0
- TER-500: Add coverage
- TER-501: Improve HTTP requests cache initialization and ensure all unit tests have their own empty cache
- TER-502: Ignore flake8 rule D103 on all unit test files

UPDATES

- Bump actions/checkout from 2 to 3
- Bump requests from 2.25.1 to 2.27.1

# 10.0.0 (2022/03/10)

BREAKING:

- GH-51: Rename `foreach` subcommand `-c` parameter to `-S`/`--shell` to avoid conflict with main stack parameter

UPDATES:

- Add .github/dependabot.yml
- Bump azure-common from 1.1.27 to 1.1.28
- Bump azure-cli-core from 2.30.0 to 2.33.1
- Bump azure-mgmt-storage from 18.0.0 to 19.1.0
- Bump black from 21.9b0 to 22.1.0
- Bump boto3 from 1.18.59 to 1.21.3
- Bump cachecontrol from 0.12.6 to 0.12.10
- Bump colorlog from 5.0.1 to 6.6.0
- Bump flake8 from 3.9.2 to 4.0.1
- Bump jinja2 from 3.0.2 to 3.0.3
- Bump md-toc from 8.0.1 to 8.1.1
- Bump natsort from 7.1.1 to 8.1.0
- Bump packaging from 21.0 to 21.3
- Bump pytest from 6.2.5 to 7.0.1
- Bump pyyaml from 5.4.1 to 6.0
- Bump schema from 0.7.4 to 0.7.5
- Ignore all boto3 patch updates which are too frequent (but not security updates), and allow up to 10 PRs

FIXES:

- Fix black command for lint
- poetry add --dev toml
- Properly check prerelease status in Create Release step

# 9.2.0 (2022/02/08)

ADDED:

TER-496: add shell completion to tfwrapper and terraform commands

UPDATES:

- Update pre-commit hooks and add flake8-docstrings dependency to flake8 pre-commit hook to match CI checks

# 9.1.0 (2022/01/24)

ADDED:

- TER-495: Add support for `terraform workspace` command

UPDATES:

- Add poetry.toml to set `in-project = true` by default

# 9.0.0 (2021/11/15)

BREAKING:

- TER-489/[GITHUB-19](https://github.com/claranet/terraform-wrapper/issues/19): Upgrade `azure-cli-core` deps to `v2.30.0` and uses MSAL auth. `azure-cli` must be in `v2.30.0` or a newer version

# 8.1.2 (2021/10/27)

FIXED:

- TER-486: script release process (it was a pain to do it right each time)

# 8.1.1 (2021/10/25)

FIXED:

- TER-485: fix `use_local_azure_session_directory` parameter which was no longer taken into account since v8.0.0

# 8.1.0 (2021/10/12)

UPDATES:

- TER-473: cleanup README of remaining Makefile references
- TER-478: display gcloud command output in case of error
- TER-482: add support for python 3.10 and update dependencies

FIXED:

- TER-477: remove warning about using `amd64` binaries on non-`arm64` architecture for `darwin` platform
- TER-483: fix azure extras

# 8.0.2 (2021/08/31)

FIXED:

- TER-476: re-add `packaging` dependency needed for Azure authentication that was lost on removal of `azure-cli` dependency

# 8.0.1 (2021/08/31)

FIXED:

- TER-475: terraform only supports `darwin` (MacOS) on `arm64` (Apple Silicon M1) since v1.0.2, so force usage of `amd64` binaries with Rosetta for older terraform versions
- TER-476: re-add `azure-cli-core` and `msrestazure` dependencies needed for Azure authentication that were lost on removal of `azure-cli` dependency

# 8.0.0 (2021/08/30)

BREAKING:

- TER-473: Use poetry to manage project to:
  - make it installable with pip and pipx once, no longer as a submodule of each workspace
  - ease dependencies management and make it more robust
  - remove the `Makefile`
  - remove the `switchver` subcommand that is no longer needed now that terraform binary is directly used from `~/.terraform.d/versions` and symbolic links are no longer created in `.wrapper/bin`
  - add `-V`/`--version` parameter to get the version of the tfwrapper itself
  - `use_local_azure_session_directory` now defaults to `True`
  - drop `azure-cli` dependency from the wrapper's virtualenv (use `pipx install azure-cli` to install it in your environment if you need)

FIXED:

- TER-474: Support downloading terraform binaries for MacOS on Apple Silicon M1 (`darwin_arm64`)

# 7.13.2 (2021/06/24)

UPDATES:

- TER-347: Update dependencies (azure-cli `v2.25.0`)

# 7.13.1 (2021/06/14)

FIXED:

- TER-430: Hotfix bootstrapped stacks created in conf directory
- [GITHUB-12](https://github.com/claranet/terraform-wrapper/pull/12): Bump urllib3 from 1.26.4 to 1.26.5

# 7.13.0 (2021/05/11)

ADDED:

- TER-430: Only load backend configuration for terraform commands requiring it

FIXED:

- TER-472: Fix switchver check when terraform version from global PATH is already matching

# 7.12.1 (2021/04/19)

FIXED:

- TER-471: Fix switchver version selection to place releases before all pre-versions

UPDATES:

- TER-471: Add python 3.9 in tests

# 7.12.0 (2021/03/29)

UPDATES:

- TER-347: Update dependencies
- [GITHUB-10](https://github.com/claranet/terraform-wrapper/pull/10): Bump jinja2 from 2.11.2 to 2.11.3
- [GITHUB-11](https://github.com/claranet/terraform-wrapper/pull/11): Bump pyyaml from 5.3.1 to 5.4.1

# 7.11.1 (2021/03/12)

FIXED:

- TER-467: Fix Azure HTTP logging policy

# 7.11.0 (2021/02/03)

UPDATES:

- TER-466: Don't try to generate/load Azure storage backend credentials if they're already set

# 7.10.0 (2021/01/15)

UPDATES:

- TER-441: Use hashicorp API to locate terraform versions
- TER-347: Update dependencies

FIXED:

- TER-465: Wrapper cannot find terraform 0.12.30 & 0.13.6

# 7.9.5 (2021/01/08)

UPDATES:

- TER-464: Pass state.yml configuration object to state.j2.tf template

# 7.9.4 (2020/10/19)

FIXED:

- TER-463: Fix yaml unsafe load warning when using Azure profile

# 7.9.3 (2020/09/29)

FIXED:

- TER-458: Fix `terraform version` ouput matching and parse

# 7.9.2 (2020/09/17)

UPDATES:

- TER-439: Bump `azure-cli` to latest `2.11.1` and upgrade AWS/boto dependencies

# 7.9.1 (2020/07/28)

FIXED:

- TER-456: Fix env for "each" process when using `foreach` (we must extend current `os.environ`)

# 7.9.0 (2020/06/30)

UPDATES:

- TER-456: Export TFWRAPPER env variables when using `foreach`
- TER-455: Handle Azure session check via Tenant ID

FIXED:

- TER-458: terraform 0.13 no longer supports -v, use version subcommand

# 7.8.0 (2020/05/25)

UPDATES:

- TER-454: support missing or empty state yml
- TER-439: Bump `azure-cli` to latest `2.6.0` and upgrade AWS/boto dependencies

# 7.7.0 (2020/04/29)

UPDATES:

- TER-450: CI - add python 3.6 and 3.8 to tested versions
- TER-451: Update dependencies

FIXED:

- TER-453: Don't load stack config for wrapper local commands (like `switchver`)

# 7.6.1 (2020/02/20)

FIXED:

- TER-331: Allow `<patch>[0-9]` suffixes to custom provider release version

# 7.6.0 (2020/02/20)

ADDED:

- TER-271: Cache github HTTP responses
- TER-443: Pass `TF_PLUGIN_CACHE_DIR` environment variable to terraform if available
- TER-444: Pre commit hooks and use `flake8`

UPDATES:

- TER-442: Format code with black
- TER-439: Bump `azure-cli` to `2.1.0`

# 7.5.1 (2020/01/08)

UPDATES:

- TER-347: Bump Python/boto dependencies

# 7.5.0 (2020/01/06)

ADDED:

- Add new wrapper option to refresh kubeconfig tokens

UPDATES:

- Improve README with TOC
- TER-439: Bump `azure-cli` to `2.0.77`

# 7.4.1 (2019/12/09)

FIXED:

- TER-423: Fix directories path detection in Makefile for exported variables

# 7.4.0 (2019/12/06)

ADDED:

- TER-438: Add support for .tar.gz, .tar.bz2 (not tested) and version number starting with "v"

UPDATES:

- TER-343: Improve README documentation for kubeconfig management

# 7.3.0 (2019/12/06)

ADDED:

- TER-35: Add `foreach` subcommand to execute arbitrary commands on several stacks at once

FIXED:

- TER-35: fix foreach when -c is not specified

# 7.2.0 (2019/10/29)

ADDED:

- TER-423: Option to override `azure-cli` session and config directory

UPDATES:

- TER-419: Always check if a `terraform-wrapper` env is already activated and always update virtualenv

FIXED:

- TER-417: Start search from the next incremented minor version

# 7.1.1 (2019/09/25)

FIXED:

- TER-418: Fix switchver regression with short version (TER-415)

# 7.1.0 (2019/09/18)

ADDED:

- TER-415: Support custom development builds of terraform

UPDATES:

- TER-347: Bump Python/boto dependencies
- TER-364: Bump `azure-cli` to `2.0.73`

# 7.0.0 (2019/07/10)

ADDED:

- TER-391: New `-l`/`--pipe-plan` arguments to pipe the `plan` output to the command of your choice. That command can be specified with the new `--pipe-plan-command` argument or configured in the `config.yml` file as `pipe_plan_command: "my custom command"`.
- TER-396: Allow mutiple states backends. We can now choose per stack which state backend to use

UPDATES:

- TER-46: Bump Python dependencies
- TER-364: Upgrade `azure cli` pip package to .64
- TER-393: Support terraform release candidates
- TER-395: Prioritize bootstrap template parameter, allow to bootstrap a non cloud template
- TER-404: Make `init` optional via config when triggering `plan` or `apply`
- TER-406: Update README documentation

BREAKING:

- TER-388: Improve `bootstrap` behavior, no longer trigger `terraform init` automatically (old behavior is available via TER-404, can be set in config)

# 6.5.0 (2019/03/18)

ADDED:

- TER-364: Support Azure Blob Storage as a terraform state backend
- TER-382: Add `-d`/`--debug` output option

UPDATES:

- TER-323: Do not use Github API to avoid rate limiting
- TER-347: Upgrade core pip dependencies and split Azure CLI dependencies
- TER-352: Update README
- TER-354: Support downloading terraform and providers binaries for other platforms (`darwin`, `freebsd`, `linux`, `openbsd` and `windows`) and architectures (`amd64`, `arm` and `386`)
- TER-358: Support terraform and providers pre-releases with version switching feature
- TER-368: Split stack templates per cloud provider
- TER-369: Refactoring
- TER-377: Support AWS profiles without assume role
- TER-381: Update `pyyaml` to 5.1 and use `yaml.safe_load`
- TER-383: Improve `version` and `providers` subcommands

# 6.4.1 (2019/01/25)

UPDATES:

- [GITHUB-4](https://github.com/claranet/terraform-wrapper/pull/4): More robust shell detection in makefile.

# 6.4.0 (2018/10/04)

UPDATES:

- TER-323: Display error message when Github API rate limit is in effect.
- TER-342: Add basic Gitlab CI.
- TER-343: Add support for GCP/GKE.
- TER-347: Update `pip` dependencies.

# 6.3.0 (2018/09/10)

UPDATES:

- TER-336: Add terraform version and providers commands support to the wrapper.
- TER-331: Support download of custom providers from Github.
- TER-319: Make subscription id check case insensitive.
- [GITHUB-2](https://github.com/claranet/terraform-wrapper/pull/2): Add lstrip_blocks=True and trim_blocks=True for jinja2 env.

# 6.2.1 (2018/07/09)

UPDATES:

- TER-301: Fix bootstrap.

# 6.2.0 (2018/07/06)

UPDATES:

- TER-253: Fix Azure language dependant date format
- TER-241: Streamline wrapper output.
- TER-284: Fix Ctrl+C.
- TER-274: Always make sure that we use correct Terraform version.

# 6.1.1 (2018/03/15)

UPDATES:

- [GITHUB-1](https://github.com/claranet/terraform-wrapper/pull/1): Remove unused attribute in AWS configuration schema.

# 6.1.0 (2018/03/14)

UPDATES:

- TER-214: Enhance Azure user mode error handling.
- TER-225: Enhance Azure documentation.
- TER-226: Enhance Azure configuration handling.
- TER-228: Add basic schema validation to stack configuration.
- TER-231: Switch from `azurerm_region` to `azure_region`.

# 6.0.0 (2018/02/27)

UPDATES:

- TER-159: Terraform version siwtching support.
- TER-28: azurerm token support update.

# 5.0.0 (2017/01/08)

UPDATES:

- TER-28: Add support for Azure stacks.

# 4.1.0 (2017/11/22)

UPDATES:

- TER-188: Use AWS profile as part of the pickle session cache filename.
- TER-190: Initialize returncode.
- TER-192: Update `README.md`.

# 4.0.1 (2017/10/13)

UPDATES:

- TER-176: Add license file.

# 4.0.0 (2017/10/11)

NOTES:

- Terraform subcommands error codes are now correctly returned.
- Terraform 0.10.x is now supported with centralized provider caching.

UPDATES:

- TER-46: Update requirements.txt to be compatible with Python 3.6.
- TER-132: Enable provider caching.
- TER-135: Remove unnecessary reference to role.
- TER-139: Return Terraform's return code.
- TER-174: Make sure that we pass pycodestyle check.

# 3.1.0 (2017/07/13)

NOTES:

- Wrapper messages are now outputted to `stderr`

UPDATES:

- TER-104: Output wrapper messages on `stderr`
- TER-105: Catch some usual exceptions

# 3.0.2 (2017/05/22)

UPDATES:

- TER-99: Update terraform subcommands.

# 3.0.1 (2017/05/10)

NOTES:

- This version mitigates https://github.com/hashicorp/terraform/issues/14298. For long runs, clear the cached credentials in `.run`.
- Runs taking more than 1 hr cannot be supported from terraform `0.9.0` to at least `0.9.4`, so try to make good use of `target`.

UPDATES:

- TER-96: Add 15 minutes margin to AssumeRole renewal.

# 3.0.0 (2017/04/27)

NOTES:

- Upgrade instructions: https://confluence.fr.clara.net/display/MT/Upgrade+to+Terraform+0.9

UPDATES:

- TER-85: Support Terraform 0.9.
- TER-87: Windows 10 compatibility.

# 2.0.0 (2017/02/10)

UPDATES:

- TER-17: Add apply confirmation.
- TER-19: Implement soft state locking.
- TER-33: Fix stack detection for global environment.
- TER-39: Force -update on a terraform get.
- TER-57: do not fail to bootstrap when bootstrap is implicit.
- TER-59: Support ACLs for statefiles.

# 1.1.1 (2016/12/19)

UPDATES:

- Add default value to template.

# 1.1.0 (2016/12/14)

UPDATES:

- TER-30: Add support for template parameter during bootstrap.

# 1.0.0 (2016/11/25)

UPDATES:

- TER-9: Support wrapper execution from anywhere.

# 0.0.3 (2016/08/22)

UPDATES:

- Fix untaint parser.

# 0.0.2 (2016/08/05)

UPDATES:

- Bootstrap remote state before plan or apply if needed.

# 0.0.1 (2016/08/05)

- First Release
