help:
	@grep "^[a-zA-Z\-]*:" Makefile | grep -v "grep" | sed -e 's/^/make /' | sed -e 's/://'

install:
	@echo -------------------- install packages ----------------------------------------------------
	@poetry install

update:
	@echo -------------------- update packages -----------------------------------------------------
	@poetry update

lint:
	@echo -------------------- run pflake8 to check grammar ----------------------------------------
	@poetry run pflake8 .
	@echo -------------------- run mypy to check type ----------------------------------------------
	@poetry run mypy .
	@echo -------------------- run isort to check import statement ---------------------------------
	@poetry run isort --check .
	@echo -------------------- run black to check code ---------------------------------------------
	@poetry run black --check .

format:
	@echo -------------------- run isort to format import statement --------------------------------
	@poetry run isort .
	@echo -------------------- run black to format code ---------------------------------------------
	@poetry run black .

clean:
	@echo -------------------- clean package -------------------------------------------------------
	@find . | grep .venv$ | xargs rm -fr
	@find . | grep .mypy_cache$ | xargs rm -fr
	@find . | grep .pytest_cache$ | xargs rm -fr
	@find . | grep __pycache__$ | xargs rm -fr
