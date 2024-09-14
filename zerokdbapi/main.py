from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from zerokdb.ipfs_storage import IPFSStorage
from fastapi.responses import FileResponse

app = FastAPI()

storage = IPFSStorage()


class Payload(BaseModel):
    data: Dict[str, Any]


