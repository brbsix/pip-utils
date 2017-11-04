.PHONY: clean package pex standalone

clean:
	rm -rf build/ pip_utils.egg-info/
	find . -type f -name '*.pyc' -delete
	find . -type d -name __pycache__ -delete

package: LICENSE README.rst setup.cfg setup.py pip_utils/*.py
	python3 setup.py bdist_wheel sdist
	python2 setup.py bdist_wheel clean

pex: pip_utils/*.py setup.py
	python3 -m venv env
	env/bin/pip install -U pip setuptools
	env/bin/pip install -U 'pex[requests]'
	env/bin/pex . --disable-cache --entry-point=pip_utils.cli:main --inherit-path --output-file=pip-utils --python=python2 --python=python3 --python-shebang='#!/usr/bin/env python'
	rm -rf *.egg-info/

standalone: pip_utils/*.py
	pip install --target . pip==8.1.2
	zip --quiet pip-utils pip_utils/*.py --exclude pip_utils/__main__.py
	zip --quiet pip-utils -r pip/ pip-8.1.2.dist-info/
	zip --quiet --junk-paths pip-utils pip_utils/__main__.py
	rm -rf pip/ pip-8.1.2.dist-info/
	echo '#!/usr/bin/env python' > pip-utils
	cat pip-utils.zip >> pip-utils
	rm pip-utils.zip
	chmod a+x pip-utils
