# -*- coding: utf-8 -*-
"""Command-line application"""

# Python 2 forwards-compatibility
from __future__ import absolute_import

# standard imports
import argparse
import sys

# external imports
from pkg_resources import DistributionNotFound, get_distribution

# application imports
from . import __description__, __version__
from .dependants import command_dependants
from .dependents import command_dependents
from .locate import command_locate
from .outdated import command_outdated
from .parents import command_parents


def _distribution(value):
    """Ensure value is the name of an installed distribution."""
    try:
        return get_distribution(value)
    except DistributionNotFound:
        raise argparse.ArgumentTypeError('invalid package: %r' % value)


def _parser():
    """Parse command-line options."""
    launcher = 'pip%s-utils' % sys.version_info.major

    parser = argparse.ArgumentParser(
        add_help=False,
        description='%s.' % __description__,
        prog=launcher)

    subparsers = parser.add_subparsers()

    # dependants
    parser_dependants = subparsers.add_parser(
        'dependants',
        add_help=False,
        help='list dependants of package')
    parser_dependants.add_argument(
        'package',
        metavar='PACKAGE',
        type=_distribution)
    parser_dependants.add_argument(
        '-h', '--help',
        action='help',
        help=argparse.SUPPRESS)
    parser_dependants.set_defaults(
        func=command_dependants)

    # dependents
    parser_dependents = subparsers.add_parser(
        'dependents',
        add_help=False,
        help='list dependents of package')
    parser_dependents.add_argument(
        'package',
        metavar='PACKAGE',
        type=_distribution)
    parser_dependents.add_argument(
        '-i', '--info',
        action='store_true',
        help='show version requirements')
    parser_dependents.add_argument(
        '-r', '--recursive',
        action='store_true',
        help='list dependencies recursively')
    parser_dependents.add_argument(
        '-h', '--help',
        action='help',
        help=argparse.SUPPRESS)
    parser_dependents.set_defaults(
        func=command_dependents)

    # locate
    parser_locate = subparsers.add_parser(
        'locate',
        add_help=False,
        help='identify package that file belongs to')
    parser_locate.add_argument(
        'file',
        metavar='FILE',
        type=argparse.FileType('r'))
    parser_locate.add_argument(
        '-h', '--help',
        action='help',
        help=argparse.SUPPRESS)
    parser_locate.set_defaults(
        func=command_locate)

    # outdated
    parser_outdated = subparsers.add_parser(
        'outdated',
        add_help=False,
        help='list outdated user packages that may be updated')
    parser_outdated.add_argument(
        '-b', '--brief',
        action='store_true',
        help='show package name only')
    group = parser_outdated.add_mutually_exclusive_group()
    group.add_argument(
        '-a', '--all',
        action='store_true',
        help='list all outdated user packages')
    group.add_argument(
        '-p', '--pinned',
        action='store_true',
        help='list outdated user packages unable to be updated')
    parser_outdated.add_argument(
        '-h', '--help',
        action='help',
        help=argparse.SUPPRESS)
    parser_outdated.set_defaults(
        func=command_outdated)

    # parents
    parser_parents = subparsers.add_parser(
        'parents',
        add_help=False,
        help='list packages lacking dependants')
    parser_parents.add_argument(
        '-h', '--help',
        action='help',
        help=argparse.SUPPRESS)
    parser_parents.set_defaults(
        func=command_parents)

    pgroup = parser.add_argument_group('program options')
    pgroup.add_argument(
        '-h', '--help',
        action='help',
        help=argparse.SUPPRESS)
    pgroup.add_argument(
        '--version',
        action='version',
        help=argparse.SUPPRESS,
        version='%(prog)s ' + __version__)

    return parser


def main(args=None):
    """Start application."""
    parser = _parser()
    options = parser.parse_args(args)

    if not hasattr(options, 'func'):
        parser.print_help()
        return 1

    options.func(options)
    return 0
