from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Union
from zerokdb.ipfs_storage import IPFSStorage
from zerokdbapi.controller import (
    add_table_sequence,
    update_table_sequence_cid,
    get_table_sequence_by_id,
    get_table_sequence_by_table_name,
)
from zerokdbapi.api.table_sequence import router as TableSequenceRouter
from zerokdbapi.contract_controller import ContractController
from zerokdbapi.config import settings
from fastapi.concurrency import run_in_threadpool

contract_controller = ContractController(
    settings.provider_url, settings.contract_address, settings.abi_path
)

app = FastAPI()

app.include_router(TableSequenceRouter, prefix="/table-sequence", include_in_schema=False)

class TableData(BaseModel):
    columns: List[str]
    column_types: Dict[str, str]
    rows: List[List[Union[int, str]]]
    indexes: Dict[str, Any]


class AppendDataPayload(BaseModel):
    data: Dict[str, Any]
    table_name: str


class EntityPayload(BaseModel):
    entity_name: str
    data: Dict[str, Any]


@app.get("/sequence/{entity_id}")
async def get_cid_sequence(entity_id: str):
    try:
        sequence = await run_in_threadpool(get_table_sequence_by_id, entity_id)
        if not sequence:
            raise HTTPException(status_code=404, detail="Entity not found.")
        sequence_cid = sequence.cid
        storage = IPFSStorage()
        data = await run_in_threadpool(storage.load_sequence, sequence_cid)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/entity")
async def create_entity(EntityPayload: EntityPayload):
    try:
        existing_sequence = await run_in_threadpool(
            get_table_sequence_by_table_name, EntityPayload.entity_name
        )
        if existing_sequence:
            raise HTTPException(
                status_code=400, detail="Invalid entity name. Entity already exists."
            )
        storage = IPFSStorage()
        data_cid, sequence_cid = await run_in_threadpool(
            storage.append_data, EntityPayload.data, "0x0"
        )
        sequence = await run_in_threadpool(
            add_table_sequence, EntityPayload.entity_name, sequence_cid
        )
        return {
            "id": sequence.id,
            "table_name": sequence.table_name,
            "data_cid": data_cid,
            "sequence_cid": sequence.cid,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/append-data/id/{entity_id}")
async def append_data(payload: AppendDataPayload, entity_id: str):
    try:
        sequence = await run_in_threadpool(get_table_sequence_by_id, entity_id)
        if not sequence:
            raise HTTPException(status_code=404, detail="Entity not found.")
        storage = IPFSStorage()
        data_cid, cid_sequence = await run_in_threadpool(
            storage.append_data, payload.data, sequence.cid
        )
        await run_in_threadpool(update_table_sequence_cid, sequence.id, cid_sequence)
        return {"data_cid": data_cid, "sequence_cid": cid_sequence}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/append-data")
async def append_data_by_table_name(payload: AppendDataPayload):
    try:
        table_name = payload.table_name
        sequence = await run_in_threadpool(get_table_sequence_by_table_name, table_name)
        if not sequence:
            raise HTTPException(status_code=404, detail="Entity not found.")
        storage = IPFSStorage()
        data_cid, cid_sequence = await run_in_threadpool(
            storage.append_data, payload.data, sequence.cid
        )
        await run_in_threadpool(update_table_sequence_cid, sequence.id, cid_sequence)
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
        cid_sequence = sequence[2]
        data_cid, cid_sequence = storage.append_data(payload.data, cid_sequence)
        contract_controller.update_sequence_cid(
            entity_id, cid_sequence, settings.from_address, settings.private_key
        )
        return {"data_cid": data_cid, "sequence_cid": cid_sequence}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
