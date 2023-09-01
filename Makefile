SHELL=/bin/bash

VENV_DIR=.venv

#.ONESHELL:

install:
	sudo apt install python3.11-venv
	python3 -m venv ${VENV_DIR}
	source ${VENV_DIR}/bin/activate; \
	pip install --upgrade pip; \
	pip install -r scripts/requirements.txt

py:
	source ${VENV_DIR}/bin/activate; \
	python -m black .; \
	python -m ruff .

get_com:
	source ${VENV_DIR}/bin/activate; \
	python scripts/download_from_lesswrong.com.py > log.txt 2>&1
