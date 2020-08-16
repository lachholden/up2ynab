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
    required=True,
)
@click.option(
    "--up-api-token",
    required=True,
    envvar="UP_API_TOKEN",
    help="Your personal access token for the Up API.",
)
@click.option(
    "--ynab-api-token",
    required=True,
    envvar="YNAB_API_TOKEN",
    help="Your personal access token for the YNAB API.",
)
@click.option(
    "--ynab-account-name",
    required=True,
    envvar="YNAB_ACCOUNT_NAME",
    help="The name of your Up spending account in YNAB.",
    default="Up Spending",
    show_default=True,
)
def transactions(days, up_api_token, ynab_api_token, ynab_account_name):
    """Import your Up transactions into YNAB.
    
    The environment variables UP_API_TOKEN, YNAB_API_TOKEN, and YNAB_ACCOUNT_NAME can be
    used for configuration as an alternative to their corresponding options specified
    below.
    
    Setting these variables in your ~/.bashrc or similar is the recommended way to setup
    this CLI for general use - just make sure to keep them secret!
    """

    out = pe.EchoManager()
    out.section(f"Checking the last *{days} days* of transactions")

    out.start_task("Fetching transactions from Up...")
    up_client = up_api.UpClient(up_api_token)
    tx_count = len(up_client.get_transactions())
    out.task_success(f"Fetched the *{tx_count} transactions* from Up.")

    out.start_task(f"Fetching the Up account ID in YNAB...")
    ynab_client = ynab_api.YNABClient(ynab_api_token)
    account_id = None
    try:
        account_id = ynab_client.account_id_from_name(ynab_account_name)
        out.task_success(f"Fetched ID for YNAB account *{ynab_account_name}*.")
    except ValueError:
        out.task_error(f"A YNAB account called *{ynab_account_name}* cannot be found.")
        out.fatal(f"Couldn't find the named Up account in YNAB.")
        sys.exit(2)

    out.end_section()

    # TODO
    out.success("Imported *13 new transactions* in 2.56 seconds.")
