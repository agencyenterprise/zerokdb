import requests
from zerokdbapi.config import settings


class EnhancedFileStorage:
    def __init__(self, filename):
        self.filename = filename

    def save(self, data, entity_id):
        """
        Save data by appending it to the REST API at zerokdbapi.
        """
        self.append_data_to_api(entity_id, data)
        """
        Call the POST /entity endpoint to create a new table.
        """
        url = "http://localhost:8000/entity"
        response = requests.post(url, json={"entity_name": entity_name})
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def load(self, cid):
        """
        Load data by querying the Pinata API using a CID.
        """
        return self.query_pinata(cid)

    def query_pinata(self, cid):
        """
        Query the Pinata API to get data based on CID.
        """
        url = f"https://gateway.pinata.cloud/ipfs/{cid}"
        headers = {
            "pinata_api_key": settings.pinata_api_key,
            "pinata_secret_api_key": settings.pinata_secret_api_key,
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def append_data_to_api(self, entity_id, data):
        """
        Call the REST API at zerokdbapi to append data.
        """
        url = f"http://localhost:8000/append-data/{entity_id}"
        response = requests.post(url, json={"data": data})
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
