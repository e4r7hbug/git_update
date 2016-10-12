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


def check_changes(current, remote, fetch_info_list, branch_list):
    """Check for changes in local branches and remote.

    Args:
        current: Dict(reference: commit) from before `git pull` operation.
        fetch_info_list: List of remote references from `git pull`.
        branch_list: List of branches in repository.
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
    except ValueError:
        LOG.warning('Check remotes for %s: %s', directory, repo.remotes)

    if repo:
        current = {ref: ref.commit for ref in repo.refs}

        click.secho('Updating {0}'.format(repo.git_dir), fg='blue')

        remote = repo.remote()

        try:
            fetch_info_list = remote.pull()
            check_changes(current, remote, fetch_info_list, repo.branches)
        except GitCommandError as error:
            remote_url = repo.git.remote('get-url', remote.name)
            LOG.fatal(
                click.style(
                    '%s pull failed, check remote: %s = %s', fg='white', bg='red'),
                directory,
                remote,
                remote_url)
            LOG.debug('Pull output: %s', error)

    return repo
