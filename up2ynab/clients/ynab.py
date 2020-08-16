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

    def create_transactions(self, account_id, transactions):
        """Create the YNABTransactions in the account with the specified ID.
        
        Returns a 2-tuple of (created_tx_ids, duplicate_import_ids).
        """
        transactions_data = [
            {**tx._asdict(), "account_id": account_id} for tx in transactions
        ]

        r = requests.post(
            YNABClient.ynab_url("/budgets/last-used/transactions"),
            headers=self.headers,
            json={"transactions": transactions_data},
        )
        r.raise_for_status()
        json_data = r.json()["data"]
        return (json_data["transaction_ids"], json_data["duplicate_import_ids"])
