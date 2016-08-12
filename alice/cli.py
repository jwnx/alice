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
def list():
    w.list()

@cli.command()
@click.argument('email', nargs=1, type=click.STRING)
def show(email):
    w.retrieve_user(email)


@cli.command()
@click.argument('email', nargs=1, type=click.STRING)
@click.argument('attributes', nargs=-1)
def modify(email, attributes):
    print attributes

@cli.command()
def drop():
    w.db.drop()

def main():
    cli()
