"""Check functions for Git items."""
import logging

import click

LOG = logging.getLogger(__name__)


def check_references(current={}, fetch_info_list=[]):
    """Check references for updates.

    Args:
        current (dict): Local references before `git pull`.
        fetch_info_list (git.util.IterableList): Remote references from `git
            pull`.
    """
    for fetch_info in fetch_info_list:
        ref_name = fetch_info.name

        LOG.debug('Checking for change in %s', ref_name)

        try:
            local_commit = current[fetch_info.ref]
        except KeyError:
            click.secho('New reference {ref}'.format(ref=ref_name), fg='magenta', dim=True)
            continue

        remote_commit = fetch_info.commit

        if local_commit != remote_commit:
            click.secho(
                '{ref} updated, {local}..{remote}'.format(
                    ref=ref_name, local=local_commit, remote=remote_commit),
                fg='green',
                dim=True)


def check_branches(branch_list=None, current={}, remote=None):
    """Check local Branches for changes.

    Args:
        branch_list (git.util.IterableList): List of branches in repository.
        current (dict): Local references before `git pull`.
        remote (git.remote.Remote): First Git Remote found, usually 'origin'.
    """
    remote_refs = {ref.remote_head: ref for ref in remote.refs}
    for branch in branch_list:
        LOG.debug('Checking for change in %s', branch.name)

        local_commit = current[branch]

        try:
            remote_commit = remote_refs[branch.name].commit
        except KeyError:
            LOG.debug('Skipping local ref: %s', branch)
            continue

        if local_commit != remote_commit:
            click.secho(
                '{branch} updated, {local}..{remote}'.format(
                    branch=branch.name, local=local_commit, remote=remote_commit),
                fg='green')

    return True
