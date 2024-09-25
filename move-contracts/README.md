## Aptos Smart Contracts

Contracts are written in Move and tested with Aptos Move CLI. Please install Aptos CLI.
https://aptos.dev/en/build/cli

#### Testing

To test the contract, you can use the following command:

```bash
aptos move test --named-addresses escrow_native=default
```

#### Deployment

Update the address in Move.toml file to your address, then compile and deploy the contract:

[dev-addresses]
escrow_native = "YOUR_ADDRESS"

First you need to compile the contract, replace address with your address:

```bash
❯ aptos move compile --named-addresses escrow_native=YOUR_ADDRESS
```

Then you can deploy the contract to the network:

```bash
aptos move deploy-object --named-addresses escrow_native
```

You will see the following output:

```bash
Do you want to deploy this package at object address 0x3668203b45b643a2d929f0db49852140fd96d190d1765e8bf0bc33f44716061b [yes/no] >
yes
package size 4403 bytes
Do you want to submit a transaction for a range of [320500 - 480700] Octas at a gas unit price of 100 Octas? [yes/no] >
yes
Transaction submitted: https://explorer.aptoslabs.com/txn/0x5e89fedb0eb2aa6eb2ba4a317184492f2568a3904ac5ec53e01c4dc12881ef8a?network=devnet
Code was successfully deployed to object address 0x3668203b45b643a2d929f0db49852140fd96d190d1765e8bf0bc33f44716061b
{
  "Result": "Success"
}
```

### Escrow Native

The Escrow Native contract provides functionality for managing escrow transactions on the Aptos blockchain. Here's how to use the EscrowNativeClient to interact with this contract:

```python
import os
from aptos_sdk.async_client import RestClient
from aptos_sdk.account import Account, AccountAddress
from blockchain.aptos.EscrowNativeClient import EscrowNativeClient

async def main():
    NODE_URL = os.getenv("APTOS_NODE_URL", "https://fullnode.devnet.aptoslabs.com/v1")
    rest_client = RestClient(NODE_URL)
    escrow_client = EscrowNativeClient(rest_client)

    # Load accounts
    admin = Account.load_key(os.getenv("ADMIN_PRIVATE_KEY"))
    user = Account.load_key(os.getenv("USER_PRIVATE_KEY"))
    relayer = AccountAddress.from_hex(os.getenv("RELAYER_ADDRESS"))
    payee = AccountAddress.from_hex(os.getenv("PAYEE_ADDRESS"))

    # Initialize the escrow contract (admin only)
    txn_hash = await escrow_client.initialize(admin, 1000000, relayer)  # 1% fee
    await escrow_client.wait_for_transaction(txn_hash)
    print("Escrow initialized")

    # Initialize user escrow
    txn_hash = await escrow_client.initialize_user(user)
    await escrow_client.wait_for_transaction(txn_hash)
    print("User escrow initialized")

    # Deposit funds
    amount = 1000000  # 1 APT
    txn_hash = await escrow_client.deposit(user, amount)
    await escrow_client.wait_for_transaction(txn_hash)
    print(f"Deposited {amount} APT")

    # Check balance
    balance = await escrow_client.balance_of(user.account_address)
    print(f"User balance: {balance}")

    # Pay from escrow
    pay_amount = 500000  # 0.5 APT
    txn_hash = await escrow_client.pay(admin, user.account_address, payee, pay_amount)
    await escrow_client.wait_for_transaction(txn_hash)
    print(f"Paid {pay_amount} APT to {payee}")

    # Check balance again
    balance = await escrow_client.balance_of(user.account_address)
    print(f"User balance after payment: {balance}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```


### Table Sequence

The Table Sequence contract provides functionality to create and manage sequences of data stored in tables on the Aptos blockchain. Here's how to use the TableSequenceClient to interact with this contract:

```python
    NODE_URL = os.getenv("APTOS_NODE_URL", "https://fullnode.devnet.aptoslabs.com/v1")
    rest_client = RestClient(NODE_URL)
    aptos_client = TableSequenceClient(NODE_URL)
    account = Account.load_key(os.getenv("APTOS_PRIVATE_KEY"))

    a_alice_balance = await rest_client.account_balance(account.account_address)
    print(a_alice_balance)

    txn_hash = await aptos_client.initialize(account)
    print(txn_hash)
    await aptos_client.wait_for_transaction(txn_hash)

    txn_hash = await aptos_client.create_sequence(account, "designations", "0x1")
    print(txn_hash)
    await aptos_client.wait_for_transaction(txn_hash)

    print("Created")

    txn_hash = await aptos_client.update_sequence_cid(account, 1, "0x2")
    print(txn_hash)
    await aptos_client.wait_for_transaction(txn_hash)

    print("Updated")
```
