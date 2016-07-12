# -*- coding: utf-8 -*-
"""
Entrypoint module, in case you use `python -m pip_utils`.

Why does this file exist, and why __main__? For more info, read:

- https://www.python.org/dev/peps/pep-0338/
- https://docs.python.org/2/using/cmdline.html#cmdoption-m
- https://docs.python.org/3/using/cmdline.html#cmdoption-m
"""

# Python 2 forwards-compatibility
from __future__ import absolute_import

# standard imports
import os
import sys


# include pip wheel in standalone zip
if __package__ is '':
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.realpath(
        os.path.abspath(__file__))), 'pip-8.1.2-py2.py3-none-any.whl'))

if __name__ == '__main__':
    from pip_utils.cli import main
    sys.exit(main())
