install: #install poetry
	poetry install
publish: #publish pack in PyPI, dont add in catalog
	poetry publish --dry-run
package-install: #Install pack from OS
	python3 -m pip install --user dist/*.whl
package-reinstall: #reinstall pack
	python3 -m pip install --user dist/*.whl --force-reinstall
lint: #lint check
	poetry run flake8 hexlet-code
dev: #project start
	poetry run flask --app hexlet-code:app --debug run
PORT ?= 5432
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) hexlet-code:app
build:
	./build.sh