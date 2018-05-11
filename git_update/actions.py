"""Git repo actions."""
import logging
import pathlib

import click
from git import InvalidGitRepositoryError, Repo
from git.exc import GitCommandError

from .checks import check_branches, check_references

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
        repo = Repo(str(directory))
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
