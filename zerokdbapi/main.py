from fastapi import FastAPI, HTTPException
from fastapi import FastAPI, HTTPException
from zerokdbapi.db import Base, engine, TableSequences
from pydantic import BaseModel
from typing import Dict, Any
from zerokdb.ipfs_storage import IPFSStorage

app = FastAPI()

storage = IPFSStorage()

class Payload(BaseModel):
    data: Dict[str, Any]

@app.get("/cid-sequence")
async def get_cid_sequence():
    try:
        cid_sequence = storage.get_cid_sequence()
        return cid_sequence
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/append-data")
async def append_data(payload: Payload):
    try:
        new_cid = storage.append_data(payload.data)
        return {"new_cid": new_cid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
from pydantic import BaseModel
from typing import Dict, Any
from zerokdb.ipfs_storage import IPFSStorage
from fastapi.responses import FileResponse

app = FastAPI()

storage = IPFSStorage()


class Payload(BaseModel):
    data: Dict[str, Any]


