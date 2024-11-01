import os
from typing import Tuple
from zerokdbapi.libs.table_sequence.TableSequenceClient import TableSequenceClient
from web3 import Web3

class EvmTableSequenceClient(TableSequenceClient):
    def __init__(self, node_url: str):
        super().__init__(node_url)
        self.contract_address = os.getenv("EVM_TABLE_SEQUENCE_CONTRACT")

    async def initialize(self, sender: any) -> str:
        pass

    async def create_sequence(self, sender: any, table_name: str, cid: str) -> str:
        w3 = Web3(Web3.HTTPProvider(self.node_url))
        
        contract = w3.eth.contract(
            address=self.contract_address,
            abi=[{
                "inputs": [
                    {"internalType": "string", "name": "tableName", "type": "string"},
                    {"internalType": "string", "name": "cid", "type": "string"}
                ],
                "name": "createSequence",
                "outputs": [],
                "stateMutability": "nonpayable", 
                "type": "function"
            }]
        )

        transaction = contract.functions.createSequence(
            table_name,
            cid
        ).build_transaction({
            'from': sender.address,
            'nonce': w3.eth.get_transaction_count(sender.address),
            'gas': 200000,
            'gasPrice': w3.eth.gas_price
        })

        signed_txn = w3.eth.account.sign_transaction(transaction, sender.private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return tx_receipt.transactionHash.hex()

    async def update_sequence_cid(self, sender: any, id: int, new_cid: str) -> str:
        w3 = Web3(Web3.HTTPProvider(self.node_url))
        
        contract = w3.eth.contract(
            address=self.contract_address,
            abi=[{
                "inputs": [
                    {"internalType": "uint256", "name": "id", "type": "uint256"},
                    {"internalType": "string", "name": "newCid", "type": "string"}
                ],
                "name": "updateSequenceCid",
                "outputs": [],
                "stateMutability": "nonpayable",
                "type": "function"
            }]
        )

        transaction = contract.functions.updateSequenceCid(
            id,
            new_cid
        ).build_transaction({
            'from': sender.address,
            'nonce': w3.eth.get_transaction_count(sender.address),
            'gas': 200000,
            'gasPrice': w3.eth.gas_price
        })

        signed_txn = w3.eth.account.sign_transaction(transaction, sender.private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return tx_receipt.transactionHash.hex()

    async def get_sequence_by_table_name(self, address: str, table_name: str) -> Tuple[int, str, str]:
        w3 = Web3(Web3.HTTPProvider(self.node_url))
        
        contract = w3.eth.contract(
            address=self.contract_address,
            abi=[{
                "inputs": [
                    {"internalType": "address", "name": "owner", "type": "address"},
                    {"internalType": "string", "name": "tableName", "type": "string"}
                ],
                "name": "getSequenceByTableName",
                "outputs": [
                    {"internalType": "uint256", "name": "", "type": "uint256"},
                    {"internalType": "string", "name": "", "type": "string"},
                    {"internalType": "string", "name": "", "type": "string"}
                ],
                "stateMutability": "view",
                "type": "function"
            }]
        )

        result = contract.functions.getSequenceByTableName(
            address,
            table_name
        ).call()

        return result
