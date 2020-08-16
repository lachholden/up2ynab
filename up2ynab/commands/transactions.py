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
    "--ynab-account-name",
    required=True,
    envvar="YNAB_ACCOUNT_NAME",
    help="The name of your Up spending account in YNAB.",
    default="Up Spending",
    show_default=True,
)
@click.pass_context
def transactions(ctx, days, ynab_account_name):
    """Import your Up transactions into YNAB.
    
    Make sure your API tokens are setup correctly! Recommended use is by setting the
    environment variables UP_API_TOKEN and YNAB_API_TOKEN. You can check they are
    configured properly by running

      $ up2ynab check
    
    For more information about setting the tokens, view

      $ up2ynab check --help
    """

    out = pe.EchoManager()
    out.section(f"Checking the last *{days} days* of transactions")

    out.start_task("Fetching transactions from Up...")
    up_client = up_api.UpClient(ctx.obj["up_token"])
    tx_count = len(up_client.get_transactions())
    out.task_success(f"Fetched the *{tx_count} transactions* from Up.")

    out.start_task(f"Fetching the Up account ID in YNAB...")
    ynab_client = ynab_api.YNABClient(ctx.obj["ynab_token"])
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
