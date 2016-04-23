# -*- coding: utf-8 -*-
"""List outdated user packages that may be updated"""

# Python 2 forwards-compatibility
from __future__ import absolute_import, print_function

# standard imports
import operator
import os
import re

# external imports
from distutils.version import LooseVersion
import pip
from pip.download import PipSession
from pip.index import PackageFinder
from pip.utils import (
    dist_is_editable, get_installed_distributions, normalize_path
)


class ListCommand(object):
    """
    Modified version of pip's list command.

    Sourced from: pip.commands.list.ListCommand
    """
    installed_distributions = None

    options = {
        'help': None,
        'local': False,
        'no_index': False,
        'allow_all_insecure': False,
        'process_dependency_links': False,
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
        'user': True,
        'verbose': 0
    }

    def _build_package_finder(self, options, index_urls, session):
        """
        Create a package finder appropriate to this list command.
        """
        return PackageFinder(
            find_links=options.get('find_links'),
            index_urls=index_urls,
            allow_all_prereleases=options.get('pre'),
            trusted_hosts=options.get('trusted_hosts'),
            process_dependency_links=options.get('process_dependency_links'),
            session=session,
        )

    def _build_session(self, options, retries=None, timeout=None):
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

    def can_be_updated(self, dist, latest_version):
        """Determine whether package can be updated or not."""

        name = dist.project_name
        dependants = self.get_dependants(name)
        for dependant in dependants:
            requires = dependant.requires()
            for requirement in self.get_requirement(name, requires):
                current = VersionPredicate(requirement)
                if not current.satisfied_by(str(latest_version)):
                    return False

        return True

    def filtered(self, dist, latest_version):
        """Filter unwanted updates."""
        if dist.project_name == 'decorator' and dist.version == '4.0.7' \
                and str(latest_version) == '4.0.8':
            return True
        return False

    def find_packages_latest_versions(self, options):
        index_urls = [options.get('index_url')] + \
                     options.get('extra_index_urls')
        if options.get('no_index'):
            index_urls = []

        dependency_links = []
        for dist in get_installed_distributions(
                local_only=options.get('local'),
                user_only=options.get('user'),
                editables_only=options.get('editable')):
            if dist.has_metadata('dependency_links.txt'):
                dependency_links.extend(
                    dist.get_metadata_lines('dependency_links.txt'),
                )

        with self._build_session(options) as session:
            finder = self._build_package_finder(options, index_urls, session)
            finder.add_dependency_links(dependency_links)

            installed_packages = get_installed_distributions(
                local_only=options.get('local'),
                user_only=options.get('user'),
                editables_only=options.get('editable'),
            )
            for dist in installed_packages:
                typ = 'unknown'
                all_candidates = finder.find_all_candidates(dist.key)
                if not options.get('pre'):
                    # Remove prereleases
                    all_candidates = [candidate for candidate in all_candidates
                                      if not candidate.version.is_prerelease]

                if not all_candidates:
                    continue
                best_candidate = max(all_candidates,
                                     key=finder._candidate_sort_key)
                remote_version = best_candidate.version
                if best_candidate.location.is_wheel:
                    typ = 'wheel'
                else:
                    typ = 'sdist'
                yield dist, remote_version, typ

    def get_dependants(self, dist):
        """Yield dependant user packages for a given package name."""

        # cache installed user distributions for re-runs
        if self.installed_distributions is None:
            self.installed_distributions = pip.get_installed_distributions(
                user_only=True)

        for package in self.installed_distributions:
            for requirement_package in package.requires():
                requirement_name = requirement_package.project_name
                # perform case-insensitive matching
                if requirement_name.lower() == dist.lower():
                    yield package

    def get_requirement(self, name, requires):
        """
        Yield matching requirement strings.

        The strings are presented in the format demanded by
        distutils.versionpredicate.VersionPredicate. Hopefully
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

    def output_package(self, dist):
        if dist_is_editable(dist):
            return '%s (%s, %s)' % (
                dist.project_name,
                dist.version,
                dist.location,
            )
        else:
            return '%s (%s)' % (dist.project_name, dist.version)

    def run_outdated(self, options):
        latest_versions = sorted(
            self.find_packages_latest_versions(self.options),
            key=lambda p: p[0].project_name.lower())

        # # configure logging
        # logging.basicConfig(format='%(message)s',
        #                     level=logging.INFO)

        for dist, latest_version, typ in latest_versions:
            if latest_version > dist.parsed_version:
                if options.all:
                    pass
                elif options.pinned:
                    if self.can_be_updated(dist, latest_version):
                        continue
                elif not options.pinned:
                    if not self.can_be_updated(dist, latest_version):
                        continue

                if not self.filtered(dist, latest_version):
                    print(dist.project_name if options.brief else
                          '%s - Latest: %s [%s]' %
                          (self.output_package(dist), latest_version, typ))


class VersionPredicate(object):
    """
    Parse and test package version predicates. Unlike the original,
    this uses LooseVersion instead of StrictVersion.

    Sourced from: distutils.versionpredicate.VersionPredicate
    """

    def __init__(self, versionPredicateStr):
        """Parse a version predicate string."""
        try:
            flags = re.ASCII  # Python 3 support
        except AttributeError:
            flags = 0

        re_paren = re.compile(r'^\s*\((.*)\)\s*$')
        re_validPackage = re.compile(
            r'(?i)^\s*([a-z_]\w*(?:\.[a-z_]\w*)*)(.*)', flags)

        versionPredicateStr = versionPredicateStr.strip()
        if not versionPredicateStr:
            raise ValueError('empty package restriction')
        match = re_validPackage.match(versionPredicateStr)
        if not match:
            raise ValueError('bad package name in %r' % versionPredicateStr)
        self.name, paren = match.groups()
        paren = paren.strip()
        if paren:
            match = re_paren.match(paren)
            if not match:
                raise ValueError('expected parenthesized list: %r' % paren)
            str = match.groups()[0]
            self.pred = [self._splitUp(aPred) for aPred in str.split(',')]
            if not self.pred:
                raise ValueError('empty parenthesized list in %r'
                                 % versionPredicateStr)
        else:
            self.pred = []

    def __str__(self):
        if self.pred:
            seq = [cond + ' ' + str(ver) for cond, ver in self.pred]
            return self.name + ' (' + ', '.join(seq) + ')'
        else:
            return self.name

    def _splitUp(self, pred):
        """Parse a single version comparison.

        Return (comparison string, LooseVersion)
        """
        re_splitComparison = re.compile(
            r'^\s*(<=|>=|<|>|!=|==)\s*([^\s,]+)\s*$')
        res = re_splitComparison.match(pred)
        if not res:
            raise ValueError('bad package restriction syntax: %r' % pred)
        comp, verStr = res.groups()
        return (comp, LooseVersion(verStr))

    def satisfied_by(self, version):
        """
        True if version is compatible with all the predicates in self.
        The parameter version must be acceptable to the LooseVersion
        constructor.  It may be either a string or LooseVersion.
        """
        compmap = {'<': operator.lt, '<=': operator.le, '==': operator.eq,
                   '>': operator.gt, '>=': operator.ge, '!=': operator.ne}

        for cond, ver in self.pred:
            if not compmap[cond](version, ver):
                return False
        return True


def command_outdated(options):
    """Command launched by CLI."""
    listcommand = ListCommand()
    listcommand.run_outdated(options)
