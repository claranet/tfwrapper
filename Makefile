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

.DEFAULT_GOAL := work

setup:
ifeq ($(shell test $(python_version_minor) -le 4; echo $$?),0)
	$(error Python 3 too old, use Python 3.5 or greater.)
endif
ifneq ($(shell test -d $(makefile_dir)/.virtualenv; echo $$?),0)
	@echo 'Setting up virtualenv.'
	@virtualenv -p python3 $(makefile_dir)/.virtualenv
	@$(pip) install -r $(makefile_dir)/requirements.txt
endif

clear:
	@echo 'Removing virtualenv.'
	@rm -Rf $(makefile_dir)/.virtualenv

work: setup
	@PATH="$(wrapper_bin):$(virtualenv_bin):$(PATH)" $(SHELL)
