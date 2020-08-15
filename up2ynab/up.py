import requests

class UpClient:
    def __init__(self, api_token):
        self.api_token = api_token
        self.headers = {'Authorization': f'Bearer {self.api_token}'}
    
    @staticmethod
    def up_url(endpoint):
        """Return the full URL corresponding to the specified Up API endpoint."""
        return 'https://api.up.com.au/api/v1' + endpoint

    def up_get(self, endpoint, **kwargs):
        """Use requests.get to get data from the specified Up API endpoint."""
        return requests.get(UpClient.up_url(endpoint), headers=self.headers, **kwargs)
    
    def get_transactions(self):
        # TODO: calculate the real date
        r = self.up_get('/transactions', params={'filter[since]': '2020-08-01T01:02:03+10:00'})
        r.raise_for_status()

        json_response = r.json()
        transactions_json = json_response['data']

        # keep following the 'next' links and retrieving the data until all the transactions are
        # retrieved
        while json_response['links']['next'] is not None:
            r = requests.get(json_response['links']['next'], headers=self.headers)
            r.raise_for_status()
            json_response = r.json()
            transactions_json.extend(json_response['data'])

        return transactions_json