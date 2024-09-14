import requests

class IPFSService:
    def __init__(self):
        self.pinata_api_key = "your_pinata_api_key"
        self.pinata_secret_api_key = "your_pinata_secret_api_key"
        self.pinata_url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"

    def save_to_ipfs(self, data):
        headers = {
            "pinata_api_key": self.pinata_api_key,
            "pinata_secret_api_key": self.pinata_secret_api_key
        }
        response = requests.post(self.pinata_url, json={"pinataContent": data}, headers=headers)
        if response.status_code == 200:
            return response.json()["IpfsHash"]
        else:
            response.raise_for_status()
