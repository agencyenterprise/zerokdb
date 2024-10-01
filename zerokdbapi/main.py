import json
from typing import Any, Dict

from aptos_sdk.account import Account
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

from zerokdb.ipfs_storage import IPFSStorage
from zerokdbapi import TableSequenceClient
from zerokdbapi.api.table_sequence import get_sender, get_table_sequence_client
from zerokdbapi.controller import add_table_sequence, update_table_sequence_cid
from zerokdbapi.TextToEmbedding import TextToEmbedding

app = FastAPI()


class AppendDataPayload(BaseModel):
    data: Dict[str, Any]
    table_name: str


class EntityPayload(BaseModel):
    entity_name: str
    data: Dict[str, Any]


class EmbeddingPayload(BaseModel):
    text: str


class EntityNamePayload(BaseModel):
    entity_name: str


@app.post("/sequence/name")
async def get_cid_sequence_by_table_name(
    payload: EntityNamePayload,
    account: Account = Depends(get_sender),
    client: TableSequenceClient = Depends(get_table_sequence_client)
):
    try:
        result = await client.get_sequence_by_table_name(str(account.address()), payload.entity_name)
        if not result:
            raise HTTPException(status_code=404, detail="Entity not found.")

        decoded_result = result.decode("utf-8")
        parsed_result = json.loads(decoded_result)
        id_, table_name, cid = int(parsed_result[0]), parsed_result[1], parsed_result[2]

        return {
            "id": id_,
            "table_name": table_name,
            "sequence_cid": cid,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/entity")
async def create_entity(
    EntityPayload: EntityPayload,
    account: Account = Depends(get_sender),
    client: TableSequenceClient = Depends(get_table_sequence_client)
):
    try:
        try:
            existing_sequence = await client.get_sequence_by_table_name(account.address().__str__(), EntityPayload.entity_name)
        except Exception as e:
            if "ABORTED" in str(e) and "get_sequence_by_table_name" in str(e):
                existing_sequence = None
            else:
                raise
        if existing_sequence:
            raise HTTPException(
                status_code=400, detail="Invalid entity name. Entity already exists."
            )
        storage = IPFSStorage()
        data_cid, sequence_cid = storage.append_data(EntityPayload.data, "0x0")
        sequence = add_table_sequence(EntityPayload.entity_name, sequence_cid)
        await client.create_sequence(account, EntityPayload.entity_name, sequence_cid)
        return {
            "id": sequence.id,
            "table_name": sequence.table_name,
            "data_cid": data_cid,
            "sequence_cid": sequence.cid,
        }
    except Exception as e:
        print('Error', e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/append-data")
async def append_data_by_table_name(
    payload: AppendDataPayload,
    account: Account = Depends(get_sender),
    client: TableSequenceClient = Depends(get_table_sequence_client)
):
    try:
        sequence = await client.get_sequence_by_table_name(str(account.address()), payload.table_name)
        if not sequence:
            raise HTTPException(status_code=404, detail="Entity not found.")

        decoded_result = sequence.decode("utf-8")
        parsed_result = json.loads(decoded_result)
        id_, _, cid = int(parsed_result[0]), parsed_result[1], parsed_result[2]

        storage = IPFSStorage()
        data_cid, cid_sequence = storage.append_data(payload.data, cid)
        update_table_sequence_cid(id_, cid_sequence)
        await client.update_sequence_cid(account, id_, cid_sequence)

        return {"data_cid": data_cid, "sequence_cid": cid_sequence}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/convert-to-embedding")
async def convert_to_embedding(payload: EmbeddingPayload):
    try:
        text_to_embedding = TextToEmbedding()
        embedding = text_to_embedding.convert(payload.text)

        if not isinstance(embedding, list):
            raise HTTPException(status_code=500, detail="Failed to generate valid embedding.")

        return {"embedding": embedding}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
