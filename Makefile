# ==================================================================================== #
# HELPERS
# ==================================================================================== #

## help: print this help message
.PHONY: help
help:
	@echo 'Usage:'
	@sed -n 's/^##//p' ${MAKEFILE_LIST} | column -t -s ':' |  sed -e 's/^/ /'

# ==================================================================================== #
# DEVELOPMENT
# ==================================================================================== #

## install: install the dependencies
.PHONY: install
install:
	uv sync

## test: run the tests
.PHONY: test
test:
	PYTHONPATH=.:./tests uv run pytest

# ==================================================================================== #
# DATABASE
# ==================================================================================== #

## makemigration: create a new migration
.PHONY: makemigration
makemigration:
	uv run scripts/makemigration.py $(comment)

## migrate: apply the migrations
.PHONY: migrate
migrate:
	uv run scripts/migrate.py

## unmigrate: revert the migrations
.PHONY: unmigrate
unmigrate:
	uv run scripts/unmigrate.py

# ==================================================================================== #
# DOCKER
# ==================================================================================== #

## build-server: build the server image
.PHONY: build-server
build-server:
	docker build -f dockerfile.server -t server .

## build-worker: build the worker image
.PHONY: build-worker
build-worker:
	docker build -f dockerfile.worker -t worker .

## build: build all docker images
.PHONY: build
build:
	docker compose build

## compose: start the services
.PHONY: up
up:
	docker compose up

## down: stop the services
.PHONY: down
down:
	docker compose down


## clean: remove Docker images
.PHONY: clean
clean:
	docker compose down --rmi all

# ==================================================================================== #
# LOCAL
# ==================================================================================== #

## run-server: run the server
.PHONY: run-server
run-server:
	PYTHONPATH=. uv run server/main.py

## run-worker: run the worker
.PHONY: run-worker
run-worker:
	PYTHONPATH=. uv run worker/main.py
