from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from zerokdbapi.ipfs_service import IPFSService

app = FastAPI()
ipfs_service = IPFSService()


class Payload(BaseModel):
    data: dict


@app.post("/save_sequence")
async def save_sequence(payload: Payload):
    try:
        cid = ipfs_service.save_to_ipfs(payload.data)
        return {"cid": cid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
