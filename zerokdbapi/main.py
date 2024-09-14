from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from zerokdbapi.ipfs_service import IPFSService

app = FastAPI()
ipfs_service = IPFSService()


class Payload(BaseModel):
    data: dict


@app.post("/save")
async def save_sequence(payload: Payload):
    """
    Endpoint to save sequence data to IPFS.
    """
    try:
        cid = ipfs_service.save_to_ipfs(payload.data)
        return {"cid": cid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
async def save_payload(payload: Payload):
    try:
        cid = ipfs_service.save_to_ipfs(payload.data)
        return {"cid": cid}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
