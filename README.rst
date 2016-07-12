=========
pip-utils
=========

.. start-badges

|version| |license| |wheel| |supported-versions|

.. |version| image:: https://img.shields.io/pypi/v/pip-utils.svg
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/pip-utils

.. |license| image:: https://img.shields.io/pypi/l/pip-utils.svg
    :alt: License
    :target: https://pypi.python.org/pypi/pip-utils

.. |wheel| image:: https://img.shields.io/pypi/wheel/pip-utils.svg
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/pip-utils

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/pip-utils.svg
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/pip-utils

.. end-badges

Helper utilities for pip.


Installation
============

Download from PyPI:

::

    pip install --user pip-utils

pip-utils is also available here_ as a ZIP application [0]_. Once you've download it, you can install it to a directory on your PATH:

::

    install pip-utils ~/.local/bin


Usage
=====

::

    usage: pip3-utils [-h] [--version]
                      {dependants,dependents,locate,outdated,parents} ...

    Helper utilities for pip.

    positional arguments:
      {dependants,dependents,locate,outdated,parents}
        dependants          list dependants of package
        dependents          list dependents of package
        locate              identify package that file belongs to
        outdated            list outdated packages that may be updated
        parents             list packages lacking dependants

    optional arguments:
      -h, --help            show this help message and exit
      --version             show program's version number and exit

    See `pip3-utils COMMAND --help` for help on a specific subcommand.

For Python 2, use ``pip2-utils``. For Python 3, use ``pip3-utils``. Or, use ``python -m pip_utils``.

If you've installed the standalone executable on your PATH, your can call ``pip-utils``. Or run it directly with the Python interpreter of your choice, e.g. ``python3.5 ~/.local/bin/pip-utils``.

By default, pip-utils will interact with packages installed to the user site (assuming the user site is available). To disable this behavior, call pip-utils with Python's ``-s`` option (i.e. ``python -sm pip_utils``) or ``PYTHONNOUSERSITE`` environment variable (i.e. ``PYTHONNOUSERSITE=1 python -m pip_utils``).


Commands
========

dependants
----------

List dependants of a package:

::

    $ pip3-utils dependants pexpect
    ipython

dependents
----------

List direct dependents of a package:

::

    $ pip3-utils dependents ipython
    backports.shutil-get-terminal-size
    decorator
    pexpect
    pickleshare
    setuptools
    simplegeneric
    traitlets

List direct dependents of a package with their version requirements:

::

    $ pip3-utils dependents -i dataset
    alembic>=0.6.2
    normality>=0.2.2
    PyYAML>=3.10
    six
    six>=1.7.3
    sqlalchemy>=0.9.1

List all dependencies of a package recursively:

::

    $ pip3-utils dependents -r dataset
    alembic
    Mako
    MarkupSafe
    normality
    python-editor
    PyYAML
    six
    SQLAlchemy

locate
------

Identify package(s) that file belongs to:

::

    $ pip3-utils locate ~/.local/bin/symilar
    pylint

outdated
--------

List outdated packages that may be updated. This differ's from pip's ``--outdated`` flag in that it verifies that there are no conflicting dependencies that would otherwise make an update inadvisable.

::

    pip3-utils outdated

List all outdated packages. Note, this is equivalent to pip's ``--outdated`` flag.

::

    pip3-utils outdated --all

List outdated packages unable to be updated due to dependency requirements:

::

    pip3-utils outdated --pinned

Update all outdated packages that may be updated.

::

    pip3-utils outdated --upgrade

parents
-------

List packages lacking dependants:

::

    pip3-utils parents


Development
===========

To run tests (automatically pulling in dependencies):

::

    python setup.py test

To run tests directly, with verbose output:

::

    python3 -m pytest -vv


License
=======

Copyright (c) 2016 Six (brbsix@gmail.com).

Licensed under the GPLv3 license.

.. [0] https://bugs.python.org/issue1739468
.. _here: https://github.com/brbsix/pip-utils/releases/latest
