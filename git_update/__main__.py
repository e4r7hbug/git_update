#!/usr/bin/env python
"""Script for updating a directory of repositories."""
import logging
import os

import click
from git import InvalidGitRepositoryError, Repo
from git.exc import GitCommandError


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
                log.info('%s has updates, %s..%s', fetch_info.name,
                         current[fetch_info.ref], fetch_info.commit)
        except KeyError:
            log.info('New reference %s', fetch_info.name)

    for branch in branch_list:
        log.debug('Checking for change in %s', branch.name)

        if current[branch] != branch.commit:
            log.info('%s updated, %s..%s', branch.name, current[branch],
                     branch.commit)

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
        log.info('Updating %s', repo.git_dir)
    except InvalidGitRepositoryError:
        log.warning('%s is not a valid repository.', directory)
        return False

    try:
        remote = repo.remote()
    except ValueError:
        log.warning('Check remotes for %s: %s', directory, repo.remotes)
        return False

    try:
        fetch_info_list = remote.pull()
    except GitCommandError as error:
        log.fatal('Pull failed. %s', error)
        return False

    check_changes(current, fetch_info_list, repo.branches)

    return True


@click.command()
@click.option('-d', '--debug', help='Set DEBUG level logging.', is_flag=True)
@click.argument('dir', default='.')
def main(**kwargs):
    """Update repositories in a directory.

    By default, the current working directory list is used for finding valid
    repositories.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)s] %(name)s:%(funcName)s - %(message)s')

    log = logging.getLogger(__name__)

    if kwargs['debug']:
        logging.root.setLevel(logging.DEBUG)

    main_dir = kwargs['dir']
    log.info('Finding directories in %s', main_dir)

    dir_list = os.listdir(main_dir)
    log.debug('List of directories: %s', dir_list)

    # Git directory was passed in, not a directory of Git directories
    if '.git' in dir_list:
        dir_list = kwargs['dir']

    for directory in dir_list:
        update_repo(os.path.join(main_dir, directory))


if __name__ == '__main__':
    main()
