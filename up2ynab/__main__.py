import click

import up2ynab.up as up_api
import up2ynab.pretty_echo as pe

@click.group()
def cli():
    pass

@click.command()
@click.option('-d', '--days', default=14, help='Number of days before today (inclusive) to find transactions.')
@click.option('--up-api-token', required=True, envvar='UP_API_TOKEN', help='Your personal access token for the Up API.')
def transactions(days, up_api_token):
    """Import your Up transactions into YNAB."""

    out = pe.EchoManager()
    out.section(f'Checking transactions from the last {days} days')

    out.start_task('Fetching transactions from Up...')
    up_client = up_api.UpClient(up_api_token)
    tx_count = len(up_client.get_transactions())
    out.task_success(f'Fetched the {tx_count} Up transactions')

    out.end_section()

    # TODO
    out.success('Imported 13 new transactions in 2.56 seconds.')


cli.add_command(transactions)
cli()