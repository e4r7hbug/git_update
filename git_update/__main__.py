#!/usr/bin/env python
"""Script for updating a directory of repositories."""
import logging
import os

import click

from .actions import update_repo


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
