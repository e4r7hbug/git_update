#!/usr/bin/env python
"""Script for updating a directory of repositories."""
import logging

import click

from .actions import crawl


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
    crawl(kwargs['dir'])


if __name__ == '__main__':
    main()
