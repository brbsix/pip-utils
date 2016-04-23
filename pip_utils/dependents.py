# -*- coding: utf-8 -*-
"""List dependents of package"""

# Python 2 forwards-compatibility
from __future__ import absolute_import, print_function

# external imports
import pkg_resources


def case_sorted(items):
    """
    Return sorted list of unique case-correct items.

    Packages are listed in a case-insensitive sorted order.
    """

    return sorted({i for i in items}, key=lambda i: i.lower())


def command_dependents(options):
    """Command launched by CLI."""
    depends = dependencies(options.package, options.recursive, options.info)

    if depends:
        print(*depends, sep='\n')


def dependencies(dist, recursive=False, info=False):
    """Yield distribution's dependencies."""

    def modifier(distribution):
        """Return project's name or full requirement string."""
        return str(distribution) if info else distribution.project_name

    if recursive:
        requires = set(pkg_resources.require(dist.project_name))
        requires.remove(dist)
        requires = {r.as_requirement() for r in requires}
    else:
        requires = dist.requires()

    return case_sorted(modifier(r) for r in requires)
