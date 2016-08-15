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

from models import Wrapper

w = Wrapper()


@click.group()
def cli():
    pass

@cli.command()
@click.argument('name', nargs=1, type=click.STRING)
@click.argument('email', nargs=1, type=click.STRING)
@click.option('--auto', default=False,
              help='Adds user automatically', is_flag=True)
@click.option('--enabled/--disabled', default=True,
              help='Enables or disables an user account', is_flag=True)
def add(name, email, auto, enabled):
    if auto is False:
        w.verify(name, email, enabled)
    else:
        w.automatic(name, email, enabled)


@cli.command()
@click.option('--enabled', default=False,
              help='Filters active users', is_flag=True)
@click.option('--disabled', default=False,
              help='Filters disabled users', is_flag=True)
def list(enabled, disabled):
    w.list(enabled, disabled)

@cli.command()
@click.argument('id', nargs=1, type=click.STRING)
def show(id):
    w.retrieve_user(id)


@cli.command()
@click.argument('id', nargs=1, type=click.STRING)
@click.argument('attributes', nargs=-1)
def modify(id, attributes):

    dict = {}
    for att in attributes:
        key, value = att.split(":", 1)
        dict[key] = value

    w.update_user(id, dict)


@cli.command()
def drop():
    w.db.drop()

def main():
    cli()
