from xkcdpass import xkcd_password as xp
from pathlib import Path
from prettytable import PrettyTable
from collections import namedtuple

import warnings
import os
import sys
import click
import getopt

from datetime import date, datetime

from models.wrapper import Wrapper

w = Wrapper()


@click.group()
def cli():
    pass


@cli.command()
@click.argument('name', nargs=1, type=click.STRING)
@click.argument('email', nargs=1, type=click.STRING)
@click.option('--enabled/--disabled', default=True,
              help='Enables or disables an user account', is_flag=True)
@click.option('--expire', default='30',
              help='Set the amount of days until this account expires')
@click.option('--yes', is_flag=True, default=False)
def add(name, email, enabled, expire, yes):
    w.add(name, email, enabled, expire, yes)

@cli.command()
@click.option('--highlight', default=False,
              help='Highlight users states', is_flag=True)
@click.argument('filter', type=click.STRING, required=False)
def list(highlight, filter):
    '''Lists registered users.

     Filters: {enabled, disabled, active, hold, expired}

    '''

    if (filter not in ['enabled', 'disabled', 'hold', 'expired', 'active', None]):
        print("\n Unknown option %s." % filter)
    else:
        w.list(highlight, filter)

@cli.command()
@click.argument('id', nargs=1, type=click.STRING)
def show(id):
    w.retrieve_user(id)


@cli.command()
@click.argument('id', nargs=1, type=click.STRING)
@click.argument('attributes', nargs=-1)
def modify(id, attributes):

    """ This option modifies user attributes.

    ID: alice's ID, user's name or email.

    Valid attributes are: name, email, password,
    project_name, description, enabled and expiration.


    Example:

    \b
       alice modify 1 name:amanda enabled:false
       alice modify amanda email:amanda@mail.com
       alice modify amanda@mail.com expiration:'in 30d'"""

    dict = {}
    for att in attributes:
        key, value = att.split(":", 1)
        dict[key] = value

    w.update_user(id, dict)


# @cli.command()
def drop():
    w.db.drop()


@cli.command()
def migrate():
    w.migrate()


def main():
    cli()
