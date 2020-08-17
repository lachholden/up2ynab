import requests
from collections import namedtuple
import datetime

_YNABTransactionBase = namedtuple(
    "YNABTransactionBase",
    ("date", "amount", "payee_name", "import_id", "is_foreign", "is_cleared"),
)


class YNABTransaction(_YNABTransactionBase):
    @classmethod
    def from_up_transaction_data(cls, transaction):
        """Create a YNABTransaction from Up API transaction data.
    
        transaction should be the dict representation of the JSON data representing a 
        single transaction from the Up API.
        """

        date = datetime.datetime.fromisoformat(transaction["attributes"]["createdAt"])

        # Convert from cents to millidollars
        amount = transaction["attributes"]["amount"]["valueInBaseUnits"] * 10

        payee_name = transaction["attributes"]["description"]

        import_id = f"up0:{transaction['id'].replace('-', '')}"

        is_foreign = transaction["attributes"]["foreignAmount"] is not None

        # Even if it's pending, Up counts it as part of the available value
        is_cleared = True

        return cls(
            date.date().isoformat(),
            amount,
            payee_name,
            import_id,
            is_foreign,
            is_cleared,
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

        # If it's neither 200 nor 401, raise it as an error
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

    def create_transactions(self, account_id, transactions, foreign_flag=None):
        """Create the provided YNABTransactions in the account with the specified ID.

        foreign_flag is the colour of the flag that should be set for transactions in a
        foreign currency.
        
        Returns a list of IDs that had already been imported.
        """
        transactions_data = [
            {
                "date": tx.date,
                "amount": tx.amount,
                "payee_name": tx.payee_name,
                "import_id": tx.import_id,
                "flag": (foreign_flag if tx.is_foreign else None),
                "account_id": account_id,
                "cleared": ("cleared" if tx.is_cleared else "uncleared"),
            }
            for tx in transactions
        ]

        r = requests.post(
            YNABClient.ynab_url("/budgets/last-used/transactions"),
            headers=self.headers,
            json={"transactions": transactions_data},
        )
        r.raise_for_status()
        json_data = r.json()["data"]
        return json_data["duplicate_import_ids"]
