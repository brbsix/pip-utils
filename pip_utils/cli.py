# -*- coding: utf-8 -*-
"""Command-line application"""

# Python 2 forwards-compatibility
from __future__ import absolute_import

# standard imports
import argparse
import sys

# external imports
from pip._vendor.pkg_resources import DistributionNotFound, get_distribution

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
        description='%s.' % __description__,
        epilog='See `%s COMMAND --help` for help '
               'on a specific subcommand.' % launcher,
        prog=launcher)
    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s ' + __version__)

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
        help='identify packages that file belongs to')
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
        help='list outdated packages that may be updated')
    parser_outdated.add_argument(
        '-b', '--brief',
        action='store_true',
        help='show package name only')
    group = parser_outdated.add_mutually_exclusive_group()
    group.add_argument(
        '-a', '--all',
        action='store_true',
        help='list all outdated packages')
    group.add_argument(
        '-p', '--pinned',
        action='store_true',
        help='list outdated packages unable to be updated')
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

    return parser


def main(args=None):
    """Start application."""
    parser = _parser()

    # Python 2 will error 'too few arguments' if no subcommand is supplied.
    # No such error occurs in Python 3, which makes it feasible to check
    # whether a subcommand was provided (displaying a help message if not).
    # argparse internals vary significantly over the major versions, so it's
    # much easier to just override the args passed to it. In this case, print
    # the usage message if there are no args.
    if args is None and len(sys.argv) <= 1:
        sys.argv.append('--help')

    options = parser.parse_args(args)

    # pass options to subcommand
    options.func(options)

    return 0
