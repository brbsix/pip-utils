# -*- coding: utf-8 -*-
"""Identify package that file belongs to"""

# Python 2 forwards-compatibility
from __future__ import absolute_import, print_function

# standard imports
import os
from site import ENABLE_USER_SITE

# external imports
from pip.commands.show import search_packages_info
from pip import get_installed_distributions


def command_locate(options):
    """Command launched by CLI."""
    matches = find_owners(options.file.name)

    if matches:
        print(*matches, sep='\n')


def find_owners(path):
    """Return the package(s) that file belongs to."""
    abspath = os.path.abspath(path)

    packages = search_packages_info(
        sorted((d.project_name for d in
                get_installed_distributions(user_only=ENABLE_USER_SITE)),
               key=lambda d: d.lower()))

    return [p['name'] for p in packages if is_owner(p, abspath)]


def is_owner(package, abspath):
    """Determine whether `abspath` belongs to `package`."""
    try:
        files = package['files']
        location = package['location']
    except KeyError:
        return False

    paths = (os.path.abspath(os.path.join(location, f))
             for f in files)

    return abspath in paths
