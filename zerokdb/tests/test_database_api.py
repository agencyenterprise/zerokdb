import os
import time
from zerok.verifier.verifier import ZkVerifier

from zerokdb.api import DatabaseAPI
from zerokdb.enhanced_file_storage import EnhancedFileStorage
from zerokdb.simple_sql_db import SimpleSQLDatabase


def create_db_api_file():
    # remove test_db.json file if it exists
    try:
        os.remove("test_db.json")
    except FileNotFoundError:
        pass

    db_api = DatabaseAPI(storage_type="file", storage_location="test_db.json", chain="aptos")

    # Delete all tables in SQLite
    cursor = db_api.db.conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for table in tables:
        cursor.execute(f"DROP TABLE IF EXISTS {table[0]};")
    db_api.db.conn.commit()

    return db_api


def create_db_api_ipfs():
    return DatabaseAPI(
        storage_type="ipfs", pinata_api_key="test", api_host="http://localhost:8001", chain="aptos"
    )


def test_create_table():
    db_api = create_db_api_file()
    table_name = "users"
    db_api.create_table(table_name, {"id": "INT", "name": "STRING"})
    db_api = create_db_api_file()
    result = db_api.execute_query(f"SELECT * FROM {table_name}")
    assert result == []


def test_create_table_ipfs():
    db_api = create_db_api_ipfs()
    table_name = f"users{int(time.time())}"
    db_api.create_table(table_name, {"id": "INT", "name": "STRING"})
    db_api = create_db_api_ipfs()
    result = db_api.execute_query(f"SELECT * FROM {table_name}")
    assert result == []


def test_insert_into():
    db_api = create_db_api_file()
    table_name = "users"
    db_api.create_table(table_name, {"id": "INT", "name": "STRING"})
    db_api = create_db_api_file()
    db_api.insert_into(table_name, {"id": 1, "name": "Alice"})
    db_api = create_db_api_file()
    result = db_api.execute_query(f"SELECT * FROM {table_name}")
    assert result == [(1, "Alice")]


def test_insert_into_ipfs():
    db_api = create_db_api_ipfs()
    table_name = f"users{int(time.time())}"
    db_api.create_table(table_name, {"id": "INT", "name": "STRING"})
    db_api = create_db_api_ipfs()
    db_api.insert_into(table_name, {"id": 1, "name": "Alice"})
    db_api = create_db_api_ipfs()
    result = db_api.execute_query(f"SELECT * FROM {table_name}")
    assert result == [(1, "Alice")]


def test_execute_query():
    db_api = create_db_api_file()
    db_api.create_table("users", {"id": "INT", "name": "STRING"})
    db_api = create_db_api_file()
    db_api.insert_into("users", {"id": 1, "name": "Alice"})
    db_api = create_db_api_file()
    result = db_api.execute_query("SELECT name FROM users WHERE id = 1")
    assert result == [("Alice",)]


def test_execute_query_with_proof():
    db_api = create_db_api_file()
    db_api.create_table("users", {"id": "int", "name": "STRING"})
    db_api = create_db_api_file()
    db_api.insert_into("users", {"id": 1, "name": "Alice"})
    db_api = create_db_api_file()
    result, circuit, proof = db_api.execute_query(
        "SELECT name FROM users WHERE id = 1", proof=True
    )
    assert result == [("Alice",)]
    verifier = ZkVerifier(circuit)
    assert verifier.run_verifier(proof)


def test_execute_query_ipfs_twice():
    db_api = create_db_api_ipfs()
    table_name = f"users{int(time.time())}"
    db_api.create_table(table_name, {"id": "INT", "name": "STRING"})
    db_api = create_db_api_ipfs()
    db_api.insert_into(table_name, {"id": 1, "name": "Alice"})

    db_api = create_db_api_ipfs()
    db_api.insert_into(table_name, {"id": 2, "name": "Bob"})

    db_api = create_db_api_ipfs()
    result = db_api.execute_query(f"SELECT name FROM {table_name} WHERE id = 1")
    assert result == [("Alice",)]

    db_api = create_db_api_ipfs()
    result = db_api.execute_query(f"SELECT name FROM {table_name} WHERE id = 2")
    assert result == [("Bob",)]

    db_api = create_db_api_ipfs()
    result = db_api.execute_query(f"SELECT name FROM {table_name}")
    assert result == [("Alice",), ("Bob",)]


def test_convert_text_to_embedding():
    db_api = create_db_api_file()
    text = "Hello world"
    embedding = db_api.convert_text_to_embedding(text)
    assert isinstance(embedding, list)
    assert len(embedding) > 0


def test_sql_embedding_search_ipfs():
    storage = EnhancedFileStorage(
        "embeddings_test_db",
        api_host="https://kumh6ogteddmj4pgtuh7p00k9c.ingress.akash-palmito.org",
        pinata_api_key="test",
        chain="aptos",
    )
    db = SimpleSQLDatabase(storage)
    table_name = f"vectors{int(time.time())}"
    # Create a table with a vector column
    db.execute(f"CREATE TABLE {table_name} (id INT, embedding TEXT)")

    # Insert some data
    db.execute(
        f"INSERT INTO {table_name} (id, embedding) VALUES (1, '[0.1, 0.2, 0.3]'), (2, '[0.4, 0.5, 0.6]'), (3, '[0.7, 0.8, 0.9]')"
    )

    # Perform a cosine similarity search
    target_vector = [0.1, 0.2, 0.35]
    result = db.execute(
        f"SELECT id, embedding FROM {table_name} LIMIT 1 COSINE SIMILARITY embedding WITH {target_vector}"
    )

    # Check if the result is as expected
    assert result == [
        (1, "[0.1, 0.2, 0.3]")
    ], f"Expected [(1, '[0.1, 0.2, 0.3]')], but got {result}"


def test_sql_embedding_search_ipfs_with_text():
    db_api = create_db_api_ipfs()
    table_name = f"vectors{int(time.time())}"
    # Create a table with a vector column
    db_api.execute_query(
        f"CREATE TABLE {table_name} (id INT, embedding text, text text)"
    )
    db_api = create_db_api_ipfs()
    initial_text = "Good morning, its a beautiful day today!"
    initial_text_vector = db_api.convert_text_to_embedding(initial_text)
    # Insert some data
    db_api.execute_query(
        f"INSERT INTO {table_name} (id, embedding, text) VALUES (1, '{initial_text_vector}', '{initial_text}')"
    )

    # Perform a cosine similarity search
    db_api = create_db_api_ipfs()
    target_text = "Is today a beautiful day?"
    target_vector = db_api.convert_text_to_embedding(target_text)
    result, circuit, proof = db_api.execute_query(
        f"SELECT * FROM {table_name} LIMIT 1 COSINE SIMILARITY embedding WITH {target_vector}",
        proof=True,
    )
    assert result == [
        (1, str(initial_text_vector), "Good morning, its a beautiful day today!")
    ], f"Expected [(1, str(initial_text_vector), 'Good morning, its a beautiful day today!')], but got {result}"
    verifier = ZkVerifier(circuit)
    assert verifier.run_verifier(proof), "Proof verification failed"
