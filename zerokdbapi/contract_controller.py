from web3 import Web3
from web3.middleware import geth_poa_middleware
import json

class ContractController:
    def __init__(self, provider_url, contract_address, abi_path):
        self.web3 = Web3(Web3.HTTPProvider(provider_url))
        self.web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.contract_address = Web3.toChecksumAddress(contract_address)
        with open(abi_path, 'r') as abi_file:
            self.abi = json.load(abi_file)
        self.contract = self.web3.eth.contract(address=self.contract_address, abi=self.abi)

    def create_sequence(self, table_name, cid, from_address, private_key):
        nonce = self.web3.eth.getTransactionCount(from_address)
        txn = self.contract.functions.createSequence(table_name, cid).buildTransaction({
            'chainId': 1337,
            'gas': 2000000,
            'gasPrice': self.web3.toWei('50', 'gwei'),
            'nonce': nonce
        })
        signed_txn = self.web3.eth.account.signTransaction(txn, private_key=private_key)
        tx_hash = self.web3.eth.sendRawTransaction(signed_txn.rawTransaction)
        return self.web3.toHex(tx_hash)

    def update_sequence_cid(self, sequence_id, new_cid, from_address, private_key):
        nonce = self.web3.eth.getTransactionCount(from_address)
        txn = self.contract.functions.updateSequenceCid(sequence_id, new_cid).buildTransaction({
            'chainId': 1337,
            'gas': 2000000,
            'gasPrice': self.web3.toWei('50', 'gwei'),
            'nonce': nonce
        })
        signed_txn = self.web3.eth.account.signTransaction(txn, private_key=private_key)
        tx_hash = self.web3.eth.sendRawTransaction(signed_txn.rawTransaction)
        return self.web3.toHex(tx_hash)

    def get_sequence_by_id(self, sequence_id):
        return self.contract.functions.getSequenceById(sequence_id).call()
