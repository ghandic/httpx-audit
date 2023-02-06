# Makefile best practices: https://docs.cloudposse.com/reference/best-practices/make-best-practices
# Reference: https://github.com/learningequality/ka-lite/blob/master/Makefile

.PHONY: help build
default: help

help:  # Reference: https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
	@grep -E '^[a-zA-Z_/-]+:.*?## .*$$' $(firstword $(MAKEFILE_LIST)) \
		| sort \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

init:  ## Initialize project with dev requirements
	@cp .env.sample .env
	@poetry install
	@npm install -g prettier

fmt:  ## Formats Python code to align with standards defined in pyproject.toml
	@poetry run isort .
	@poetry run black .
	@prettier --write *.{md,json,yml,yaml} --loglevel silent || exit 0

demo:  ## Runs the basic cli demo
	@poetry run python app/main.py
		
build:  ## Builds the local demo application
	@poetry export --without-hashes --format=requirements.txt > app/requirements.txt
	@docker-compose build

up:  ## Builds and starts the whole application stack
	@(MAKE build)
	@docker-compose up

up/debug:  ## Builds and starts the whole application stack with debugger attached
	@(MAKE build)
	@docker-compose -f docker-compose.yml -f docker-compose.debug.yml up

clean:  ## Removes junk build, test, coverage and Python artifacts
	@find . -type d -name dist -exec rm -fr {} +
	@find . -type d -name __pycache__ -exec rm -fr {} +
	@find . -type d -name htmlcov -exec rm -fr {} +
	@find . -type d -name log -exec rm -fr {} +
	@find . -type d -name obfuscated_log -exec rm -fr {} +

	@find . -type f -name .coverage -exec rm -f {} +
	@find . -type f -name .mypy_cache -exec rm -f {} +
	@find . -type f -name .pytest_cache -exec rm -f {} +

##################
### Make Utils ###
##################

check_defined = \
    $(strip $(foreach 1,$1, \
        $(call __check_defined,$1,$(strip $(value 2)))))
__check_defined = \
    $(if $(value $1),, \
      $(error Undefined $1$(if $2, Message: ($2))))