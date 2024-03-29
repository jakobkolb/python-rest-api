#!make
include .env
export $(shell sed 's/=.*//' .env)

install:
	poetry install

setup-db:
	docker compose -f docker/docker-compose.yaml up -d && bash docker/wait-for-healthy-container.sh db 30
	make migrate

dev:
	make setup-db
	poetry run uvicorn src.main:app --reload --port 8080

build:
	docker build -t ${APP_IMAGE_TAG} -f docker/Dockerfile .

run:
	make build
	docker compose -f docker/docker-compose.yaml -f docker/docker-compose.integration.yaml up -d  && bash docker/wait-for-healthy-container.sh app 30

run-interactive:
	make build
	docker compose -f docker/docker-compose.yaml -f docker/docker-compose.integration.yaml up

teardown:
	docker compose -f docker/docker-compose.yaml -f docker/docker-compose.integration.yaml down -v

cleanup:
	docker rm -f $(docker ps -a -q) && \
 	docker volume rm $(docker volume ls -q)

test:
	poetry run pytest -k='not integration_test'

integration-test:
	poetry run pytest -k='integration_test'

watch:
	poetry run pytest -f --ff -x --color=yes

this:
	poetry run pytest -f -k='${test}'

lint:
	poetry run flake8 src/ && poetry run black src/ --check


add-migration:
	poetry run yoyo new -m ${name} --sql

migrate:
	poetry run yoyo apply --batch --no-config-file --database postgresql://${DB_USER}:${DB_PASSWORD}@${DB_HOSTNAME}/${DB_NAME} src/database/migration/migration_files