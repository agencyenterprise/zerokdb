from web3 import Web3
import json


class ContractController:
    def __init__(self, provider_url, contract_address, abi_path):
        self.web3 = Web3(Web3.HTTPProvider(provider_url))
        self.contract_address = Web3.to_checksum_address(contract_address)
        with open(abi_path, "r") as abi_file:
            self.abi = json.load(abi_file)["abi"]
        self.contract = self.web3.eth.contract(
            address=self.contract_address, abi=self.abi
        )

    def create_sequence(self, table_name, cid, from_address, private_key):
        nonce = self.web3.eth.get_transaction_count(from_address)
        txn = self.contract.functions.createSequence(table_name, cid).build_transaction(
            {
                "chainId": 1337,
                "gas": 2000000,
                "gasPrice": self.web3.to_wei("50", "gwei"),
                "nonce": nonce,
            }
        )
        signed_txn = self.web3.eth.account.sign_transaction(txn, private_key)

        tx_hash = self.web3.eth.send_raw_transaction(signed_txn.raw_transaction)
        tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        # Assuming the event is named "SequenceCreated" and has the fields id, tableName, and cid
        event = self.contract.events.SequenceCreated().process_receipt(tx_receipt)
        return event[0]["args"] if event else None

    def update_sequence_cid(self, sequence_id, new_cid, from_address, private_key):
        nonce = self.web3.eth.get_transaction_count(from_address)
        txn = self.contract.functions.updateSequenceCid(
            sequence_id, new_cid
        ).build_transaction(
            {
                "chainId": 1337,
                "gas": 2000000,
                "gasPrice": self.web3.to_wei("50", "gwei"),
                "nonce": nonce,
            }
        )
        signed_txn = self.web3.eth.account.sign_transaction(txn, private_key)
        tx_hash = self.web3.eth.send_raw_transaction(signed_txn.raw_transaction)
        return self.web3.to_hex(tx_hash)

    def get_sequence_by_id(self, sequence_id):
        return self.contract.functions.getSequenceById(sequence_id).call()


def contract_controller():
    provider_url = "http://localhost:8545"  # Local Ethereum node
    contract_address = "0xDc64a140Aa3E981100a9becA4E685f962f0cF6C9"  # Replace with your deployed contract address
    abi_path = "contracts/artifacts/contracts/TableSequences.sol/TableSequences.json"  # Replace with the path to your contract's ABI
    return ContractController(provider_url, contract_address, abi_path)


def account_details():
    from_address = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"  # Replace with your Ethereum address
    private_key = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"  # Replace with your private key
    return from_address, private_key
