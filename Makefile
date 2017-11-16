MAKEFLAGS += --warn-undefined-variables
.DEFAULT_GOAL := package

PEXBUILD_PYTHON := python3
PEXBUILD_OUTPUT := pip-utils.pex
PEXBUILD_SPECIFICATION := .

.PHONY: clean
clean:
	rm -rf build/ pip_utils.egg-info/
	find . -type f -name '*.pyc' -delete
	find . -type d -name __pycache__ -delete

.PHONY: package
package: LICENSE README.rst setup.cfg setup.py pip_utils/*.py
	python3 setup.py bdist_wheel sdist
	python2 setup.py bdist_wheel clean

.PHONY: pex
pex: pip_utils/*.py setup.py
	$(PEXBUILD_PYTHON) -m venv env
	env/bin/pip install -U pip setuptools
	env/bin/pip install -U 'pex[cachecontrol,requests]'
	patch -N "$$(env/bin/python -c 'import pex.environment; print(pex.environment.__file__)')" fix_pex_import_order.patch || :
	env/bin/pex $(PEXBUILD_SPECIFICATION) --disable-cache --entry-point=pip_utils --inherit-path --output-file=$(PEXBUILD_OUTPUT) --python=python2 --python=python3 --python-shebang='#!/usr/bin/env python'
	rm -rf *.egg-info/

.PHONY: standalone
standalone: pip_utils/*.py
	pip install --target . pip==8.1.2
	zip --quiet pip-utils pip_utils/*.py --exclude pip_utils/__main__.py
	zip --quiet pip-utils -r pip/ pip-8.1.2.dist-info/ --exclude '*.pyc' --exclude '*/__pycache__/*'
	zip --quiet --junk-paths pip-utils pip_utils/__main__.py
	rm -rf pip/ pip-8.1.2.dist-info/
	echo '#!/usr/bin/env python' > pip-utils.standalone
	cat pip-utils.zip >> pip-utils.standalone
	echo '#!/usr/bin/env python2' > pip2-utils.standalone
	cat pip-utils.zip >> pip2-utils.standalone
	echo '#!/usr/bin/env python3' > pip3-utils.standalone
	cat pip-utils.zip >> pip3-utils.standalone
	rm pip-utils.zip
	chmod a+x pip-utils.standalone pip2-utils.standalone pip3-utils.standalone
