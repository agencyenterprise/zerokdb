from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from zerokdb.ipfs_storage import IPFSStorage

app = FastAPI()
storage = IPFSStorage()


class Payload(BaseModel):
    data: Dict[str, Any]


