#!make
include .env
export $(shell sed 's/=.*//' .env)

install:
	poetry install

setup-db:
	docker compose up -d && bash wait-for-healthy-container.sh db 30
	make migrate

dev:
	make setup-db
	poetry run uvicorn python_rest_template.main:app --reload

build:
	docker build -t ${APP_IMAGE_TAG} .

run:
	make build
	docker compose -f docker-compose.yaml -f docker-compose.integration.yaml up -d  && bash wait-for-healthy-container.sh app 30
	make migrate

cleanup:
	docker rm -f $(docker ps -a -q) && \
 	docker volume rm $(docker volume ls -q)

test:
	poetry run pytest

watch:
	poetry run pytest -f --ff -x --color=yes

this:
	poetry run pytest -f -k='${test}'

lint:
	poetry run flake8 decilo_core/ && poetry run black decilo_core/ --check


add-migration:
	poetry run yoyo new -m ${name} --sql

migrate:
	poetry run yoyo apply --batch --no-config-file --database postgresql://${TARGET_DB_USER}:${TARGET_DB_PW}@${TARGET_DB_HOSTNAME}/${TARGET_DB} python_rest_template/database/migration/migration_files