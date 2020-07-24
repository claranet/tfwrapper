makefile_path := $(realpath $(lastword $(MAKEFILE_LIST)))
makefile_dir := $(patsubst %/,%,$(dir $(makefile_path)))
wrapper_bin := $(makefile_dir)/bin
virtualenv_bin := $(makefile_dir)/.virtualenv/bin
pip := $(virtualenv_bin)/pip
run_dir := $(realpath $(makefile_dir)/..)/.run
conf_dir := $(realpath $(makefile_dir)/..)/conf

export PATH := $(wrapper_bin):$(virtualenv_bin):$(PATH)

# Keep the user's current shell (say bash or zsh) instead of using the system's
# default /bin/sh shell which can differ (e.g. dash by default on Ubuntu).
OUT_SHELL := $(shell env | grep '^SHELL=' | cut -d '=' -f '2' )
SHELL := env PATH=$(PATH) $(OUT_SHELL)

python_version_full := $(wordlist 2,4,$(subst ., ,$(shell python3 --version 2>&1)))
python_version_minor := $(word 2,${python_version_full})

# Config parsing
use_local_azure_session_directory := $(shell grep -i 'use_local_azure_session_directory' $(conf_dir)/config.yml 2>&1 | grep -i 'true' 2>&1 >/dev/null && echo 'true' || echo 'false')
with_azure_deps := $(shell grep -i 'install_azure_dependencies' $(conf_dir)/config.yml 2>&1 | grep -i 'false' 2>&1 >/dev/null && echo 'false' || echo 'true')

.PHONY := check clean clear renew work
.DEFAULT_GOAL := work

check:
ifeq ($(shell test $(python_version_minor) -le 4; echo $$?),0)
	$(error Python 3 too old, use Python 3.5 or greater.)
endif

venv: check
ifneq ($(shell test -d $(makefile_dir)/.virtualenv; echo $$?),0)
ifneq (,$(findstring zsh,$(OUT_SHELL)))
	$(MAKE) $(makefile_dir)/.zshtempdir
endif
	@echo 'Setting up virtualenv.'
	@python3 -m venv $(makefile_dir)/.virtualenv
endif

$(makefile_dir)/.zshtempdir: check 
	@echo 'Setting up zshtempdir.'
	@mkdir -p $(makefile_dir)/.zshtempdir
	@cp -f $(HOME)/.zshrc $(makefile_dir)/.zshtempdir/.zshrc
ifeq ($(use_local_azure_session_directory),true)
	@echo 'export PATH="$(wrapper_bin):$(virtualenv_bin):$(PATH)"\nAZURE_CONFIG_DIR="$(run_dir)/azure"\nTERRAFORM_WRAPPER_SHELL="$(wrapper_bin)" >> $(makefile_dir)/.zshtempdir/.zshrc'
else
	@echo 'export PATH="$(wrapper_bin):$(virtualenv_bin):$(PATH)"\nTERRAFORM_WRAPPER_SHELL="$(wrapper_bin)"' >> $(makefile_dir)/.zshtempdir/.zshrc
endif

setup: check venv
	@$(pip) install -U pip
	@$(pip) install -r $(makefile_dir)/requirements.txt
ifeq ($(with_azure_deps),true)
	@$(pip) install -r $(makefile_dir)/requirements-azure.txt
endif

clean clear: check
	@echo 'Removing virtualenv.'
	@rm -Rf $(makefile_dir)/.virtualenv
	@echo 'Removing zsh tempdir.'
	@rm -Rf $(makefile_dir)/.zshtempdir

renew: check clear setup
	@echo 'Renew done.'

work: check setup
ifneq (,$(findstring zsh,$(OUT_SHELL)))
	ZDOTDIR=$(makefile_dir)/.zshtempdir $(OUT_SHELL)
else
ifeq ($(use_local_azure_session_directory),true)
	@echo 'Exporting AZURE_CONFIG_DIR="$(run_dir)/azure"'
	@PATH="$(wrapper_bin):$(virtualenv_bin):$(PATH)" AZURE_CONFIG_DIR="$(run_dir)/azure" TERRAFORM_WRAPPER_SHELL="$(wrapper_bin)" $(OUT_SHELL)
else
	@PATH="$(wrapper_bin):$(virtualenv_bin):$(PATH)" TERRAFORM_WRAPPER_SHELL="$(wrapper_bin)" $(OUT_SHELL)
endif
endif
	@echo 'terraform-wrapper env exited. ("$(wrapper_bin)")'
