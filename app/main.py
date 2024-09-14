from fastapi import FastAPI
import json
import hashlib

from zerokdb.ipfs_storage import IPFSStorage

app = FastAPI()

# Initialize IPFSStorage
storage = IPFSStorage()

@app.post("/save")
async def save_data(data: dict):
    # Use the append_linked_data method to save data
    new_cid = storage.append_linked_data(data)
    return {"cid": new_cid, "cid_sequence_cid": storage.cid_sequence_cid}
