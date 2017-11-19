MAKEFLAGS += --warn-undefined-variables
.DEFAULT_GOAL := package

PEXBUILD_BUILD_DIR := build.pex
PEXBUILD_OUTPUT_DIR := out.pex
PEXBUILD_OUTPUT_FILE := $(PEXBUILD_OUTPUT_DIR)/pip-utils.pex
PEXBUILD_PYTHON := python3
PEXBUILD_VENV_TOOL := venv
PEXBUILD_VENV_DIR := $(PEXBUILD_BUILD_DIR)/env
PEXBUILD_VENV_PYTHON := $(PEXBUILD_VENV_DIR)/bin/python
PEXBUILD_SPECIFICATION := .
PEXBUILD_PEX_REPO_URL := https://github.com/pantsbuild/pex.git
PEXBUILD_PEX_REPO_DIR := $(PEXBUILD_BUILD_DIR)/pex

ZIPBUILD_BUILD_DIR := build.zip
ZIPBUILD_OUTPUT_DIR := out.zip
ZIPBUILD_ZIP_DIR := $(ZIPBUILD_BUILD_DIR)/zip
ZIPBUILD_ZIP_FILE := $(ZIPBUILD_BUILD_DIR)/pip-utils.zip

.PHONY: clean
clean:
	rm -rf build/ pip_utils.egg-info/ $(PEXBUILD_BUILD_DIR) $(ZIPBUILD_BUILD_DIR)
	find . -type f -name '*.pyc' -delete
	find . -type d -name __pycache__ -delete

.PHONY: package
package: LICENSE README.rst setup.cfg setup.py pip_utils/*.py
	python3 setup.py bdist_wheel sdist
	python2 setup.py bdist_wheel clean

.PHONY: pex
pex: pip_utils/*.py setup.py
	rm -rf -- $(PEXBUILD_BUILD_DIR)
	mkdir -- $(PEXBUILD_BUILD_DIR) $(PEXBUILD_BUILD_DIR)/egg
	$(PEXBUILD_PYTHON) -m $(PEXBUILD_VENV_TOOL) $(PEXBUILD_VENV_DIR)
	git clone --depth=1 $(PEXBUILD_PEX_REPO_URL) $(PEXBUILD_PEX_REPO_DIR)
	git apply --directory $(PEXBUILD_PEX_REPO_DIR) --verbose fix_pex_import_order.patch
	$(PEXBUILD_VENV_PYTHON) -m pip install -U pip
	$(PEXBUILD_VENV_PYTHON) -m pip install -U $(PEXBUILD_PEX_REPO_DIR)[cachecontrol,requests]
	$(PEXBUILD_VENV_PYTHON) setup.py setopt -c bdist_wheel -o universal -s 1
	$(PEXBUILD_VENV_PYTHON) setup.py setopt -c egg_info -o egg-base -s $(PEXBUILD_BUILD_DIR)/egg
	$(PEXBUILD_VENV_PYTHON) -m pex.bin.pex $(PEXBUILD_SPECIFICATION) --disable-cache --entry-point=pip_utils --inherit-path --output-file=$(PEXBUILD_OUTPUT_FILE) --python-shebang='/usr/bin/env python'
	$(PEXBUILD_VENV_PYTHON) setup.py setopt -c bdist_wheel -o universal -r
	$(PEXBUILD_VENV_PYTHON) setup.py setopt -c egg_info -o egg-base -r

.PHONY: standalone
standalone: pip_utils/*.py
	rm -rf -- $(ZIPBUILD_BUILD_DIR)
	pip install --no-compile --only-binary :all: --target $(ZIPBUILD_ZIP_DIR) .
	cp pip_utils/__main__.py $(ZIPBUILD_ZIP_DIR)
	cd $(ZIPBUILD_ZIP_DIR) && zip -9r ../pip-utils .
	mkdir -- $(ZIPBUILD_OUTPUT_DIR)
	cd $(ZIPBUILD_OUTPUT_DIR) && \
	  for v in '' 2 3; do \
	    echo '#!/usr/bin/env python'"$$v" > "pip$$v-utils.standalone" && \
	    cat ../$(ZIPBUILD_ZIP_FILE) >> "pip$$v-utils.standalone" && \
	    chmod -v +x "pip$$v-utils.standalone"; \
	  done
