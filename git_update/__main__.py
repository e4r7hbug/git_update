#!/usr/bin/env python
"""Script for updating a directory of repositories."""
import logging
import os
from pathlib import Path

import click

from .actions import update_repo


def set_logging(ctx, param, value):
    """Set logging level based on how many verbose flags."""
    logging_level = (logging.root.getEffectiveLevel() - value * 10) or 1
    logging.basicConfig(level=logging_level, format='[%(levelname)s] %(name)s:%(funcName)s - %(message)s')

    logging.addLevelName(47, 'NOTICE')


@click.command()
@click.option('-v', '--verbose', count=True, callback=set_logging, help='More verbose logging, use multiple times.')
@click.argument('dir', default='.')
def main(**kwargs):
    """Update repositories in a directory.

    By default, the current working directory list is used for finding valid
    repositories.
    """
    log = logging.getLogger(__name__)

    main_dir = Path(kwargs['dir'])
    if not main_dir.is_dir():
        main_dir = main_dir.parent
    main_dir = main_dir.resolve()
    log.info('Finding directories in %s', main_dir)

    dir_list = [directory for directory in main_dir.iterdir() if directory.is_dir() and directory.parts[-1] != '.git']
    log.debug('List of directories: %s', dir_list)

    for directory in dir_list:
        update_repo(os.path.join(main_dir, directory))


if __name__ == '__main__':
    main()
