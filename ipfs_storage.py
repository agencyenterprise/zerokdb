import ipfshttpclient
import json

class IPFSStorage:
    def __init__(self, ipfs_address='/dns/localhost/tcp/5001/http'):
        self.client = ipfshttpclient.connect(ipfs_address)
        self.cid = None

    def save(self, data):
        # Convert data to JSON and save to IPFS
        json_data = json.dumps(data)
        result = self.client.add_str(json_data)
        self.cid = result

    def load(self):
        if not self.cid:
            return {}
        # Retrieve data from IPFS using CID
        json_data = self.client.cat(self.cid)
        return json.loads(json_data)
