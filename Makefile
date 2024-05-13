install: #install poetry
	poetry install
lint: #lint check
	poetry run flake8 page_analyzer
dev: #project start
	poetry run flask --app page_analyzer:app --debug run
PORT ?= 5432
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app
build:
	./build.sh