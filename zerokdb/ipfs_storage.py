import json
import hashlib
import requests


class IPFSStorage:
    def __init__(self, ipfs_address="/dns/localhost/tcp/5001/http"):
        self.cid = None  # This will hold the latest data chunk CID
        self.cid_sequence_cid = None  # This will hold the CID of the sequence list

    def call_rest_api(self, endpoint, payload):
        """
        Utility function to call the FastAPI REST API.
        """
        response = requests.post(f"http://localhost:8000/{endpoint}", json=payload)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def read_from_ipfs(self, cid):
        """
        Utility function to read data from IPFS using Pinata.
        """
        headers = {
            "pinata_api_key": "your_pinata_api_key",
            "pinata_secret_api_key": "your_pinata_secret_api_key",
        }
        response = requests.get(f"https://gateway.pinata.cloud/ipfs/{cid}", headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def load(self, cid=None):
        """
        Load data from IPFS using a given CID or the stored CID.
        """
        if cid:
            self.cid = cid
        if not self.cid:
            return {}
        # Use Pinata to retrieve data from IPFS using CID
        return self.read_from_ipfs(self.cid)

    def append_linked_data(self, new_data):
        """
        Append new data to the linked list in IPFS and update the CID sequence.
        """
        # Step 1: Retrieve the current CID sequence from IPFS
        current_sequence = self.load_sequence()

        # Step 2: Create a new chunk with the new data and a reference to the previous chunk
        chunk = {
            "data": new_data,
            "next": self.cid,  # Point to the previous chunk (the last saved one)
        }

        # Step 3: Compute the hash of the chunk's data (excluding the next reference)
        chunk_hash_data = json.dumps(new_data).encode("utf-8")
            "utf-8"
        )  # Hash only the 'data' part
        chunk_hash = hashlib.sha256(chunk_hash_data).hexdigest()

        # Step 4: Use the FastAPI REST API to save the new chunk to IPFS and get the new CID
        new_cid = self.call_rest_api("save", {"data": chunk})["cid"]

        # Step 5: Update the sequence with the new chunk details
        chunk_entry = {"chunk_id": new_cid, "chunk_hash": chunk_hash}
        current_sequence["default_sequence"].append(chunk_entry)

        # Step 5: Track the chunk history (versions of this chunk)
        existing_chunk = next(
            (
                item
                for item in current_sequence["chunk_history"]
                if item["chunk_id"] == new_cid
            ),
            None,
        )

        if existing_chunk:
            # Update existing chunk history with the new version
            existing_chunk["versions"].append(new_cid)
        else:
            # Create new entry in the chunk history
            current_sequence["chunk_history"].append(
                {"chunk_id": new_cid, "versions": [new_cid]}
            )

        # Step 6: Update the latest chunk CID
        current_sequence["latest_chunk"] = new_cid

        # Step 7: Save the updated CID sequence to IPFS and store its CID
        self.cid_sequence_cid = self.save(current_sequence)

        print(f"New chunk CID: {new_cid}")
        print(f"Updated CID sequence CID: {self.cid_sequence_cid}")

        return new_cid

    def load_sequence(self):
        """
        Load the CID sequence from IPFS. If no sequence exists, return a default structure.
        """
        if not self.cid_sequence_cid:
            # Return default structure if no sequence exists
            return {"default_sequence": [], "chunk_history": [], "latest_chunk": None}

        # Load the current CID sequence
        sequence_data = self.client.cat(self.cid_sequence_cid)
        return json.loads(sequence_data)

    def traverse_linked_data(self, start_cid=None):
        """
        Traverse the linked list starting from the given CID and return all the data.
        """
        if start_cid:
            self.cid = start_cid

        current_cid = self.cid
        all_data = []

        while current_cid:
            # Load the current chunk
            chunk = self.load(current_cid)

            # Add the current chunk's data to the list
            all_data.append(chunk["data"])

            # Move to the next chunk
            current_cid = chunk.get("next")

        return all_data

    def get_cid_sequence(self):
        """
        Return the stored sequence of CIDs from IPFS.
        """
        return self.load_sequence()


# Example Usage
if __name__ == "__main__":
    storage = IPFSStorage()

    # Append new data chunks to the linked list and update the CID sequence
    cid1 = storage.append_linked_data({"id": 1, "value": "First Entry"})
    cid2 = storage.append_linked_data({"id": 2, "value": "Second Entry"})
    cid3 = storage.append_linked_data({"id": 3, "value": "Third Entry"})

    # Retrieve the full sequence of CIDs in the structured format
    cid_sequence = storage.get_cid_sequence()
    print("CID Sequence:", json.dumps(cid_sequence, indent=2))

    # Traverse the linked list starting from the latest chunk
    all_data = storage.traverse_linked_data(cid3)
    print("Retrieved linked data:", all_data)
