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

    up_client = up_api.UpClient(up_api_token)

    click.echo(f'Checking transactions from the last {pe.key(f"{days} days")}:')

    fetching_echo = pe.EchoInProgress('    Fetching transactions from Up...').start()
    tx_count = len(up_client.get_transactions())
    fetching_echo.finish(f'    Fetched the {pe.up(f"{tx_count} Up transactions")}.')

    # TODO
    click.echo(f'    Fetched the {pe.ynab(f"{tx_count} previously imported YNAB transactions")}.')
    
    # TODO
    click.echo(f'    There are {pe.key("13 new transactions")} to be imported.')

    click.echo()

    click.echo(f'Imported transactions to YNAB.')

    click.echo()

    # TODO
    click.echo(pe.success('Imported 13 new transactions in 2.56 seconds.'))


cli.add_command(transactions)
cli()