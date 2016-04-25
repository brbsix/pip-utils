# -*- coding: utf-8 -*-
"""List dependents of package"""

# Python 2 forwards-compatibility
from __future__ import absolute_import, print_function

# external imports
import pkg_resources


def command_dependents(options):
    """Command launched by CLI."""
    dependents = dependencies(options.package, options.recursive, options.info)

    if dependents:
        print(*dependents, sep='\n')


def dependencies(dist, recursive=False, info=False):
    """Yield distribution's dependencies."""

    def case_sorted(items):
        """Return unique list sorted in case-insensitive order."""
        return sorted({i for i in items}, key=lambda i: i.lower())

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
