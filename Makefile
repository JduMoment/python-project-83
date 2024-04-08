install: #install poetry
	poetry install
build: #build pack
	poetry build
publish: #publish pack in PyPI, dont add in catalog
	poetry publish --dry-run
package-install: #Install pack from OS
	python3 -m pip install --user dist/*.whl
package-reinstall: #reinstall pack
	python3 -m pip install --user dist/*.whl --force-reinstall
lint: #lint check
	poetry run flake8 page_analyzer
dev: #project start
	poetry run flask --app page_analyzer:app --debug run
PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app