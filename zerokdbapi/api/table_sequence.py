import json
import os
from fastapi import APIRouter, Depends
from aptos_sdk.account import Account
from typing import Tuple

from zerokdbapi.TableSequenceClient import TableSequenceClient

router = APIRouter()


async def get_table_sequence_client():
    node_url = os.getenv("APTOS_NODE_URL", "https://fullnode.testnet.aptoslabs.com/v1")
    return TableSequenceClient(node_url)


async def get_sender():
    return Account.load_key(os.getenv("APTOS_PRIVATE_KEY"))


@router.post("/initialize")
async def initialize_endpoint(
    client: TableSequenceClient = Depends(get_table_sequence_client),
    sender: Account = Depends(get_sender),
):
    return await client.initialize(sender)


@router.post("/create-sequence")
async def create_sequence_endpoint(
    table_name: str,
    cid: str,
    client: TableSequenceClient = Depends(get_table_sequence_client),
    sender: Account = Depends(get_sender),
):
    return await client.create_sequence(sender, table_name, cid)


@router.post("/update-sequence-cid")
async def update_sequence_cid_endpoint(
    id: int,
    new_cid: str,
    client: TableSequenceClient = Depends(get_table_sequence_client),
    sender: Account = Depends(get_sender),
):
    return await client.update_sequence_cid(sender, id, new_cid)


@router.get("/name")
async def get_sequence_by_id_endpoint(
    address: str,
    table_name: str,
    client: TableSequenceClient = Depends(get_table_sequence_client),
) -> Tuple[int, str, str]:
    result = await client.get_sequence_by_table_name(address, table_name)
    decoded_result = result.decode("utf-8")
    parsed_result = json.loads(decoded_result)
    return (int(parsed_result[0]), parsed_result[1], parsed_result[2])
