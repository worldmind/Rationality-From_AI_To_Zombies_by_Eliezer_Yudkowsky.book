SHELL=/bin/bash

CONFIG_DIR=config
COMMON_VARS=$(CONFIG_DIR)/common.conf

include $(COMMON_VARS)

VENV_DIR=.venv

DOC_MODE=$(FINAL_MODE)

PROFILING_XSL=$(CONFIG_DIR)/profile-$(DOC_MODE).xsl
FO_XSL=$(CONFIG_DIR)/fo-$(DOC_MODE).xsl
HTML_XSL=$(CONFIG_DIR)/html.xsl
CROSSLINKS_DB=olinkdb.xml
CLDB_XSL=$(CONFIG_DIR)/olinkdb.xsl

DBK_FILES=$(wildcard $(BOOK_DIR)/*$(BOOK_EXT))
PDF_FILES=$(patsubst $(BOOK_DIR)/%$(BOOK_EXT),$(PDF_DIR)/%.pdf,$(DBK_FILES))
CLDB_CHUNKS=$(patsubst $(BOOK_DIR)/%$(BOOK_EXT),%.db,$(DBK_FILES))
HTML_FILES=$(patsubst $(BOOK_DIR)/%$(BOOK_EXT),$(HTML_DIR)/%.html,$(DBK_FILES))

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

valid_book: book validate

book:
	source ${VENV_DIR}/bin/activate; \
	CONFIG_FILE=$(COMMON_VARS) python scripts/html_to_docbook.py > $(LOG_FILE) 2>&1

validate:
	xmllint --noout --xinclude --noent --schema $(DOCBOOK_XSD) $(DBK_FILES) >> $(LOG_FILE) 2>&1

pdf: $(PDF_DIR)/$(CROSSLINKS_DB) $(PDF_FILES) pdf_clean

$(PDF_DIR)/$(CROSSLINKS_DB): $(addprefix $(PDF_DIR)/,$(CLDB_CHUNKS))
	xsltproc --stringparam dbk_files "$(DBK_FILES)" \
		--stringparam target_ext ".pdf" \
		-o $@ $(CLDB_XSL) $(word 1, $(DBK_FILES)) >> $(LOG_FILE) 2>&1

$(PDF_DIR)/%.db: $(BOOK_DIR)/%$(BOOK_EXT)
	xsltproc -xinclude $(PROFILING_XSL) $< | \
	xsltproc --stringparam targets.filename "$@" \
		--stringparam collect.xref.targets "only" \
		-xinclude $(FO_XSL) - >> $(LOG_FILE) 2>&1

%.pdf: %.fo
	fop -c $(FOP_CONF) -pdf $@ -fo $< >> $(LOG_FILE) 2>&1

$(PDF_DIR)/%.fo: $(BOOK_DIR)/%$(BOOK_EXT)
	xsltproc -xinclude $(PROFILING_XSL) $< | \
	xsltproc --stringparam target.database.document "$(PDF_DIR)/$(CROSSLINKS_DB)" \
		-o $@ --xinclude $(FO_XSL) - >> $(LOG_FILE) 2>&1

pdf_clean:
	@rm $(PDF_DIR)/*.db $(PDF_DIR)/$(CROSSLINKS_DB)

html: $(HTML_DIR)/$(CROSSLINKS_DB) $(HTML_FILES) html_clean

$(HTML_DIR)/$(CROSSLINKS_DB): $(addprefix $(HTML_DIR)/,$(CLDB_CHUNKS))
	xsltproc --stringparam dbk_files "$(DBK_FILES)" \
		--stringparam target_ext ".html" \
		-o $@ $(CLDB_XSL) $(word 1, $(DBK_FILES)) >> $(LOG_FILE) 2>&1

$(HTML_DIR)/%.db: $(BOOK_DIR)/%$(BOOK_EXT)
	xsltproc -xinclude $(PROFILING_XSL) $< | \
	xsltproc --stringparam targets.filename "$@" \
		--stringparam collect.xref.targets "only" \
		-xinclude $(FO_XSL) - >> $(LOG_FILE) 2>&1

$(HTML_DIR)/%.html: $(BOOK_DIR)/%$(BOOK_EXT)
	xsltproc --xinclude $(PROFILING_XSL) $< | \
	xsltproc --stringparam target.database.document $(HTML_DIR)/$(CROSSLINKS_DB) \
		-o $@ --xinclude $(HTML_XSL) - >> $(LOG_FILE) 2>&1

html_clean:
	@rm $(HTML_DIR)/*.db $(HTML_DIR)/$(CROSSLINKS_DB)

check_links:
	source ${VENV_DIR}/bin/activate; \
	python -u scripts/utils/check_links.py > broken_links.txt 2>$(LOG_FILE)

fop_cfg:
	source ${VENV_DIR}/bin/activate; \
	CONFIG_FILE=$(COMMON_VARS) python -u scripts/utils/fop_cfg.py 2>>$(LOG_FILE)
