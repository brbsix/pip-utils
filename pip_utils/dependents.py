# -*- coding: utf-8 -*-
"""List dependents of package"""

# Python 2 forwards-compatibility
from __future__ import absolute_import, print_function

# external imports
from pip._vendor import pkg_resources


def command_dependents(options):
    """Command launched by CLI."""
    dependents = dependencies(options.package, options.recursive, options.info)

    if dependents:
        print(*dependents, sep='\n')


def dependencies(dist, recursive=False, info=False):
    """Yield distribution's dependencies."""

    def case_sorted(items):
        """Return unique list sorted in case-insensitive order."""
        return sorted(set(items), key=lambda i: i.lower())

    def requires(distribution):
        """Return the requirements for a distribution."""
        if recursive:
            req = set(pkg_resources.require(distribution.project_name))
            req.remove(distribution)
            return {r.as_requirement() for r in req}
        else:
            return distribution.requires()

    def modifier(distribution):
        """Return project's name or full requirement string."""
        return str(distribution) if info else distribution.project_name

    return case_sorted(modifier(r) for r in requires(dist))
