import pytest
from zerokdbapi.contract_controller import ContractController


@pytest.fixture
def contract_controller():
    provider_url = "http://localhost:8545"  # Local Ethereum node
    contract_address = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"  # Replace with your deployed contract address
    abi_path = "contracts/artifacts/contracts/TableSequences.sol/TableSequences.json"  # Replace with the path to your contract's ABI
    return ContractController(provider_url, contract_address, abi_path)


@pytest.fixture
def account_details():
    from_address = "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266"  # Replace with your Ethereum address
    private_key = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"  # Replace with your private key
    return from_address, private_key


def test_create_sequence(contract_controller: ContractController, account_details):
    from_address, private_key = account_details
    tx_hash = contract_controller.create_sequence(
        "TestTable", "CID123", from_address, private_key
    )
    print(f"Transaction hash for create_sequence: {tx_hash}")


def test_update_sequence_cid(contract_controller: ContractController, account_details):
    from_address, private_key = account_details
    tx_hash = contract_controller.update_sequence_cid(
        1, "CID456", from_address, private_key
    )
    print(f"Transaction hash for update_sequence_cid: {tx_hash}")


def test_get_sequence_by_id(contract_controller: ContractController):
    sequence = contract_controller.get_sequence_by_id(1)
    print(f"Sequence retrieved: {sequence}")
