from functools import wraps
from requests.exceptions import HTTPError


def handle_http_errors(f):
    """Handles any otherwise unhandled HTTPError in f.
    
    The errors are generally raised as a result of response.raise_for_status() after any
    desired or specifically checked HTTP Error codes have been handled.
    """

    @wraps(f)
    def decorated(ctx, *args, **kwargs):
        try:
            return f(ctx, *args, **kwargs)
        except HTTPError as e:
            out = ctx.obj["echo_manager"]
            code = e.response.status_code

            if code >= 500:
                out.fatal(
                    "An internal server error occurred requesting the URL",
                    e.response.url,
                )
                ctx.exit(2)
            elif code == 401:
                out.fatal(
                    "An authentication error occurred accessing one of the APIs.",
                    "Please run `up2ynab check` to help fix this problem.",
                )
                ctx.exit(2)
            elif code == 421:
                out.fatal(
                    "The rate limit has been exceeded for one of the APIs.",
                    "Please wait before trying again.",
                )
                ctx.exit(2)
            else:
                out.fatal(
                    f"Accessing one of the APIs resulted in an unexpected HTTP {code} error."
                )
                ctx.exit(2)

    return decorated
