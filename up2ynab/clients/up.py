import requests


class UpClient:
    def __init__(self, api_token):
        self.api_token = api_token
        self.headers = {"Authorization": f"Bearer {self.api_token}"}

    @staticmethod
    def up_url(endpoint):
        """Return the full URL corresponding to the specified Up API endpoint."""
        return "https://api.up.com.au/api/v1" + endpoint

    def up_get(self, endpoint, **kwargs):
        """Use requests.get to get data from the specified Up API endpoint."""
        return requests.get(UpClient.up_url(endpoint), headers=self.headers, **kwargs)

    def is_authenticated(self):
        r = self.up_get("/util/ping")

        # 401 means not authenticated properly, 200 means good to go
        if r.status_code == 401:
            return False
        elif r.status_code == 200:
            return True

        # If it's neither 200 nor 401, raise it as an error
        r.raise_for_status()

    def get_transactional_account_id(self):
        r = self.up_get("/accounts")
        r.raise_for_status()
        json_data = r.json()
        ids = [
            acc["id"]
            for acc in json_data["data"]
            if acc["attributes"]["accountType"] == "TRANSACTIONAL"
        ]

        if len(ids) != 1:
            raise ValueError(f"found {len(ids)} transactional accounts, should be 1")

        self.tx_acct_id = ids[0]

    def get_transactions(self, since):
        assert self.tx_acct_id is not None
        r = self.up_get(
            f"/accounts/{self.tx_acct_id}/transactions",
            params={"filter[since]": since.strftime("%Y-%m-%dT%H:%M:%S+00:00")},
        )
        r.raise_for_status()

        json_response = r.json()
        transactions_json = json_response["data"]

        # Keep following the 'next' links and retrieving the data until all the
        # transactions are retrieved
        while json_response["links"]["next"] is not None:
            r = requests.get(json_response["links"]["next"], headers=self.headers)
            r.raise_for_status()
            json_response = r.json()
            transactions_json.extend(json_response["data"])

        return transactions_json
