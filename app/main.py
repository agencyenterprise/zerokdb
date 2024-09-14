from fastapi import FastAPI
import json
import hashlib

app = FastAPI()

@app.post("/save")
async def save_data(data: dict):
    # Step 1: Compute the hash of the chunk's data
    chunk_hash_data = json.dumps(data).encode("utf-8")  # Hash only the 'data' part
    chunk_hash = hashlib.sha256(chunk_hash_data).hexdigest()

    # Step 2: Save the new chunk to IPFS and get the new CID
    new_cid = save_to_ipfs(data)  # Assume save_to_ipfs is a function that saves data to IPFS

    # Step 3: Update the sequence with the new chunk details
    chunk_entry = {"chunk_id": new_cid, "chunk_hash": chunk_hash}
    current_sequence["default_sequence"].append(chunk_entry)

    # Step 4: Track the chunk history (versions of this chunk)
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

    # Step 5: Update the latest chunk CID
    current_sequence["latest_chunk"] = new_cid

    # Step 6: Save the updated CID sequence to IPFS and store its CID
    cid_sequence_cid = save_to_ipfs(current_sequence)  # Assume save_to_ipfs is a function that saves data to IPFS

    return {"cid": new_cid, "cid_sequence_cid": cid_sequence_cid}
