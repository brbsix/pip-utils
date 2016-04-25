# -*- coding: utf-8 -*-
"""List dependants of package"""

# Python 2 forwards-compatibility
from __future__ import absolute_import, print_function

# standard imports
from site import ENABLE_USER_SITE

# external imports
from pip import get_installed_distributions


def command_dependants(options):
    """Command launched by CLI."""
    dependants = sorted(
        get_dependants(options.package.project_name),
        key=lambda n: n.lower()
    )

    if dependants:
        print(*dependants, sep='\n')


def get_dependants(project_name):
    """Yield dependants of `project_name`."""
    for package in get_installed_distributions(user_only=ENABLE_USER_SITE):
        if is_dependant(package, project_name):
            yield package.project_name


def is_dependant(package, project_name):
    """Determine whether `package` is a dependant of `project_name`."""
    for requirement in package.requires():
        # perform case-insensitive matching
        if requirement.project_name.lower() == project_name.lower():
            return True
