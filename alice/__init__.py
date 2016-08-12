import getopt
import sys

# from cli import Cli
import click

@click.group
def greet():
    pass

@click.command()
def list():
    print "List"

@click.command()
def add():
    print "Add"

# def main():
#     cli = Cli()

if __name__ == '__main__':
    greet()
    print("Done")
