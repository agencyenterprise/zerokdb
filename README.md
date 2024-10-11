# ZeroKDB Platform

ZeroKDB Platform is a decentralized database ecosystem built on the Aptos blockchain. It leverages a network of worker nodes to execute queries, store data on IPFS, and ensure data integrity through cryptographic proofs. The platform is composed of several interconnected components that work together to provide a secure, scalable, and efficient database solution.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
  - [Components](#components)
    - [Hub](#hub)
    - [Worker](#worker)
    - [zerokdb Library](#zerokdb)
    - [zerokdb.api](#zerokdbapi)
- [Interaction Flow](#interaction-flow)
- [System Interactions](#system-interactions)

## Overview

The ZeroKDB Platform is designed to facilitate decentralized data management by integrating blockchain technology with distributed storage systems. It ensures that data queries are executed reliably and securely, with results verifiable through cryptographic proofs. The platform's modular architecture allows for flexibility and scalability, making it suitable for various applications that require decentralized data processing and storage.

## Architecture

The ZeroKDB Platform is all deployed on Akash for decentralization and reliability and it comprises four main components:

### Components

#### Hub

The **Hub** is the central coordinator of the ZeroKDB Platform. It is responsible for managing worker registrations, distributing query requests, verifying responses, and handling payments to workers. The Hub ensures that queries from the frontend are efficiently allocated to available workers and that the integrity of the responses is maintained.

**Key Responsibilities:**

- **Worker Registration:** Allows worker nodes to register and deregister with the platform.
- **Query Distribution:** Receives query requests from the frontend and assigns them to appropriate workers.
- **Response Verification:** Validates the responses and proofs submitted by workers to ensure data integrity.
- **Payment Management:** Allocates credits to workers based on verified proofs, using user-locked credits as payment.

#### Worker

**Workers** are the execution nodes in the ZeroKDB Platform. Each worker is responsible for processing queries, interacting with the decentralized database, and generating proofs for the executed queries. Workers operate independently, ensuring scalability and fault tolerance within the system.

**Key Responsibilities:**

- **Query Execution:** Receives queries from the Hub and executes them locally using the `zerokdb` library.
- **Data Storage:** Saves query results to IPFS, ensuring decentralized and immutable storage.
- **Contract Interaction:** Utilizes the `zerokdb.api` to interact with the Aptos contract, updating the data sequences from the contract to match what was saved on IPFS.
- **Proof Generation:** Generates cryptographic proofs for executed queries and submits them back to the Hub for verification.

#### zerokdb

The **zerokdb** library serves as the interface for workers to interact with the `zerokdb.api`. It provides essential functionalities for retrieving data sequences from the decentralized database and managing interactions with the Aptos contract.

**Key Features:**

- **Sequence Retrieval:** Fetches all data sequences from the database contract on the Aptos blockchain.
- **API Integration:** Facilitates seamless communication with the `zerokdb.api` for updating the sequences on the contract according to what was updated by the worker.

#### zerokdb.api

The **zerokdb.api** acts as an intermediary between the workers and the Aptos blockchain. It provides a set of APIs that allow workers to execute queries, manage data storage on IPFS, and interact with the Aptos contract controlling the decentralized database.

**Key Features:**

- **Blockchain Interaction:** Interfaces with the Aptos contract to manage and retrieve decentralized data.
- **Proof Handling:** Assists in generating and verifying cryptographic proofs to maintain data integrity.

## Interaction Flow

The ZeroKDB Platform operates through a coordinated interaction between its components, ensuring efficient query processing and data management. Below is a high-level overview of the interaction flow:

1. **Worker Registration:**

   - Workers initiate registration with the Hub to join the network.
   - The Hub maintains a registry of active workers available to process queries.

2. **Query Submission:**

   - Users submit queries through the frontend interface.
   - The Hub receives these queries and determines the appropriate worker to handle each request based on availability and workload.

3. **Query Execution:**

   - The selected worker receives the query from the Hub.
   - Using the `zerokdb` library, the worker executes the query locally.
   - Query results are stored on IPFS to ensure decentralized storage.

4. **Proof Generation:**

   - After executing the query, the worker generates a cryptographic proof of the result's integrity.
   - The proof, along with the query results, is sent back to the Hub for verification.

5. **Response Verification:**

   - The Hub verifies the cryptographic proof to ensure the accuracy and integrity of the query results.
   - Upon successful verification, the Hub returns the results to the frontend for the user.

6. **Payment Allocation:**
   - Once the proof is verified, the Hub credits the worker with the appropriate amount of credits.
   - Credits are deducted from the user's locked credits, ensuring a fair payment mechanism.
  
# Getting Started

## Interact with ZeroKDB

1. Visit https://db.0k.wtf
2. Click on DB Interactions in the menu
3. Use the provided interface to use the database.

## Example Queries

### Create a table

```
CREATE TABLE crunchy (
  id int,
  name string
);
```

### Insert some data

```
INSERT INTO crunchy (id, name) VALUES (1, 'China Star-crusted Pigeon')
```

### Select some data

```
SELECT * FROM users LIMIT 10
```
