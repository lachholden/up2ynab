import sys

import click
import requests.exceptions

import up2ynab.clients.up as up_api
import up2ynab.clients.ynab as ynab_api
import up2ynab.pretty_echo as pe


@click.command()
@click.option(
    "-d",
    "--days",
    default=14,
    help="Number of days before today (inclusive) to find transactions.",
    show_default=True,
)
@click.option(
    "--up-api-token",
    required=True,
    envvar="UP_API_TOKEN",
    help="Your personal access token for the Up API.",
)
def transactions(days, up_api_token):
    """Import your Up transactions into YNAB."""

    out = pe.EchoManager()
    out.section(f"Checking the last *{days} days* of transactions")

    out.start_task("Fetching transactions from Up...")
    try:
        up_client = up_api.UpClient(up_api_token)
        tx_count = len(up_client.get_transactions())
    except requests.exceptions.ConnectionError:
        out.fatal("Unable to connect to the Up API.")
        sys.exit(2)
    out.task_success(f"Fetched the *{tx_count} transactions* from Up.")

    out.end_section()

    # TODO
    out.success("Imported *13 new transactions* in 2.56 seconds.")
