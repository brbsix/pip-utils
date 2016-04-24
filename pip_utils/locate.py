# -*- coding: utf-8 -*-
"""Identify package that file belongs to"""

# Python 2 forwards-compatibility
from __future__ import absolute_import, print_function

# standard imports
import os

# external imports
from pip.commands.show import search_packages_info
from pip import get_installed_distributions


def command_locate(options):
    """Command launched by CLI."""
    match = find_owner(options.file.name)

    if match is not None:
        print(match)


def find_owner(path):
    """Return the package that file belongs to."""
    abspath = os.path.abspath(path)

    packages = search_packages_info(
        sorted((d.project_name for d in
                get_installed_distributions(user_only=True)),
               key=lambda d: d.lower()))

    for package in packages:
        try:
            files = package['files']
            location = package['location']
            name = package['name']
        except KeyError:
            continue

        paths = (os.path.abspath(os.path.join(location, f))
                 for f in files)

        if abspath in paths:
            return name
