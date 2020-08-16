import sys

import click
import requests.exceptions

import up2ynab.up as up_api
import up2ynab.ynab as ynab_api
import up2ynab.pretty_echo as pe


@click.group()
def cli():
    pass


@click.command()
@click.option(
    "--up-api-token",
    required=False,  # want to bypass click's default handling if not present
    envvar="UP_API_TOKEN",
    help="Your personal access token for the Up API.",
)
@click.option(
    "--ynab-api-token",
    required=False,  # want to bypass click's default handling if not present
    envvar="YNAB_API_TOKEN",
    help="Your personal access token for the YNAB API.",
)
def check(up_api_token, ynab_api_token):
    """Check your Up and YNAB API tokens are configured correctly."""

    out = pe.EchoManager()
    out.section("Checking your API tokens")

    up_authenticated = None
    out.start_task("Checking your Up API token...")
    if up_api_token is not None:
        up_client = up_api.UpClient(up_api_token)
        up_authenticated = up_client.is_authenticated()
        if up_authenticated:
            out.task_success("Your Up API token is working")
        else:
            out.task_error("Your Up API token returned an authentication error")
    else:
        out.task_error("No Up API token was provided")

    ynab_authenticated = None
    out.start_task("Checking your YNAB token...")
    if ynab_api_token is not None:
        ynab_client = ynab_api.YNABClient(ynab_api_token)
        ynab_authenticated = ynab_client.is_authenticated()
        if ynab_authenticated:
            out.task_success("Your YNAB API token is working")
        else:
            out.task_error("Your YNAB API token returned an authentication error")
    else:
        out.task_error("No YNAB API token was provided")

    out.end_section()

    if up_authenticated is None or ynab_authenticated is None:
        # TODO: better multiline/wrapping handling
        out.error("One or both of your API tokens were not provided.")
        out.error(
            "Either use the --up-api-token/--ynab-api-token flags, or\n"
            + "  set the UP_API_TOKEN/YNAB_API_TOKEN environment variables."
        )
        sys.exit(1)
    elif up_authenticated and ynab_authenticated:
        out.success("Both API tokens authenticated successfully - you're good to go!")
    else:
        out.warning(
            "One or both of your API tokens are misconfigured - fix them and run `up2ynab check` again"
        )
        sys.exit(1)


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
    out.section(f"Checking transactions from the last *{days} days*")

    out.start_task("Fetching transactions from Up...")
    try:
        up_client = up_api.UpClient(up_api_token)
        tx_count = len(up_client.get_transactions())
    except requests.exceptions.ConnectionError:
        out.fatal("Unable to connect to the Up API")
        sys.exit(2)
    out.task_success(f"Fetched the *{tx_count} transactions* from Up")

    out.end_section()

    # TODO
    out.success("Imported *13 new transactions* in 2.56 seconds")


cli.add_command(check)
cli.add_command(transactions)
cli()
