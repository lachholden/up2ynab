import click

from up2ynab.commands import *
from up2ynab.util.pretty_echo import EchoManager

# The required=False flags for the two API tokens are set that way to bypass click's
# default handling if they are not provided. Running `up2ynab check` will display
# specific error/help information if they are unset, and other commands will fail with
# an authentication error, which also directs users to `up2ynab check` (if
# up2ynab.util.http_error_handler is used).
@click.group()
@click.option(
    "--up-api-token",
    required=False,
    envvar="UP_API_TOKEN",
    help="Your personal access token for the Up API.",
)
@click.option(
    "--ynab-api-token",
    required=False,
    envvar="YNAB_API_TOKEN",
    help="Your personal access token for the YNAB API.",
)
@click.pass_context
def cli(ctx, up_api_token, ynab_api_token):
    """A command-line interface for synchronising the Up neobank with the budgeting
    app You Need A Budget.
    
    You can use the below options to specify the respective API keys for each command,
    but see

      $ up2ynab check --help

    for details on the recommended way of configuration using environment variables.
    """
    ctx.obj = {
        "up_token": up_api_token,
        "ynab_token": ynab_api_token,
        "echo_manager": EchoManager(),
    }


cli.add_command(check)
cli.add_command(transactions)
cli(obj={})
