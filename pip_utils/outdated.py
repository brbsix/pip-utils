# -*- coding: utf-8 -*-
"""List outdated user packages that may be updated"""

# Python 2 forwards-compatibility
from __future__ import absolute_import, print_function

# standard imports
import os
from site import ENABLE_USER_SITE

# external imports
try:
    from pip._internal.download import PipSession
    from pip._internal.index import PackageFinder
    from pip._internal.utils.misc import (
        dist_is_editable, get_installed_distributions, normalize_path
    )
    from pip._internal import main
except ImportError:
    # legacy support for pip 8 & 9
    from pip.download import PipSession
    from pip.index import PackageFinder
    from pip.utils import (
        dist_is_editable, get_installed_distributions, normalize_path
    )
    from pip import main
from pip._vendor.distlib.util import parse_requirement
from pip._vendor.distlib.version import UnsupportedVersionError, get_scheme


class ListCommand(object):
    """
    Modified version of pip's list command.

    Sourced from: pip.commands.list.ListCommand
    """
    installed_distributions = []

    options = {
        'help': None,
        'local': True,
        'no_index': False,
        'allow_all_insecure': False,
        'proxy': '',
        'require_venv': False,
        'timeout': 15,
        'exists_action': [],
        'no_input': False,
        'isolated_mode': False,
        'allow_external': [],
        'quiet': 1,
        'editable': False,
        'client_cert': None,
        'allow_unverified': [],
        'disable_pip_version_check': False,
        'default_vcs': '',
        'skip_requirements_regex': '',
        'trusted_hosts': [],
        'version': None,
        'log': None,
        'index_url': 'https://pypi.python.org/simple',
        'cache_dir': os.path.join(os.environ['HOME'], '.cache/pip'),
        'outdated': True,
        'retries': 5,
        'allow_all_external': False,
        'pre': False,
        'find_links': [],
        'cert': None,
        'uptodate': False,
        'extra_index_urls': [],
        'user': ENABLE_USER_SITE,
        'verbose': 0
    }

    @staticmethod
    def _build_package_finder(options, index_urls, session):
        """
        Create a package finder appropriate to this list command.
        """
        return PackageFinder(
            find_links=options.get('find_links'),
            index_urls=index_urls,
            allow_all_prereleases=options.get('pre'),
            trusted_hosts=options.get('trusted_hosts'),
            session=session,
        )

    @staticmethod
    def _build_session(options, retries=None, timeout=None):
        session = PipSession(
            cache=(
                normalize_path(os.path.join(options.get('cache_dir'), 'http'))
                if options.get('cache_dir') else None
            ),
            retries=retries if retries is not None else options.get('retries'),
            insecure_hosts=options.get('trusted_hosts'),
        )

        # Handle custom ca-bundles from the user
        if options.get('cert'):
            session.verify = options.get('cert')

        # Handle SSL client certificate
        if options.get('client_cert'):
            session.cert = options.get('client_cert')

        # Handle timeouts
        if options.get('timeout') or timeout:
            session.timeout = (
                timeout if timeout is not None else options.get('timeout')
            )

        # Handle configured proxies
        if options.get('proxy'):
            session.proxies = {
                'http': options.get('proxy'),
                'https': options.get('proxy'),
            }

        # Determine if we can prompt the user for authentication or not
        session.auth.prompting = not options.get('no_input')

        return session

    @classmethod
    def can_be_updated(cls, dist, latest_version):
        """Determine whether package can be updated or not."""
        scheme = get_scheme('default')
        name = dist.project_name
        dependants = cls.get_dependants(name)
        for dependant in dependants:
            requires = dependant.requires()
            for requirement in cls.get_requirement(name, requires):
                req = parse_requirement(requirement)
                # Ignore error if version in requirement spec can't be parsed
                try:
                    matcher = scheme.matcher(req.requirement)
                except UnsupportedVersionError:
                    continue
                if not matcher.match(str(latest_version)):
                    return False

        return True

    @classmethod
    def find_packages_latest_versions(cls, options):
        """Yield latest versions."""
        index_urls = [] if options.get('no_index') else \
            [options.get('index_url')] + options.get('extra_index_urls')

        with cls._build_session(options) as session:
            finder = cls._build_package_finder(options, index_urls, session)

            cls.installed_distributions = get_installed_distributions(
                local_only=options.get('local'),
                user_only=options.get('user'),
                editables_only=options.get('editable'),
            )
            for dist in cls.installed_distributions:
                all_candidates = finder.find_all_candidates(dist.key)
                if not options.get('pre'):
                    # Remove prereleases
                    all_candidates = [c for c in all_candidates if not
                                      c.version.is_prerelease]

                if not all_candidates:
                    continue
                # pylint: disable=protected-access
                best_candidate = max(all_candidates,
                                     key=finder._candidate_sort_key)
                remote_version = best_candidate.version
                typ = 'wheel' if best_candidate.location.is_wheel else 'sdist'
                yield dist, remote_version, typ

    @classmethod
    def get_dependants(cls, dist):
        """Yield dependant user packages for a given package name."""
        for package in cls.installed_distributions:
            for requirement_package in package.requires():
                requirement_name = requirement_package.project_name
                # perform case-insensitive matching
                if requirement_name.lower() == dist.lower():
                    yield package

    @staticmethod
    def get_requirement(name, requires):
        """
        Yield matching requirement strings.

        The strings are presented in the format demanded by
        pip._vendor.distlib.util.parse_requirement. Hopefully
        I'll be able to figure out a better way to handle this
        in the future. Perhaps figure out how pip does it's
        version satisfaction tests and see if it is offloadable?

        FYI there should only really be ONE matching requirement
        string, but I want to be able to process additional ones
        in case a certain package does something funky and splits
        up the requirements over multiple entries.
        """
        for require in requires:
            if name.lower() == require.project_name.lower() and require.specs:
                safe_name = require.project_name.replace('-', '_')
                yield '%s (%s)' % (safe_name, require.specifier)

    @staticmethod
    def output_package(dist):
        """Return string displaying package information."""
        if dist_is_editable(dist):
            return '%s (%s, %s)' % (
                dist.project_name,
                dist.version,
                dist.location,
            )
        return '%s (%s)' % (dist.project_name, dist.version)

    @classmethod
    def run_outdated(cls, options):
        """Print outdated user packages."""
        latest_versions = sorted(
            cls.find_packages_latest_versions(cls.options),
            key=lambda p: p[0].project_name.lower())

        for dist, latest_version, typ in latest_versions:
            if latest_version > dist.parsed_version:
                if options.all:
                    pass
                elif options.pinned:
                    if cls.can_be_updated(dist, latest_version):
                        continue
                elif not options.pinned:
                    if not cls.can_be_updated(dist, latest_version):
                        continue
                    elif options.update:
                        print(dist.project_name if options.brief else
                              'Updating %s to Latest: %s [%s]' %
                              (cls.output_package(dist), latest_version, typ))
                        main(['install', '--upgrade'] + ([
                            '--user'
                        ] if ENABLE_USER_SITE else []) + [dist.key])
                        continue

                print(dist.project_name if options.brief else
                      '%s - Latest: %s [%s]' %
                      (cls.output_package(dist), latest_version, typ))


def command_outdated(options):
    """Command launched by CLI."""
    listcommand = ListCommand()
    listcommand.run_outdated(options)
