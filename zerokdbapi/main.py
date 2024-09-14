from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel
from typing import Dict, Any
from zerokdb.ipfs_storage import IPFSStorage
from zerokdbapi.controller import (
    add_table_sequence,
    update_table_sequence_cid,
    get_table_sequence_by_id,
)
from zerokdbapi.contract_controller import ContractController
from zerokdbapi.config import settings

contract_controller = ContractController(
    settings.provider_url, settings.contract_address, settings.abi_path
)

app = FastAPI()


class AppendDataPayload(BaseModel):
    data: Dict[str, Any]


class EntityPayload(BaseModel):
    entity_name: str


@app.get("/sequence/{entity_id}")
async def get_cid_sequence(entity_id: str):
    try:
        sequence = get_table_sequence_by_id(entity_id)
        if not sequence:
            raise HTTPException(status_code=404, detail="Entity not found.")
        sequence_cid = sequence.cid
        storage = IPFSStorage()
        data = storage.load_sequence(sequence_cid)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/entity")
async def create_entity(EntityPayload: EntityPayload):
    try:
        sequence = add_table_sequence(EntityPayload.entity_name)
        return {"id": sequence.id, "table_name": sequence.table_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/append-data/{entity_id}")
async def append_data(payload: AppendDataPayload, entity_id: str):
    try:
        sequence = get_table_sequence_by_id(entity_id)
        if not sequence:
            raise HTTPException(status_code=404, detail="Entity not found.")
        storage = IPFSStorage()
        data_cid, cid_sequence = storage.append_data(payload.data)
        update_table_sequence_cid(entity_id, cid_sequence)
        return {"data_cid": data_cid, "sequence_cid": cid_sequence}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/dsequence/{entity_id}")
async def dget_cid_sequence(entity_id: str):
    try:
        sequence = contract_controller.get_sequence_by_id(entity_id)
        if not sequence:
            raise HTTPException(status_code=404, detail="Entity not found.")
        sequence_cid = sequence[2]
        storage = IPFSStorage()
        data = storage.load_sequence(sequence_cid)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/dentity")
async def dcreate_entity(EntityPayload: EntityPayload):
    try:
        sequence = contract_controller.create_sequence(
            EntityPayload.entity_name,
            "0x0",
            settings.from_address,
            settings.private_key,
        )
        return {"id": sequence["id"], "table_name": sequence["tableName"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/dappend-data/{entity_id}")
async def dappend_data(payload: AppendDataPayload, entity_id: str):
    try:
        sequence = contract_controller.get_sequence_by_id(entity_id)
        if not sequence:
            raise HTTPException(status_code=404, detail="Entity not found.")
        storage = IPFSStorage()
        data_cid, cid_sequence = storage.append_data(payload.data)
        contract_controller.update_sequence_cid(
            entity_id, cid_sequence, settings.from_address, settings.private_key
        )
        return {"data_cid": data_cid, "sequence_cid": cid_sequence}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
def create_new_table(entity_name: str):
    """
    Call the POST /entity endpoint to create a new table.
    """
    client = TestClient(app)
    response = client.post("/entity", json={"entity_name": entity_name})
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail=response.text)
