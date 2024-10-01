import requests
from zerokdb.config import settings
from zerokdb.ipfs_storage import IPFSStorage
from typing import Dict, Any


class EnhancedFileStorage:
    def __init__(self, filename):
        self.filename = filename

    def save(self, data, table_name):
        """
        Save data by appending it to the REST API at zerokdbapi.
        """
        return self.append_data_to_api(table_name, data)

    def get_table_sequence_by_name(self, table_name):
        """
        Get the CID sequence by querying the REST API at zerokdbapi.
        """
        url = f"{settings.api_host}/sequence/name"
        response = requests.post(url, json={"entity_name": table_name})
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def create_table(self, entity_name, data) -> Dict[str, Any]:
        """
        Call the POST /entity endpoint to create a new table.
        """
        url = f"{settings.api_host}/entity"
        response = requests.post(url, json={"entity_name": entity_name, "data": data})
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def load_by_id(self, cid: str) -> Dict[str, Any]:
        """
        Load data by querying the Pinata API using a CID.
        """
        storage = IPFSStorage()
        return storage.download_db(cid)

    def load(self, table_name: str) -> Dict[str, Any]:
        """
        Load data by querying the Pinata API using the table name.
        """
        try:
            print(f"Loading data for table {table_name}")
            storage = IPFSStorage()
            sequence = self.get_table_sequence_by_name(table_name)
            cid = sequence["sequence_cid"]
            return storage.download_db(cid)
        except Exception as e:
            print(e)
            return {}

    def append_data_to_api(self, table_name, data) -> Dict[str, Any]:
        """
        Call the REST API at zerokdbapi to append data.
        """
        url = f"{settings.api_host}/append-data"
        response = requests.post(url, json={"data": data, "table_name": table_name})
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()
