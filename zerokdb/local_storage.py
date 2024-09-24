import json
import hashlib
import os


class LocalStorage:
    def __init__(self, storage_dir="storage"):
        # Create a directory to store the data locally
        self.storage_dir = storage_dir
        os.makedirs(self.storage_dir, exist_ok=True)
        self.cid = None  # This will hold the latest data chunk CID
        self.cid_sequence_cid = None  # This will hold the CID of the sequence list

    def save(self, data):
        """
        Save data locally to a file and return the file name as the "CID".
        """
        # Compute a file name based on the hash of the data
        json_data = json.dumps(data)
        data_hash = hashlib.sha256(json_data.encode("utf-8")).hexdigest()
        file_name = f"{data_hash}.json"
        file_path = os.path.join(self.storage_dir, file_name)

        # Save the JSON data to the file
        with open(file_path, "w") as file:
            file.write(json_data)

        return file_name  # Return the file name as the "CID"

    def load(self, cid=None):
        """
        Load data from a local file using a given "CID" (file name) or the stored CID.
        """
        if cid:
            self.cid = cid
        if not self.cid:
            return {}
        # Load data from the file
        file_path = os.path.join(self.storage_dir, self.cid)
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                return json.load(file)
        return {}

    def append_linked_data(self, new_data):
        """
        Append new data to the linked list locally and update the CID sequence.
        """
        # Step 1: Retrieve the current CID sequence from local storage
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

        # Step 4: Save the new chunk to local storage and get the new CID (file name)
        new_cid = self.save(chunk)

        # Step 5: Update the sequence with the new chunk details
        chunk_entry = {"chunk_id": new_cid, "chunk_hash": chunk_hash}
        current_sequence["default_sequence"].append(chunk_entry)

        # Step 6: Track the chunk history (versions of this chunk)
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
            # Create a new entry in the chunk history
            current_sequence["chunk_history"].append(
                {"chunk_id": new_cid, "versions": [new_cid]}
            )

        # Step 7: Update the latest chunk CID
        current_sequence["latest_chunk"] = new_cid

        # Step 8: Save the updated CID sequence locally as a new file and get its CID
        self.cid_sequence_cid = self.save_sequence(current_sequence)

        print(f"New chunk CID: {new_cid}")
        print(f"Updated CID sequence CID: {self.cid_sequence_cid}")

        return new_cid

    def load_sequence(self, cid=None):
        """
        Load the CID sequence from a local file. If no sequence exists, return a default structure.
        """
        if cid:
            self.cid_sequence_cid = cid

        if not self.cid_sequence_cid or not os.path.exists(
            os.path.join(self.storage_dir, self.cid_sequence_cid)
        ):
            # Return default structure if no sequence exists
            return {"default_sequence": [], "chunk_history": [], "latest_chunk": None}

        # Load the current CID sequence from the local file
        with open(os.path.join(self.storage_dir, self.cid_sequence_cid), "r") as file:
            return json.load(file)

    def save_sequence(self, sequence):
        """
        Save the CID sequence to a new local file and return the new file name as the CID.
        """
        # Convert sequence to JSON
        json_sequence = json.dumps(sequence)

        # Hash the sequence to create a unique file name
        sequence_hash = hashlib.sha256(json_sequence.encode("utf-8")).hexdigest()
        sequence_file_name = f"{sequence_hash}.json"
        sequence_file_path = os.path.join(self.storage_dir, sequence_file_name)

        # Save the sequence to the new file
        with open(sequence_file_path, "w") as file:
            file.write(json_sequence)

        return sequence_file_name

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
        Return the stored sequence of CIDs from the local file.
        """
        return self.load_sequence()


# Example Usage
if __name__ == "__main__":
    storage = LocalStorage()

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
