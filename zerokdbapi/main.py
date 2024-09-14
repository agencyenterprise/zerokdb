from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from zerokdb.ipfs_storage import IPFSStorage

app = FastAPI()
storage = IPFSStorage()


class Payload(BaseModel):
    data: dict


@app.post("/save_sequence")
async def save_sequence(payload: Payload):
    try:
        # Use the append_linked_data method to save data
        cid = storage.append_linked_data(payload.data)
        return {"cid": cid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
