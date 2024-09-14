from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from zerokdb.ipfs_storage import IPFSStorage
from fastapi.responses import FileResponse

app = FastAPI()

@app.get("/download")
async def download_app():
    file_path = "path/to/your/app/file"  # Replace with the actual file path
    return FileResponse(file_path, media_type='application/octet-stream', filename="app_file_name")  # Replace with the actual file name
storage = IPFSStorage()


class Payload(BaseModel):
    data: Dict[str, Any]


