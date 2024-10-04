import json
from typing import Optional, Dict, Any, TypedDict, Union, List, Literal
import hashlib
import requests
from tenacity import retry, wait_exponential
import time


class TableData(TypedDict):
    columns: List[str]
    column_types: Dict[
        str, Literal["int", "float", "bool", "string", "datetime", "list[float]"]
    ]
    rows: List[List[Union[int, str]]]
    indexes: Dict[str, Any]


class CIDSequence(TypedDict):
    default_sequence: List[Dict[str, str]]
    chunk_history: List[Dict[str, List[str]]]
    latest_chunk: Optional[str]


class IPFSStorage:
    def __init__(self, pinata_api_key):
        self.pinata_api_key = pinata_api_key
        self.cid: Optional[str] = None  # This will hold the latest data chunk CID

    def save(self, data: Dict[str, TableData]) -> str:
        """
        Save data to IPFS using Pinata SDK and return the CID.
        """
        url = "https://api.pinata.cloud/pinning/pinJSONToIPFS"
        headers = {
            "Authorization": f"Bearer {self.pinata_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "pinataOptions": {"cidVersion": 1},
            "pinataMetadata": {"name": "table"},
            "pinataContent": data,
        }
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()["IpfsHash"]
        else:
            response.raise_for_status()

    def read_from_ipfs_pinata(self, cid: str) -> Dict[str, Any]:
        """
        Utility function to read data from IPFS using Pinata.
        """
        url = f"https://gateway.pinata.cloud/ipfs/{cid}"
        headers = {
            "Authorization": f"Bearer {self.pinata_api_key}",
            "Content-Type": "application/json",
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    @retry(wait=wait_exponential(min=4, max=10))
    def read_from_ipfs_raw(self, cid: str) -> bytes:
        """
        Directly read raw data from IPFS using Pinata.
        """
        # Use a public IPFS gateway
        gateway_url = f"https://ipfs.io/ipfs/{cid}"

        # Fetch the file
        response = requests.get(gateway_url)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def load(self, cid: Optional[str] = None) -> Dict[str, TableData]:
        """
        Load data from IPFS using a given CID or the stored CID.
        """
        if cid:
            self.cid = cid
        if not self.cid:
            return {}
        # Use Pinata to retrieve data from IPFS using CID
        return self.read_from_ipfs_pinata(self.cid)

    def append_data(self, new_data: Dict[str, TableData], cid_sequence: str) -> str:
        """
        Append new data to IPFS and update the CID sequence.
        """
        start = time.time()
        # Step 1: Retrieve the current CID sequence from IPFS
        current_sequence = self.load_sequence(cid_sequence)
        print(f"Loaded CID sequence in {time.time() - start} seconds")
        # Step 2: Create a new chunk with the new data and a reference to the previous chunk
        chunk = new_data

        # Step 3: Compute the hash of the chunk's data (excluding the next reference)
        chunk_hash_data = json.dumps(new_data).encode(
            "utf-8"
        )  # Hash only the 'data' part
        chunk_hash = hashlib.sha256(chunk_hash_data).hexdigest()
        print(f"Computed chunk hash in {time.time() - start} seconds")
        # Step 4: Save the new chunk to IPFS using Pinata and get the new CID
        new_cid = self.save(chunk)
        print(f"Saved new chunk in {time.time() - start} seconds")
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
        cid_sequence_cid = self.save(current_sequence)
        print(f"Saved updated CID sequence in {time.time() - start} seconds")
        print(f"New chunk CID: {new_cid}")
        print(f"Updated CID sequence CID: {cid_sequence_cid}")

        return new_cid, cid_sequence_cid

    def load_sequence(self, cid_sequence: str) -> CIDSequence:
        """
        Load the CID sequence from IPFS. If no sequence exists, return a default structure.
        """
        if cid_sequence == "0x0":
            # Return a default CID sequence structure
            return {
                "default_sequence": [],
                "chunk_history": [],
                "latest_chunk": None,
            }
        # Load the current CID sequence using the utility function
        sequence_data: CIDSequence = self.read_from_ipfs_pinata(cid_sequence)
        return sequence_data

    def get_cid_sequence(self, cid_sequence: str) -> CIDSequence:
        """
        Return the stored sequence of CIDs from IPFS.
        """
        return self.load_sequence(cid_sequence)

    def download_table(self, table_name: str) -> Dict[str, Any]:
        """
        Download all chunks into a single JSON where the rows are the union of all rows.
        """
        sequence: CIDSequence = self.load_sequence()
        merged_data = None

        for chunk_entry in sequence.get("default_sequence", []):
            chunk = self.load(chunk_entry["chunk_id"])
            table = chunk.get(table_name, {})

            if merged_data is None:
                # Initialize merged_data with the first chunk's structure
                merged_data = {
                    key: value for key, value in table.items() if key != "rows"
                }
                merged_data["rows"] = []

            # Extend the rows with the current chunk's rows
            merged_data["rows"].extend(table.get("rows", []))

        return merged_data

    def download_db(self, cid_sequence: str) -> Dict[str, TableData]:
        """
        Download all chunks into a single JSON where the rows are the union of all rows.
        """
        sequence: CIDSequence = self.load_sequence(cid_sequence)
        merged_data: Dict[str, TableData] = {}

        for chunk_entry in sequence.get("default_sequence", []):
            chunk = self.load(chunk_entry["chunk_id"])
            for table_key in chunk.keys():
                table = chunk.get(table_key, {})
                if merged_data.get(table_key, None) is None:
                    # Initialize merged_data with the first chunk's structure
                    merged_data[table_key] = {
                        key: value for key, value in table.items() if key != "rows"
                    }
                    merged_data[table_key]["rows"] = []

                # Extend the rows with the current chunk's rows
                merged_data[table_key]["rows"].extend(table.get("rows", []))

        return merged_data


# Example Usage
if __name__ == "__main__":
    storage = IPFSStorage()

    # Append new data chunks to the linked list and update the CID sequence
    cid1, _ = storage.append_data({"id": 1, "value": "First Entry"})
    cid2, _ = storage.append_data({"id": 2, "value": "Second Entry"})
    cid3, cid_sequence_id = storage.append_data({"id": 3, "value": "Third Entry"})

    # Retrieve the full sequence of CIDs in the structured format
    cid_sequence = storage.get_cid_sequence(cid_sequence_id)
    print("CID Sequence:", json.dumps(cid_sequence, indent=2))

    # Traverse the linked list starting from the latest chunk
    all_data = storage.download_table("table_name")
    print("Retrieved linked data:", all_data)
