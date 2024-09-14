from fastapi import FastAPI
import json
import hashlib

from zerokdb.ipfs_storage import IPFSStorage

app = FastAPI()

# Initialize IPFSStorage
storage = IPFSStorage()

@app.get("/cid-sequence")
async def get_cid_sequence():
    try:
        cid_sequence = storage.get_cid_sequence()
        return cid_sequence
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
