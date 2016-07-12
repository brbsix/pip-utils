.PHONY: clean package standalone

clean:
	rm -rf build/ pip_utils.egg-info/ pip-utils
	find pip_utils/ \( -name __pycache__ -o -name '*.pyc' \) -delete

package: LICENSE README.rst setup.cfg setup.py pip_utils/*.py
	python3 setup.py bdist_wheel sdist
	python2 setup.py bdist_wheel clean

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
