#!make
include .env
export $(shell sed 's/=.*//' .env)

install:
	poetry install

dev:
	skaffold dev -p dev --port-forward

build:
	skaffold build

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
