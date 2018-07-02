.DEFAULT_GOAL := help
SHELL := /bin/bash

APP_NAME ?= re-observe-aws-exporter

DOCKER_CONTAINER_PREFIX = ${USER}-${BUILD_TAG}

DOCKER_IMAGE = kenlt/${APP_NAME}
DOCKER_IMAGE_TAG = ${CF_SPACE}
DOCKER_IMAGE_NAME = ${DOCKER_IMAGE}:${DOCKER_IMAGE_TAG}
DOCKER_TTY ?= $(if ${JENKINS_HOME},,t)

PORT ?= 5100

.PHONY: help
help:
	@cat $(MAKEFILE_LIST) | grep -E '^[a-zA-Z_-]+:.*?## .*$$' | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: bootstrap
bootstrap: ## run bootstrap
	./scripts/bootstrap.sh

.PHONY: run-app
run-app: ## run app
	./scripts/run_app.sh

.PHONY: run-tests
run-tests: ## run tests
	./scripts/run_tests.sh

define run_docker_container
	docker run -i${DOCKER_TTY} --rm \
		--name "${DOCKER_CONTAINER_PREFIX}-${1}" \
		-p ${PORT}:${PORT} \
		-e FLASK_APP=${FLASK_APP} \
		-e FLASK_DEBUG=${FLASK_DEBUG} \
		-e WERKZEUG_DEBUG_PIN=${WERKZEUG_DEBUG_PIN} \
		-e BUILD_NUMBER=${BUILD_NUMBER} \
		-e BUILD_URL=${BUILD_URL} \
		-e APP_NAME=${APP_NAME} \
		-e PORT=${PORT} \
		-e http_proxy="${HTTP_PROXY}" \
		-e HTTP_PROXY="${HTTP_PROXY}" \
		-e https_proxy="${HTTPS_PROXY}" \
		-e HTTPS_PROXY="${HTTPS_PROXY}" \
		-e NO_PROXY="${NO_PROXY}" \
		${DOCKER_IMAGE_NAME} \
		${2}
endef

# ---- DOCKER COMMANDS ---- #

.PHONY: run-with-docker
run-with-docker: prepare-docker-build-image ## Build inside a Docker container
	$(call run_docker_container,build, make run_app)

.PHONY: bash-with-docker
bash-with-docker: prepare-docker-build-image ## Build inside a Docker container
	$(call run_docker_container,build, bash)

.PHONY: prepare-docker-build-image
prepare-docker-build-image: ## Build docker image
	docker build -f docker/Dockerfile \
		--build-arg http_proxy="${http_proxy}" \
		--build-arg https_proxy="${https_proxy}" \
		--build-arg NO_PROXY="${NO_PROXY}" \
		--build-arg PORT=${PORT} \
		-t ${DOCKER_IMAGE_NAME} \
		.

.PHONY: clean-docker-containers
clean-docker-containers: ## Clean up any remaining docker containers
	docker rm -f $(shell docker ps -q -f "name=${DOCKER_CONTAINER_PREFIX}") 2> /dev/null || true
