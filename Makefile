SHELL=/bin/bash

VENV_DIR=.venv

FINAL_MODE=final
DRAFT_MODE=draft

DOC_MODE=$(FINAL_MODE)
BOOK_DIR=lesswrong.com/book.english
BOOK_EXT=.dbk
LOG_FILE=log.txt
XSL_DIR=xsl
DOCBOOK_XSD=/usr/share/xml/docbook/schema/xsd/5.0/docbook.xsd
FOP_CFG=config/fop.xml

DBK_FILES=$(wildcard $(BOOK_DIR)/*$(BOOK_EXT))
PDF_FILES=$(subst $(BOOK_EXT),.pdf,$(DBK_FILES))

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
	python scripts/download_from_lesswrong.com.py > $(LOG_FILE) 2>&1

book:
	source ${VENV_DIR}/bin/activate; \
	python scripts/html_to_docbook.py > $(LOG_FILE) 2>&1

validate:
	xmllint --noout --xinclude --noent --schema $(DOCBOOK_XSD) $(DBK_FILES) >> $(LOG_FILE) 2>&1

pdf: $(PDF_FILES)

%.pdf: %.fo
	fop -c $(FOP_CFG) -pdf $@ -fo $< >> $(LOG_FILE) 2>&1

%.fo: %$(BOOK_EXT)
	xsltproc --xinclude $(XSL_DIR)/profile-$(DOC_MODE).xsl $< | \
	xsltproc -o $@ --xinclude $(XSL_DIR)/fo-$(DOC_MODE).xsl - >> $(LOG_FILE) 2>&1

check_links:
	source ${VENV_DIR}/bin/activate; \
	python -u scripts/utils/check_links.py > broken_links.txt 2>$(LOG_FILE)

fop_cfg:
	source ${VENV_DIR}/bin/activate; \
	python -u scripts/utils/fop_cfg.py 2>>$(LOG_FILE)
