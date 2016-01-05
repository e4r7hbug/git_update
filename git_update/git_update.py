#!/usr/bin/env python
"""Script for updating a directory of repositories."""
import logging
import os
from inspect import getmembers
from pprint import pformat

import click
from git import InvalidGitRepositoryError, Repo
from git.exc import GitCommandError


def update_repo(directory):
    """Update a repository.

    Returns:
        False if bad repository.
        True if everything worked.
    """
    log = logging.getLogger(__name__)

    try:
        repo = Repo(directory)
        log.info('Updating %s', repo)
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

    for count, fetch_info in enumerate(fetch_info_list):
        log.debug('Fetch info %d:\n%s', count, pformat(getmembers(fetch_info)))

    return True


@click.command()
@click.option('-d', '--debug', help='Set DEBUG level logging.', is_flag=True)
@click.argument('dir', default='.')
def main(**kwargs):
    """Update repositories in a directory.

    By default, the current working directory list is used for finding valid
    repositories.
    """
    logging.basicConfig(level=logging.INFO)

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
