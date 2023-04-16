help:
	@echo usage: make "<target>"
	@echo args:
	@echo - target: install, update, lint, format, clean

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
	@rm -fr .mypy_cache .pytest_cache .venv
