.PHONY: clean package pex standalone

clean:
	rm -rf build/ pip_utils.egg-info/
	find pip_utils/ \( -name __pycache__ -o -name '*.pyc' \) -delete

package: LICENSE README.rst setup.cfg setup.py pip_utils/*.py
	python3 setup.py bdist_wheel sdist
	python2 setup.py bdist_wheel clean

pex: pip_utils/*.py setup.py
	virtualenv env
	env/bin/pip install 'git+https://github.com/brbsix/pex'
	python setup.py bdist_wheel --universal
	env/bin/pex --entry-point=pip_utils.cli:main --inherit-path --output-file=pip-utils --python-shebang='#!/usr/bin/env python' dist/pip_utils-*-py2.py3-none-any.whl
	rm -rf env/ pex/ dist/pip_utils-*-py2.py3-none-any.whl
	chmod a+x pip-utils

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
