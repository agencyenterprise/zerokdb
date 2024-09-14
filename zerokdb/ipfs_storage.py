import json
from typing import Optional, Dict, Any, List
import hashlib
import requests


class IPFSStorage:
    def __init__(self, ipfs_address: str = "/dns/localhost/tcp/5001/http"):
        self.cid: Optional[str] = None  # This will hold the latest data chunk CID
        self.cid_sequence_cid: Optional[str] = (
            None  # This will hold the CID of the sequence list
        )

    def save(self, data: Dict[str, Any]) -> str:
        """
        Save data to IPFS using Pinata SDK and return the CID.
        """
        url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
        headers = {
            "pinata_api_key": "your_pinata_api_key",
            "pinata_secret_api_key": "your_pinata_secret_api_key",
            "Content-Type": "application/json",
        }
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()["IpfsHash"]
        else:
            response.raise_for_status()

    def read_from_ipfs(self, cid: str) -> Dict[str, Any]:
        """
        Utility function to read data from IPFS using Pinata.
        """
        headers = {
            "pinata_api_key": "your_pinata_api_key",
            "pinata_secret_api_key": "your_pinata_secret_api_key",
        }
        response = requests.get(
            f"https://gateway.pinata.cloud/ipfs/{cid}", headers=headers
        )
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def load(self, cid: Optional[str] = None) -> Dict[str, Any]:
        """
        Load data from IPFS using a given CID or the stored CID.
        """
        if cid:
            self.cid = cid
        if not self.cid:
            return {}
        # Use Pinata to retrieve data from IPFS using CID
        return self.read_from_ipfs(self.cid)

    def append_linked_data(self, new_data: Dict[str, Any]) -> str:
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
        chunk_hash_data = json.dumps(new_data).encode(
            "utf-8"
        )  # Hash only the 'data' part
        chunk_hash = hashlib.sha256(chunk_hash_data).hexdigest()

        # Step 4: Save the new chunk to IPFS using Pinata and get the new CID
        new_cid = self.save(chunk)

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

    def load_sequence(self) -> Dict[str, Any]:
        """
        Load the CID sequence from IPFS. If no sequence exists, return a default structure.
        """
        if not self.cid_sequence_cid:
            # Return default structure if no sequence exists
            return {"default_sequence": [], "chunk_history": [], "latest_chunk": None}

        # Load the current CID sequence using the utility function
        sequence_data = self.read_from_ipfs(self.cid_sequence_cid)
        return sequence_data

    def download_ids_from_sequence(self, table_name: str) -> List[str]:
        """
        Read the sequence and download the IDs from the specified table.
        """
        sequence = self.load_sequence()
        ids = []
        for chunk_entry in sequence.get("default_sequence", []):
            chunk = self.load(chunk_entry["chunk_id"])
            table = chunk.get(table_name, {})
            rows = table.get("rows", [])
            ids.extend(row[0] for row in rows)  # Assuming the first column is "id"
        return ids

    def get_cid_sequence(self) -> Dict[str, Any]:
        """
        Return the stored sequence of CIDs from IPFS.
        """
        return self.load_sequence()

    def merge_chunks(self, table_name: str) -> Dict[str, Any]:
        """
        Merge all chunks into a single JSON where the rows are the union of all rows.
        """
        sequence = self.load_sequence()
        merged_data = None

        for chunk_entry in sequence.get("default_sequence", []):
            chunk = self.load(chunk_entry["chunk_id"])
            table = chunk.get(table_name, {})

            if merged_data is None:
                # Initialize merged_data with the first chunk's structure
                merged_data = {key: value for key, value in table.items() if key != "rows"}
                merged_data["rows"] = []

            # Extend the rows with the current chunk's rows
            merged_data["rows"].extend(table.get("rows", []))

        return merged_data


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
