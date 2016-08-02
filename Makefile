SHELL := $(shell env | grep SHELL | cut -d '=' -f '2' )

makefile_path := $(realpath $(lastword $(MAKEFILE_LIST)))
makefile_dir := $(patsubst %/,%,$(dir $(makefile_path)))
wrapper_bin := $(makefile_dir)/bin
virtualenv_bin := $(makefile_dir)/.virtualenv/bin
pip := $(virtualenv_bin)/pip

.DEFAULT_GOAL := work

setup:
ifneq ($(shell test -d $(makefile_dir)/.virtualenv; echo $$?),0)
	@echo 'Setting up virtualenv.'
	@virtualenv -p python3 $(makefile_dir)/.virtualenv
	@$(pip) install -r $(makefile_dir)/requirements.txt
endif

clear:
	@echo 'Removing virtualenv.'
	@rm -Rf $(makefile_dir)/.virtualenv

work: setup
	@PATH=$(wrapper_bin):$(virtualenv_bin):$(PATH) $(SHELL)
