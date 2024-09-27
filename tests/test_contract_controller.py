import pytest
from zerokdbapi.contract_controller import ContractController
from uuid import uuid4
from zerokdbapi.config import settings


@pytest.fixture
def contract_controller():
    provider_url = "http://localhost:8545"  # Local Ethereum node
    contract_address = (
        settings.contract_address
    )  # Replace with your deployed contract address
    abi_path = "contracts/artifacts/contracts/TableSequences.sol/TableSequences.json"  # Replace with the path to your contract's ABI
    return ContractController(provider_url, contract_address, abi_path)


@pytest.fixture
def account_details():
    from_address = settings.from_address  # Replace with your Ethereum address
    private_key = settings.private_key  # Replace with your private key
    return from_address, private_key


def test_create_sequence(contract_controller: ContractController, account_details):
    from_address, private_key = account_details
    sequence = contract_controller.create_sequence(
        "TestTable", "CID123", from_address, private_key
    )
    assert sequence["tableName"] == "TestTable"
    assert sequence["cid"] == "CID123"


def test_update_sequence_cid(contract_controller: ContractController, account_details):
    from_address, private_key = account_details
    cid = str(uuid4())
    contract_controller.update_sequence_cid(1, cid, from_address, private_key)
    sequence = contract_controller.get_sequence_by_id(1)
    assert sequence[2] == str(cid)


def test_get_sequence_by_id(contract_controller: ContractController):
    sequence = contract_controller.get_sequence_by_id(1)
    print(f"Sequence retrieved: {sequence}")
