# -*- coding: utf-8 -*-
"""List packages lacking dependants"""

# Python 2 forwards-compatibility
from __future__ import absolute_import, print_function

# standard imports
from site import ENABLE_USER_SITE

# external imports
from pip import get_installed_distributions
from pip._vendor.pkg_resources import get_distribution


# pylint: disable=unused-argument
def command_parents(options):
    """Command launched by CLI."""
    parents = get_parents()

    if parents:
        print(*parents, sep='\n')


def get_parents():
    """Return sorted list of names of packages without dependants."""
    distributions = get_installed_distributions(user_only=ENABLE_USER_SITE)
    remaining = {d.project_name.lower() for d in distributions}
    requirements = {r.project_name.lower() for d in distributions for
                    r in d.requires()}

    return get_realnames(remaining - requirements)


def get_realnames(packages):
    """
    Return list of unique case-correct package names.

    Packages are listed in a case-insensitive sorted order.
    """
    return sorted({get_distribution(p).project_name for p in packages},
                  key=lambda n: n.lower())
