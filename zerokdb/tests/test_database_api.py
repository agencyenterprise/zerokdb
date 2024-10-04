import pytest
from zerokdb.api import DatabaseAPI
from zerokdb.simple_sql_db import SimpleSQLDatabase
from zerok.verifier.verifier import ZkVerifier
from zerokdb.enhanced_file_storage import EnhancedFileStorage
import time
import os


@pytest.fixture
def db_api_file():
    # remove test_db.json file if it exists
    try:
        os.remove("test_db.json")
    except FileNotFoundError:
        pass
    return DatabaseAPI(storage_type="file", storage_location="test_db.json")


@pytest.fixture
def db_api_ipfs():
    return DatabaseAPI(storage_type="ipfs", pinata_api_key='test', api_host='http://localhost:8001')


def test_create_table(db_api_file: DatabaseAPI):
    table_name = "users"
    db_api_file.create_table(table_name, {"id": "int", "name": "string"})
    result = db_api_file.execute_query(f"SELECT * FROM {table_name}")
    assert result == []


def test_create_table_ipfs(db_api_ipfs: DatabaseAPI):
    table_name = f"users{int(time.time())}"
    db_api_ipfs.create_table(table_name, {"id": "int", "name": "string"})
    result = db_api_ipfs.execute_query(f"SELECT * FROM {table_name}")
    assert result == []


def test_insert_into(db_api_file: DatabaseAPI):
    table_name = "users"
    db_api_file.create_table(table_name, {"id": "int", "name": "string"})
    db_api_file.insert_into(table_name, {"id": 1, "name": "Alice"})
    result = db_api_file.execute_query(f"SELECT * FROM {table_name}")
    assert result == [[1, "Alice"]]


def test_insert_into_ipfs(db_api_ipfs: DatabaseAPI):
    table_name = f"users{int(time.time())}"
    db_api_ipfs.create_table(table_name, {"id": "int", "name": "string"})
    db_api_ipfs.insert_into(table_name, {"id": 1, "name": "Alice"})
    result = db_api_ipfs.execute_query(f"SELECT * FROM {table_name}")
    assert result == [[1, "Alice"]]


def test_execute_query(db_api_file: DatabaseAPI):
    db_api_file.create_table("users", {"id": "int", "name": "string"})
    db_api_file.insert_into("users", {"id": 1, "name": "Alice"})
    result = db_api_file.execute_query("SELECT name FROM users WHERE id = 1")
    assert result == [["Alice"]]


def test_execute_query_with_proof(db_api_file: DatabaseAPI):
    db_api_file.create_table("users", {"id": "int", "name": "string"})
    db_api_file.insert_into("users", {"id": 1, "name": "Alice"})
    result, circuit, proof = db_api_file.execute_query(
        "SELECT name FROM users WHERE id = 1", proof=True
    )
    assert result == [["Alice"]]
    verifier = ZkVerifier(circuit)
    assert verifier.run_verifier(proof)


def test_execute_query_ifps(db_api_ipfs: DatabaseAPI):
    table_name = f"users{int(time.time())}"
    db_api_ipfs.create_table(table_name, {"id": "int", "name": "string"})
    db_api_ipfs.insert_into(table_name, {"id": 1, "name": "Alice"})
    result = db_api_ipfs.execute_query(f"SELECT name FROM {table_name} WHERE id = 1")
    assert result == [["Alice"]]


def test_convert_text_to_embedding(db_api_file: DatabaseAPI):
    text = "Hello world"
    embedding = db_api_file.convert_text_to_embedding(text)
    assert isinstance(embedding, list)
    assert len(embedding) > 0


def test_sql_embedding_search_ipfs():
    storage = EnhancedFileStorage("embeddings_test_db", api_host="http://localhost:8001", pinata_api_key="test")
    db = SimpleSQLDatabase(storage)
    table_name = f"vectors{int(time.time())}"
    # Create a table with a vector column
    db.execute(f"CREATE TABLE {table_name} (id int, embedding list[float])")

    # Insert some data
    db.execute(
        f"INSERT INTO {table_name} (id, embedding) VALUES (1, [0.1, 0.2, 0.3]), (2, [0.4, 0.5, 0.6]), (3, [0.7, 0.8, 0.9])"
    )

    # Perform a cosine similarity search
    target_vector = [0.1, 0.2, 0.35]
    result = db.execute(
        f"SELECT id FROM {table_name} LIMIT 1 COSINE SIMILARITY embedding WITH {target_vector}"
    )

    # Check if the result is as expected
    assert result == [[1, [0.1, 0.2, 0.3]]], f"Expected [[1]], but got {result}"


def test_sql_embedding_search_ipfs_with_text():
    db = DatabaseAPI(storage_type="ipfs", pinata_api_key='test', api_host='http://localhost:8001')
    table_name = f"vectors{int(time.time())}"
    # Create a table with a vector column
    db.execute_query(
        f"CREATE TABLE {table_name} (id int, embedding list[float], text string)"
    )
    initial_text = "Good morning, its a beautiful day today!"
    initial_text_vector = db.convert_text_to_embedding(initial_text)
    # Insert some data
    db.execute_query(
        f"INSERT INTO {table_name} (id, embedding, text) VALUES (1, {initial_text_vector}, '{initial_text}')"
    )

    # Perform a cosine similarity search
    target_text = "Is today a beautiful day?"
    target_vector = db.convert_text_to_embedding(target_text)
    result, circuit, proof = db.execute_query(
        f"SELECT * FROM {table_name} LIMIT 1 COSINE SIMILARITY embedding WITH {target_vector}",
        proof=True,
    )
    assert result == [
        [1, initial_text_vector, "Good morning,its a beautiful day today!"]
    ], f"Expected [[1]], but got {result}"
    verifier = ZkVerifier(circuit)
    assert verifier.run_verifier(proof), "Proof verification failed"
