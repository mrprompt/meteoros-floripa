# import env config
cnf ?= .env
include $(cnf)
export $(shell sed 's/=.*//' $(cnf))

# Local variables
PWD=$(shell pwd)

ifndef VERBOSE
MAKEFLAGS += --no-print-directory -s 
endif

# Functions
define prompt_continue
	@read -p "Continue? [y/N]: " ans && [ $${ans:-N} != y ] && echo "Exiting" && exit 1;
endef

# HELP
# This will output the help for each task
# thanks to https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help http-up http-down http-enter http-logs
.DEFAULT_GOAL := help

help: ## This help.
#	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@awk 'BEGIN {FS = ":.*##"; printf "\n\u2605 Usage:\n \033[32m make \033[0m\033[36m<target> [params]\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } '  $(MAKEFILE_LIST)

http-up: ## Start http server
ifeq ($(shell docker ps -f name=meteoros-floripa-http | wc -l | tr -d '[:space:]'), 1)
	@echo "Starting http service"
	@docker run \
		--rm \
		--name meteoros-floripa-http \
		-v $(PWD):/usr/src/app \
		-p 4000:4000 \
		starefossen/github-pages
else
	@echo "Service meteoros-floripa-http up and running"
endif

http-down: ## Stop http server
ifeq ($(shell docker ps -f name=meteoros-floripa-http | wc -l | tr -d '[:space:]'), 2)
	@echo "Stopping meteoros-floripa-http"
	@docker stop meteoros-floripa-http
else
	@echo "Service meteoros-floripa-http is not running"
endif

http-enter: ## Enter to http server shell
ifeq ($(shell docker ps -f name=meteoros-floripa-http | wc -l | tr -d '[:space:]'), 2)
	@echo "Acessing meteoros-floripa-http shell"
	@docker exec -it meteoros-floripa-http sh
else
	@echo "Service meteoros-floripa-http is not running"
endif

http-logs: ## View logs from http server
ifeq ($(shell docker ps -f name=meteoros-floripa-http | wc -l | tr -d '[:space:]'), 2)
	@echo "Acessing meteoros-floripa-http shell"
	@docker logs -f meteoros-floripa-http
else
	@echo "Service meteoros-floripa-http is not running"
endif
