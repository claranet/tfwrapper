# Keep the user's current shell (say bash or zsh) instead of using the system's
# default /bin/sh shell which can differ (e.g. dash by default on Ubuntu).
SHELL := $(shell env | grep '^SHELL=' | cut -d '=' -f '2' )

python_version_full := $(wordlist 2,4,$(subst ., ,$(shell python3 --version 2>&1)))
python_version_minor := $(word 2,${python_version_full})

makefile_path := $(realpath $(lastword $(MAKEFILE_LIST)))
makefile_dir := $(patsubst %/,%,$(dir $(makefile_path)))
wrapper_bin := $(makefile_dir)/bin
virtualenv_bin := $(makefile_dir)/.virtualenv/bin
pip := $(virtualenv_bin)/pip
with_azure_deps := true

.DEFAULT_GOAL := work

setup:
ifeq ($(shell test $(python_version_minor) -le 4; echo $$?),0)
	$(error Python 3 too old, use Python 3.5 or greater.)
endif
ifneq ($(shell test -d $(makefile_dir)/.virtualenv; echo $$?),0)
	@echo 'Setting up virtualenv.'
	@virtualenv -p python3 $(makefile_dir)/.virtualenv
	@$(pip) install -r $(makefile_dir)/requirements.txt
ifeq ($(with_azure_deps),true)
	@$(pip) install -r $(makefile_dir)/requirements-azure.txt
endif
endif

update:
	@echo 'Cleaning up old dependencies.'
	@$(pip) freeze | xargs $(pip) uninstall -y
	@$(pip) install -U pip
	@echo 'Updating virtualenv Python dependencies.'
	@$(pip) install -r $(makefile_dir)/requirements.txt
ifeq ($(with_azure_deps),true)
	@$(pip) install -r $(makefile_dir)/requirements-azure.txt
endif

clean: clear
clear:
	@echo 'Removing virtualenv.'
	@rm -Rf $(makefile_dir)/.virtualenv

renew: clear setup
	@echo 'Renew done.'

work: setup
ifeq ($(shell test -z ${TERRAFORM_WRAPPER_SHELL}; echo $$?),0)
	@PATH="$(wrapper_bin):$(virtualenv_bin):$(PATH)" TERRAFORM_WRAPPER_SHELL="$(wrapper_bin)" $(SHELL)
	@echo 'terraform-wrapper env exited. ("$(wrapper_bin)")'
else
	@echo 'You already have a shell for "${TERRAFORM_WRAPPER_SHELL}" loaded.'
endif
