install:
	uv sync

dev:
	uv run flask --debug --app page_analyzer:app run

lint:
	uv run ruff check page_analyzer

test:
	uv run pytest

#build:
#	uv build

test-coverage:
	uv run pytest --cov=page_analyzer tests --cov-report xml

build:
	./build.sh

render-start:
	gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app


#package-install:
#	uv tool install dist/*.whl

#publish:
#	uv run poetry publish --dry-run

PORT ?= 8000

start:
	uv run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app
