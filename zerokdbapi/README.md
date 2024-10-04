# ZEROKDB

ZEROKDB is a lightweight protocol and file-based database system with support for basic SQL operations and vector similarity search. It is designed to be simple and easy to use and fully decentralized. By being part of the [0k labs ecosystem](https://0k.wtf), ZEROKDB it's powered by ZKPs (Zero-Knowledge Proofs) acting as reward confirmation for users providing idle hardware to run the protocol. The rewards are granted in APTOS

![ZEROKDB](docs/zerokdb.png)

## Features

- Create, insert, and query tables using SQL-like syntax.
- Support for various data types including strings, integers, floats, booleans, datetimes, and lists of floats.
- Perform cosine similarity searches on vector data.
- IPFS support for distributed storage.
- Decentralized version controll powered by a smart contract
- Change tracking for database operations.

## Installation

To install the necessary dependencies using Poetry, use the following command:

```bash
poetry install
```

## Usage

### Creating a Table

To create a table, use the `CREATE TABLE` command:

```sql
CREATE TABLE users (id int, name string)
```

### Inserting Data

To insert data into a table, use the `INSERT INTO` command:

```sql
INSERT INTO users (id, name) VALUES (1, 'Alice')
```

### Querying Data

To query data from a table, use the `SELECT` command:

```sql
SELECT * FROM users
```

### Vector Similarity Search

To perform a cosine similarity search on vector data, use the `COSINE SIMILARITY` clause:

```sql
SELECT id FROM vectors COSINE SIMILARITY embedding WITH [0.1, 0.2, 0.3]
```

### Limiting Results

To limit the number of results returned, use the `LIMIT` clause:

```sql
SELECT * FROM users LIMIT 10
```

## Running Tests

To run the tests for this project, follow these steps:

1. **Configure your .env file**

   Create a .env file out of the .env.example file on the root folder:

   ```bash
   PINATA_API_KEY= #get a pinata key to search the sequences for the database on IPFS
   API_HOST="http://localhost:8001" # replace with the URL where this will be running

   APTOS_TABLE_SEQUENCE_CONTRACT=0x9f741dc033b45ddaf27b5ab711572f2f042fc9d2a3a49dbf3e215c6d9f02a72b # replace with teh contract on aptos that holds all the sequences from your database
   APTOS_PRIVATE_KEY= #private key to access and handle the contract with the sequences
   ```

1. **Run FastAPI with Uvicorn:**

   Start the FastAPI server using Uvicorn:

   ```bash
   uvicorn main:app --reload --port 8001
   ```

   Obs.: sometimes you neew to with `python -m` at the begining depending on your venv config

   The API will be available at `http://127.0.0.1:8001`.

1. **Run the python tests:**
   ```bash
   pytest
   ```

## NOTES:

Although the database nodes can be fully decentralized, this project relies on a central authority for persisting data on ipfs.

### Forking the protocol

If you wanna setup and run your own application our of **zerokdb**, you will have to configure a pinata account capable of pinning files to IPFS, and you must
deploy the rest api present on this folder.

- Consider running the REST API on akash to have a decentralized infraestructure.

### Running a node

If you just wanna run your own node in the **zerokdb** network you will need a pinata account to read from IPFS.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.

## License

This project is licensed under the MIT License.
