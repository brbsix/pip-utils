MAKEFLAGS += --warn-undefined-variables
.DEFAULT_GOAL := all

BUILD_DATE := $(shell date +%Y%m%d%H%M)

DISTBUILD_BUILD_DIRS := ./*.egg-info/ .eggs/ build/
DISTBUILD_OUTPUT_DIR := dist

PEXBUILD_BUILD_DIR := build.pex
PEXBUILD_OUTPUT_DIR := dist.pex
PEXBUILD_PYTHON := python3
PEXBUILD_SPECIFICATION := .
PEXBUILD_VENV_DIR := $(PEXBUILD_BUILD_DIR)/env
PEXBUILD_VENV_PYTHON := $(PEXBUILD_VENV_DIR)/bin/python
PEXBUILD_VENV_TOOL := venv

ZIPBUILD_BUILD_DIR := build.zip
ZIPBUILD_OUTPUT_DIR := dist.zip
ZIPBUILD_PYTHON := python3
ZIPBUILD_ZIP_DIR := $(ZIPBUILD_BUILD_DIR)/zip
ZIPBUILD_ZIP_FILE := $(ZIPBUILD_BUILD_DIR)/pip-utils.zip

.PHONY: clean
clean:
	rm -rf -- $(DISTBUILD_BUILD_DIRS) $(PEXBUILD_BUILD_DIR) $(ZIPBUILD_BUILD_DIR)
	find . -type f -name '*.pyc' -delete
	find . -type d -name __pycache__ -delete

.PHONY: distclean
distclean:
	rm -- ./*.pex ./*.standalone
	rm -rf -- $(DISTBUILD_OUTPUT_DIR) $(PEXBUILD_OUTPUT_DIR) $(ZIPBUILD_OUTPUT_DIR)

.PHONY: all
all: package pex standalone

.PHONY: package
package: LICENSE README.rst setup.cfg setup.py pip_utils/*.py
	python3 setup.py bdist_wheel sdist
	python2 setup.py bdist_wheel clean

.PHONY: pex
pex: pip_utils/*.py setup.py
	$(eval PEXBUILD_VERSION := $(shell $(PEXBUILD_PYTHON) setup.py --version))
	rm -rf -- $(PEXBUILD_BUILD_DIR)
	$(PEXBUILD_PYTHON) -m $(PEXBUILD_VENV_TOOL) $(PEXBUILD_VENV_DIR)
	$(PEXBUILD_VENV_PYTHON) -m pip install -U pip
	$(PEXBUILD_VENV_PYTHON) -m pip install -U 'pex[cachecontrol,requests]>=1.3.1'
	$(PEXBUILD_VENV_PYTHON) setup.py setopt -c bdist_wheel -o universal -s 1
	$(PEXBUILD_VENV_PYTHON) setup.py setopt -c egg_info -o egg-base -s $(PEXBUILD_BUILD_DIR)/egg
	mkdir -- $(PEXBUILD_BUILD_DIR)/egg
	$(PEXBUILD_VENV_PYTHON) -m pex.bin.pex $(PEXBUILD_SPECIFICATION) --disable-cache --entry-point=pip_utils --inherit-path=fallback --output-file=$(PEXBUILD_OUTPUT_DIR)/pip-utils-$(PEXBUILD_VERSION)_$(BUILD_DATE) --python-shebang='/usr/bin/env python'
	$(PEXBUILD_VENV_PYTHON) setup.py setopt -c bdist_wheel -o universal -r
	$(PEXBUILD_VENV_PYTHON) setup.py setopt -c egg_info -o egg-base -r

.PHONY: standalone
standalone: pip_utils/*.py
	$(eval ZIPBUILD_VERSION := $(shell $(ZIPBUILD_PYTHON) setup.py --version))
	rm -rf -- $(ZIPBUILD_BUILD_DIR)
	$(ZIPBUILD_PYTHON) -m pip install --no-compile --only-binary :all: --target $(ZIPBUILD_ZIP_DIR) .
	cp pip_utils/__main__.py $(ZIPBUILD_ZIP_DIR)
	cd $(ZIPBUILD_ZIP_DIR) && zip -9r ../pip-utils .
	mkdir -p -- $(ZIPBUILD_OUTPUT_DIR)
	cd $(ZIPBUILD_OUTPUT_DIR) && \
	  for v in '' 2 3; do \
	    echo '#!/usr/bin/env python'"$$v" > "pip$$v-utils-$(ZIPBUILD_VERSION)_$(BUILD_DATE)" && \
	    cat ../$(ZIPBUILD_ZIP_FILE) >> "pip$$v-utils-$(ZIPBUILD_VERSION)_$(BUILD_DATE)" && \
	    chmod -v +x "pip$$v-utils-$(ZIPBUILD_VERSION)_$(BUILD_DATE)"; \
	  done
