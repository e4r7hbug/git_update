"""Git repo actions."""
import logging
import pathlib

import click
from git import InvalidGitRepositoryError, Repo
from git.exc import GitCommandError

LOG = logging.getLogger(__name__)


def crawl(path):
    """Crawl the path for possible Git directories.

    Args:
        path (str): Original path to crawl.
    """
    main_dir = pathlib.Path(path)
    if not main_dir.is_dir():
        main_dir = main_dir.parent
    main_dir = main_dir.resolve()
    LOG.info('Finding directories in %s', main_dir)

    dir_list = [directory for directory in main_dir.iterdir() if directory.is_dir() and directory.parts[-1] != '.git']
    dir_list.append(main_dir)
    LOG.debug('List of directories: %s', dir_list)

    for directory in dir_list:
        update_repo(directory)


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
    print(type(branch_list))
    print(type(remote))
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


def pull(directory=None, repo=None, remote=None):
    """Perform 'git pull'.

    Args:
        directory (pathlib.Path): Git path to update.
        repo (git.repo.base.Repo): Git repository object.
        remote (git.remote.Remote): First Git Remote found, usually 'origin'.
    """
    click.secho('Updating {0}'.format(repo.git_dir), fg='blue')

    current = {ref: ref.commit for ref in repo.refs}

    try:
        fetch_info_list = remote.pull()
        check_references(current=current, fetch_info_list=fetch_info_list)
        check_branches(branch_list=repo.branches, current=current, remote=remote)
    except GitCommandError as error:
        remote_url = repo.git.remote('get-url', remote.name)
        LOG.fatal(
            click.style(
                '%s pull failed, check remote: %s = %s', fg='white', bg='red'), directory, remote, remote_url)
        LOG.debug('Pull output: %s', error)


def update_repo(directory):
    """Update a repository.

    Returns:
        git.repo.base.Repo: Valid Git repository or None.
    """
    repo = None

    try:
        repo = Repo(directory)
    except InvalidGitRepositoryError:
        LOG.debug('%s is not a valid repository.', directory)

    if repo:
        remote = None

        try:
            remote = repo.remote()
        except ValueError:
            LOG.warning(click.style('Missing remotes: %s', fg='red'), directory)

        if remote:
            pull(directory=directory, repo=repo, remote=remote)

    return repo
