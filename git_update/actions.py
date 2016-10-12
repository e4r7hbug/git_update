"""Git repo actions."""
import logging
import os
import pathlib

import click
from git import InvalidGitRepositoryError, Repo
from git.exc import GitCommandError

LOG = logging.getLogger(__name__)


def crawl(path):
    """Crawl the path for possible Git directories."""
    main_dir = pathlib.Path(path)
    if not main_dir.is_dir():
        main_dir = main_dir.parent
    main_dir = main_dir.resolve()
    LOG.info('Finding directories in %s', main_dir)

    dir_list = [directory for directory in main_dir.iterdir() if directory.is_dir() and directory.parts[-1] != '.git']
    LOG.debug('List of directories: %s', dir_list)

    for directory in dir_list:
        update_repo(os.path.join(main_dir, directory))


def check_changes(current, fetch_info_list, branch_list):
    """Check for changes in local branches and remote.

    Args:
        current: Dict(reference: commit) from before `git pull` operation.
        fetch_info_list: List of remote references from `git pull`.
        branch_list: List of branches in repository.
    """
    log = logging.getLogger(__name__)

    for fetch_info in fetch_info_list:
        log.debug('Checking for change in %s', fetch_info.name)

        try:
            if current[fetch_info.ref] != fetch_info.commit:
                log.info('%s has updates, %s..%s', fetch_info.name, current[fetch_info.ref], fetch_info.commit)
        except KeyError:
            log.info('New reference %s', fetch_info.name)

    for branch in branch_list:
        log.debug('Checking for change in %s', branch.name)

        if current[branch] != branch.commit:
            log.info('%s updated, %s..%s', branch.name, current[branch], branch.commit)

    return True


def update_repo(directory):
    """Update a repository.

    Returns:
        False if bad repository.
        True if everything worked.
    """
    log = logging.getLogger(__name__)

    try:
        repo = Repo(directory)
        current = {ref: ref.commit for ref in repo.refs}

        click.secho('Updating {0}'.format(repo.git_dir), fg='blue')

        remote = repo.remote()
        fetch_info_list = remote.pull()
    except InvalidGitRepositoryError:
        log.warning('%s is not a valid repository.', directory)
        return False
    except ValueError:
        log.warning('Check remotes for %s: %s', directory, repo.remotes)
        return False
    except GitCommandError as error:
        log.fatal('Pull failed. %s', error)
        return False

    check_changes(current, fetch_info_list, repo.branches)

    return True
