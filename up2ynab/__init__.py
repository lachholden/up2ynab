import click

from up2ynab.commands import *


@click.group()
def cli():
    pass


cli.add_command(check)
cli.add_command(transactions)
cli()
