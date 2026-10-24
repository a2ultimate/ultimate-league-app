COMPOSE := $(shell docker compose version >/dev/null 2>&1 && echo "docker compose" || echo "docker-compose")

.DEFAULT_GOAL := help

.PHONY: help up down logs shell test check build db-import prodlike clean

help: ## Show available commands
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z_-]+:.*## / {printf "%-14s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

up: ## Start the development environment
	$(COMPOSE) up --build

down: ## Stop the development environment
	$(COMPOSE) down

logs: ## Follow all service logs
	$(COMPOSE) logs --follow

shell: ## Open a shell in the backend container
	$(COMPOSE) exec backend bash

test: ## Run the Django test suite
	$(COMPOSE) exec -e DJANGO_SETTINGS_MODULE=ultimate.settings.test backend python manage.py test

check: ## Run Django checks and detect missing migrations
	$(COMPOSE) exec backend python manage.py check
	$(COMPOSE) exec backend python manage.py makemigrations --check --dry-run

build: ## Build development and production images
	$(COMPOSE) build backend backend-prod

db-import: ## Replace local data: make db-import FILE=path/to/dump.sql.gz
	@test -n "$(FILE)" || (echo "FILE is required" && exit 1)
	./bin/import-db.sh "$(FILE)"

prodlike: ## Run the production-like stack at http://localhost:8081
	$(COMPOSE) --profile prodlike up --build db backend-prod nginx

clean: ## Remove containers and all local Docker volumes
	@printf "Remove all local database, media, and dependency volumes? [y/N] "; read answer; \
		case "$$answer" in [Yy]) $(COMPOSE) down --volumes ;; *) echo "Cancelled." ;; esac