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
    required=True,
    envvar="YNAB_ACCOUNT_NAME",
    help="The name of your Up spending account in YNAB.",
    default="Up Spending",
    show_default=True,
)
@click.pass_context
@handle_http_errors
def transactions(ctx, days, ynab_account_name):
    """Import your Up transactions (transactional account only) into YNAB.
    
    Make sure your API tokens are setup correctly! Recommended use is by setting the
    environment variables UP_API_TOKEN and YNAB_API_TOKEN. You can check they are
    configured properly by running

      $ up2ynab check
    
    For more information about setting the tokens, view

      $ up2ynab check --help
    """

    out = ctx.obj["echo_manager"]

    start_time = time.perf_counter()

    out.section(f"Checking the last *{days} days* of transactions")
    out.start_task("Fetching the Up transactional account ID...")
    up_client = up_api.UpClient(ctx.obj["up_token"])
    try:
        up_client.get_transactional_account_id()
    except ValueError:
        out.task_error("More or less than 1 transactional account found.")
        out.fatal("Couldn't determine the Up transactional account ID.")
        sys.exit(2)
    out.task_success("Fetched the Up transactional account ID.")

    out.start_task("Fetching transactions from Up...")
    transactions = up_client.get_transactions(
        datetime.datetime.now() - datetime.timedelta(days=days)
    )
    tx_count = len(transactions)
    ynab_transactions = []
    for transaction in transactions:
        date = datetime.datetime.fromisoformat(transaction["attributes"]["createdAt"])
        amount = transaction["attributes"]["amount"]["valueInBaseUnits"] * 10
        payee_name = transaction["attributes"]["description"]
        import_id = f"up0:{transaction['id'].replace('-', '')}"
        ynab_transactions.append(
            ynab_api.YNABTransaction(
                date.date().isoformat(), amount, payee_name, import_id
            )
        )
    out.task_success(f"Fetched the *{tx_count} transactions* from Up.")

    out.start_task("Fetching the Up account ID in YNAB...")
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
    ids = ynab_client.create_transactions(account_id, ynab_transactions)
    out.task_success(f"Uploaded *{tx_count-len(ids)} new transactions* to YNAB.")
    out.comment(f"*{len(ids)} transactions* were previously imported.")

    out.end_section()

    time_delta = time.perf_counter() - start_time

    out.success(
        f"Imported *{tx_count-len(ids)} new transactions* in {time_delta:.2f} seconds."
    )
