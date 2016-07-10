# -*- coding: utf-8 -*-
"""
Application setup script

To build package:
python3 setup.py bdist_wheel sdist
python2 setup.py bdist_wheel clean

To run tests in an virtualenv:
python setup.py test

To run tests directly with verbose output:
python -m pytest -vv
"""

# Python 2 forwards-compatibility
from __future__ import absolute_import

# standard imports
import io
import os
import re
import sys

# external imports
from setuptools import setup

# application imports
from pip_utils import __description__, __program__, __version__


def long_description():
    """Return the contents of README.rst (with badging removed)."""
    # use re.compile() for flags support in Python 2.6
    pattern = re.compile(r'\n^\.\. start-badges.*^\.\. end-badges\n',
                         flags=re.M | re.S)
    return pattern.sub('', read('README.rst'))


def read(*names, **kwargs):
    """Return contents of text file (in the same directory as this file)."""
    return io.open(
        os.path.join(os.path.dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()


SETUP_REQUIRES = ['pytest-runner'] if \
    {'ptr', 'pytest', 'test'}.intersection(sys.argv) else []
INSTALL_REQUIRES = ['pip>=8.0.0']
TESTS_REQUIRE = ['pytest-pylint']  # Python 2.7 & 3.3+ only

setup(
    name=__program__,
    version=__version__,
    description=__description__,
    author='Brian Beffa',
    author_email='brbsix@gmail.com',
    long_description=long_description(),
    url='https://github.com/brbsix/pip-utils',
    license='GPLv3',
    keywords=['package', 'packaging', 'pip', 'PyPi'],
    packages=['pip_utils'],
    install_requires=INSTALL_REQUIRES,
    setup_requires=SETUP_REQUIRES,
    tests_require=TESTS_REQUIRE,
    extras_require={'testing': TESTS_REQUIRE},
    entry_points={
        'console_scripts': [
            'pip{v}-utils=pip_utils.cli:main'.format(
                v=sys.version_info[0])  # not a named tuple in Python 2.6
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: System',
        'Topic :: System :: Software Distribution',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities'
    ]
)
