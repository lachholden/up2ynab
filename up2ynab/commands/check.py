import sys

import click
import requests.exceptions

import up2ynab.clients.up as up_api
import up2ynab.clients.ynab as ynab_api
import up2ynab.pretty_echo as pe


@click.command()
@click.pass_context
def check(ctx):
    """Check that your API tokens are configured correctly.

    To get your Up API token, visit the following page:

      https://api.up.com.au/getting_started

    To get your YNAB API token, visit the following page:

      https://app.youneedabudget.com/settings/developer
    
    The API tokens should be configured by setting the environment variables
    UP_API_TOKEN and YNAB_API_TOKEN. Setting these variables in your ~/.bashrc or
    similar is the recommended way to setup this CLI for general use, for example by
    including:

      # DO NOT MAKE THIS FILE PUBLICLY AVAILABLE

      export UP_API_TOKEN=up:yeah:alonghashofnumbersandletters

      export YNAB_API_TOKEN=ashorterhashofnumbersandletters

    It is CRITICAL that you do not make your API keys publicly available. If you version
    control your config files, consider exporting your tokens in a separate file (e.g.
    ~/.up2ynab) ignored by version control that you source as part of your shell
    configuration.

    Alternatively, the options --up-api-token and --ynab-api-token can be used *before*
    the subcommand to specify the tokens at runtime, e.g.:

      $ up2ynab --up-api-token xxxx --ynab-api-token xxxx check
    """

    out = pe.EchoManager()
    out.section("Checking your API tokens")

    # Check the Up API token
    up_authenticated = None
    out.start_task("Checking your Up API token...")
    if ctx.obj["up_token"] is not None:
        up_client = up_api.UpClient(ctx.obj["up_token"])
        up_authenticated = up_client.is_authenticated()
        if up_authenticated:
            out.task_success("Your Up API token is working.")
        else:
            out.task_error("Your Up API token returned an authentication error.")
    else:
        out.task_error("No Up API token was provided.")

    # Check the YNAB API token
    ynab_authenticated = None
    out.start_task("Checking your YNAB token...")
    if ctx.obj["ynab_token"] is not None:
        ynab_client = ynab_api.YNABClient(ctx.obj["ynab_token"])
        ynab_authenticated = ynab_client.is_authenticated()
        if ynab_authenticated:
            out.task_success("Your YNAB API token is working.")
        else:
            out.task_error("Your YNAB API token returned an authentication error.")
    else:
        out.task_error("No YNAB API token was provided.")

    out.end_section()

    # Display the results
    if up_authenticated is None or ynab_authenticated is None:
        out.error(
            "One or both of your API tokens were not provided.",
            "Either use the --up-api-token/--ynab-api-token flags,",
            "or set the UP_API_TOKEN/YNAB_API_TOKEN environment variables.",
        )
        sys.exit(1)
    elif up_authenticated and ynab_authenticated:
        out.success("Both API tokens authenticated successfully - you're good to go!")
    else:
        out.warning(
            "One or both of your API tokens are misconfigured.",
            "Fix them and run `up2ynab check` again.",
        )
        sys.exit(2)
