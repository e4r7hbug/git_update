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
        LOG.debug('Checking for change in %s', fetch_info.name)

        try:
            if current[fetch_info.ref] != fetch_info.commit:
                click.secho(
                    '{ref} has updates, {current}..{commit}'.format(
                        ref=fetch_info.name, current=current[fetch_info.ref], commit=fetch_info.commit),
                    fg='green',
                    dim=True)
        except KeyError:
            click.secho('New reference {ref}'.format(ref=fetch_info.name), fg='magenta', dim=True)

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
        False if bad repository.
        True if everything worked.
    """
    try:
        repo = Repo(directory)
        current = {ref: ref.commit for ref in repo.refs}

        click.secho('Updating {0}'.format(repo.git_dir), fg='blue')

        remote = repo.remote()
        fetch_info_list = remote.pull()
    except InvalidGitRepositoryError:
        LOG.debug('%s is not a valid repository.', directory)
        return False
    except ValueError:
        LOG.warning('Check remotes for %s: %s', directory, repo.remotes)
        return False
    except GitCommandError as error:
        LOG.fatal('Pull failed. %s', error)
        return False

    check_changes(current, remote, fetch_info_list, repo.branches)

    return True
