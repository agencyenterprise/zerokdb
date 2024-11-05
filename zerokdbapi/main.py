import json
import os
from typing import Any, Dict

from libs.table_sequence.TableSequenceClient import TableSequenceClient
from libs.table_sequence.AptosTableSequenceClient import AptosTableSequenceClient
from libs.table_sequence.EvmTableSequenceClient import EvmTableSequenceClient

from aptos_sdk.account import Account
from config import settings
from fastapi import Depends, FastAPI, HTTPException, Header
from pydantic import BaseModel
from TextToEmbedding import TextToEmbedding

from zerokdb.ipfs_storage import IPFSStorage

from dotenv import load_dotenv

load_dotenv()
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

async def get_table_sequence_client(chain: str = Header(None)):
    if chain == "evm":
        node_url = os.getenv("EVM_NODE_URL")
        return EvmTableSequenceClient(node_url)

    if chain == "aptos":
        node_url = os.getenv("APTOS_NODE_URL", "https://fullnode.testnet.aptoslabs.com/v1")
        return AptosTableSequenceClient(node_url)

    raise HTTPException(status_code=400, detail="Invalid chain")

async def get_sender():
    return Account.load_key(os.getenv("APTOS_PRIVATE_KEY"))

@app.get("/health")
async def health_check():
    return {"status": "OK", "message": "Service is up and running"}

@app.post("/sequence/name")
async def get_cid_sequence_by_table_name(
    payload: EntityNamePayload,
    account: Account = Depends(get_sender),
    client: TableSequenceClient = Depends(get_table_sequence_client)
):
    try:
        try:
            result = await client.get_sequence_by_table_name(account.address().__str__(), payload.entity_name)
        except Exception as e:
            if "ABORTED" in str(e) and "get_sequence_by_table_name" in str(e):
                return {}
            else:
                raise
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
        print('Error', e)
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
        storage = IPFSStorage(pinata_api_key=settings.pinata_api_key)
        data_cid, sequence_cid = storage.append_data(EntityPayload.data, "0x0")
        await client.create_sequence(account, EntityPayload.entity_name, sequence_cid)
        return {
            "data_cid": data_cid,
            "sequence_cid": sequence_cid,
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

        storage = IPFSStorage(pinata_api_key=settings.pinata_api_key)
        data_cid, cid_sequence = storage.append_data(payload.data, cid)
        await client.update_sequence_cid(account, id_, cid_sequence)

        return {"data_cid": data_cid, "sequence_cid": cid_sequence}
    except HTTPException:
        raise
    except Exception as e:
        print('Error while appending data: ', e)
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
