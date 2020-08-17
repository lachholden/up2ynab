import sys
import datetime
import time

import click
import requests.exceptions

import up2ynab.clients.up as up_api
import up2ynab.clients.ynab as ynab_api
from up2ynab.util.http_error_handler import handle_http_errors


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
    "-a",
    required=True,
    envvar="YNAB_ACCOUNT_NAME",
    help="The name of your Up spending account in YNAB."
    + " Can also be set by YNAB_ACCOUNT_NAME environment variable.",
    default="Up Spending",
    show_default=True,
)
@click.option(
    "--flag-foreign",
    "-ff",
    required=False,
    envvar="YNAB_FOREIGN_TRANSACTION_FLAG",
    help="The coloured flag in YNAB to apply to transactions in a foreign currency."
    + " Can also be set by YNAB_FOREIGN_TRANSACTION_FLAG environment variable.",
    type=click.Choice(
        ["red", "orange", "yellow", "green", "blue", "purple"], case_sensitive=False
    ),
)
@click.pass_context
@handle_http_errors
def transactions(ctx, days, ynab_account_name, flag_foreign):
    """Import your Up transactions into YNAB.

    This command only imports transactions from the transactional account in Up, not
    from any Savers.
    
    Make sure your API tokens are setup correctly! Recommended use is by setting the
    environment variables UP_API_TOKEN and YNAB_API_TOKEN. You can check they are
    configured properly by running

      $ up2ynab check
    
    For more information about setting the tokens, view

      $ up2ynab check --help
    """

    # Get the context-provided echo manager for printing output
    out = ctx.obj["echo_manager"]

    # Fetch the current time, to print the execution time at the end of the script
    start_time = time.perf_counter()

    out.section(f"Checking the last *{days} days* of transactions")

    # Display the selected foreign currency flag, if one has been selected
    if flag_foreign is not None:
        out.info(f"Any foreign currency transactions will be flagged *{flag_foreign}*.")

    out.start_task("Fetching the Up transactional account ID...")

    # Create the Up client and try to get the ID of the transactional account
    up_client = up_api.UpClient(ctx.obj["up_token"])
    try:
        up_client.get_transactional_account_id()
    except ValueError:
        out.task_error("More or less than 1 transactional account found.")
        out.fatal("Couldn't determine the Up transactional account ID.")
        sys.exit(2)
    out.task_success("Fetched the Up transactional account ID.")

    # Fetch the transactions from Up from the past proved number of days using the
    # client
    out.start_task("Fetching transactions from Up...")
    transactions = up_client.get_transactions(
        datetime.datetime.now() - datetime.timedelta(days=days)
    )

    # Convert the transaction data to the format required by the YNAB client
    ynab_transactions = [
        ynab_api.YNABTransaction.from_up_transaction_data(tx) for tx in transactions
    ]

    out.task_success(f"Fetched the *{len(transactions)} transactions* from Up.")

    out.start_task("Fetching the Up account ID in YNAB...")

    # Create the YNAB client and try to get the ID of the up account
    ynab_client = ynab_api.YNABClient(ctx.obj["ynab_token"])
    account_id = None
    try:
        account_id = ynab_client.account_id_from_name(ynab_account_name)
        out.task_success(f"Fetched ID for YNAB account *{ynab_account_name}*.")
    except ValueError:
        out.task_error(f"A YNAB account called *{ynab_account_name}* cannot be found.")
        out.fatal(f"Couldn't find the named Up account in YNAB.")
        sys.exit(2)

    out.start_task("Uploading the transactions to YNAB...")

    # Import the transactions to YNAB via the client
    ids = ynab_client.create_transactions(account_id, ynab_transactions)
    out.task_success(
        f"Uploaded *{len(transactions)-len(ids)} new transactions* to YNAB."
    )
    out.comment(f"*{len(ids)} transactions* were previously imported.")

    out.end_section()

    # Calculate the execution time
    time_delta = time.perf_counter() - start_time

    # Display the final script result
    out.success(
        f"Imported *{len(transactions)-len(ids)} new transactions* in {time_delta:.2f} seconds."
    )
