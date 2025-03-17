# Local variables
PWD=$(shell pwd)

# HELP
# This will output the help for each task
# thanks to https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help
.DEFAULT_GOAL := help

help: ## This help.
	@awk 'BEGIN {FS = ":.*##"; printf "\n\u2605 Usage:\n \033[32m make \033[0m\033[36m<target> [params]\033[0m\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } '  $(MAKEFILE_LIST)

http-up: ## Start http server
ifeq ($(shell docker ps -f name=meteoros-floripa-http | wc -l | tr -d '[:space:]'), 1)
	@echo "Starting http service"
	@docker run \
		--rm \
		--name meteoros-floripa-http \
		-v $(PWD):/usr/src/app \
		-e JEKYLL_ENV="development" \
		-p 4000:4000 \
		-d starefossen/github-pages
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
