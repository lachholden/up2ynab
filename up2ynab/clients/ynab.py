import requests
from collections import namedtuple

YNABTransaction = namedtuple(
    "YNABTransaction", ("date", "amount", "payee_name", "import_id")
)


class YNABClient:
    def __init__(self, api_token):
        self.api_token = api_token
        self.headers = {"Authorization": f"Bearer {self.api_token}"}

    @staticmethod
    def ynab_url(endpoint):
        """Return the full URL corresponding to the specified YNAB API endpoint."""
        return "https://api.youneedabudget.com/v1" + endpoint

    def ynab_get(self, endpoint, **kwargs):
        """Use requests.get to get data from the specified Up API endpoint."""
        return requests.get(
            YNABClient.ynab_url(endpoint), headers=self.headers, **kwargs
        )

    def is_authenticated(self):
        r = self.ynab_get("/user")

        # 401 means not authenticated properly, 200 means good to go
        if r.status_code == 401:
            return False
        elif r.status_code == 200:
            return True

        # if it's neither 200 nor 401, raise it as an error
        r.raise_for_status()

    def account_id_from_name(self, name):
        r = self.ynab_get("/budgets/last-used/accounts")
        r.raise_for_status()

        matching_ids = [
            acc["id"] for acc in r.json()["data"]["accounts"] if acc["name"] == name
        ]

        if len(matching_ids) == 0:
            raise ValueError(f"no accounts found for name {name}")
        elif len(matching_ids) > 1:
            raise ValueError(f"more than one account found for {name}")
        else:
            return matching_ids[0]
