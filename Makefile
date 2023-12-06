SHELL=/bin/bash

CONFIG_DIR=config
COMMON_VARS=$(CONFIG_DIR)/common.conf

include $(COMMON_VARS)

VENV_DIR=.venv

DOC_MODE=$(FINAL_MODE)

PROFILING_XSL=$(CONFIG_DIR)/profile-$(DOC_MODE).xsl
FO_XSL=$(CONFIG_DIR)/fo-$(DOC_MODE).xsl

DBK_FILES=$(wildcard $(BOOK_DIR)/*$(BOOK_EXT))
PDF_FILES=$(patsubst $(BOOK_DIR)/%$(BOOK_EXT),$(PDF_DIR)/%.pdf,$(DBK_FILES))

#.ONESHELL:

install:
	sudo apt install python3.11-venv
	python3 -m venv ${VENV_DIR}
	source ${VENV_DIR}/bin/activate; \
	pip install --upgrade pip; \
	pip install -r scripts/requirements.txt
	sudo apt-get install herold docbook-xsl fop libxml2-utils pre-commit
	pre-commit install

format:
	source ${VENV_DIR}/bin/activate; \
	ruff format . ; \
	ruff check --select I001 --fix . ;

py:
	pre-commit run --all-files

get_com:
	source ${VENV_DIR}/bin/activate; \
	CONFIG_FILE=$(COMMON_VARS) python scripts/download_from_lesswrong.com.py > $(LOG_FILE) 2>&1

book:
	source ${VENV_DIR}/bin/activate; \
	CONFIG_FILE=$(COMMON_VARS) python scripts/html_to_docbook.py > $(LOG_FILE) 2>&1

validate:
	xmllint --noout --xinclude --noent --schema $(DOCBOOK_XSD) $(DBK_FILES) >> $(LOG_FILE) 2>&1

pdf: $(PDF_FILES)

%.pdf: %.fo
	fop -c $(FOP_CONF) -pdf $@ -fo $< >> $(LOG_FILE) 2>&1

$(PDF_DIR)/%.fo: $(BOOK_DIR)/%$(BOOK_EXT)
	xsltproc --xinclude $(PROFILING_XSL) $< | \
	xsltproc -o $@ --xinclude $(FO_XSL) - >> $(LOG_FILE) 2>&1

check_links:
	source ${VENV_DIR}/bin/activate; \
	python -u scripts/utils/check_links.py > broken_links.txt 2>$(LOG_FILE)

fop_cfg:
	source ${VENV_DIR}/bin/activate; \
	CONFIG_FILE=$(COMMON_VARS) python -u scripts/utils/fop_cfg.py 2>>$(LOG_FILE)
