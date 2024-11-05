import os
from typing import Tuple
from libs.table_sequence.TableSequenceClient import TableSequenceClient

from aptos_sdk.account import Account
from aptos_sdk.async_client import RestClient
from aptos_sdk.bcs import Serializer
from aptos_sdk.transactions import (
    EntryFunction,
    TransactionArgument,
    TransactionPayload,
)

class AptosTableSequenceClient(RestClient, TableSequenceClient):
    def __init__(self, node_url: str):
        super().__init__(node_url)
        self.contract_address = os.getenv("APTOS_TABLE_SEQUENCE_CONTRACT")

    async def initialize(self, sender: Account) -> str:
        """Initialize the table sequences"""
        payload = EntryFunction.natural(
            f"{self.contract_address}::table_sequences",
            "initialize",
            [],
            [],
        )
        signed_transaction = await self.create_bcs_signed_transaction(
            sender, TransactionPayload(payload)
        )
        return await self.submit_and_wait_for_bcs_transaction(signed_transaction)

    async def create_sequence(self, sender: Account, table_name: str, cid: str) -> str:
        """Create a new sequence"""
        payload = EntryFunction.natural(
            f"{self.contract_address}::table_sequences",
            "create_sequence",
            [],
            [
                TransactionArgument(table_name, Serializer.str),
                TransactionArgument(cid, Serializer.str),
            ],
        )
        signed_transaction = await self.create_bcs_signed_transaction(
            sender, TransactionPayload(payload)
        )
        return await self.submit_and_wait_for_bcs_transaction(signed_transaction)

    async def update_sequence_cid(self, sender: Account, id: int, new_cid: str) -> str:
        """Update the CID of an existing sequence"""
        payload = EntryFunction.natural(
            f"{self.contract_address}::table_sequences",
            "update_sequence_cid",
            [],
            [
                TransactionArgument(id, Serializer.u64),
                TransactionArgument(new_cid, Serializer.str),
            ],
        )
        signed_transaction = await self.create_bcs_signed_transaction(
            sender, TransactionPayload(payload)
        )
        return await self.submit_and_wait_for_bcs_transaction(signed_transaction)

    async def get_sequence_by_table_name(self, address: str, table_name: str) -> Tuple[int, str, str]:
        """Get a sequence by its table name"""

        result = await self.view(
            f"{self.contract_address}::table_sequences::get_sequence_by_table_name",
            [],
            [address.__str__(), table_name],
        )
        return result
