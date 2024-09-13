import pytest
from zerokdb.api import DatabaseAPI
from zerokdb.simple_sql_db import SimpleSQLDatabase
from zerokdb.file_storage import FileStorage


@pytest.fixture
def db_api_file():
    return DatabaseAPI(storage_type="file", storage_location="test_db.json")


def test_create_table(db_api_file: DatabaseAPI):
    db_api_file.create_table("users", {"id": "int", "name": "string"})
    result = db_api_file.execute_query("SELECT * FROM users")
    assert result == []


def test_insert_into(db_api_file: DatabaseAPI):
    db_api_file.create_table("users", {"id": "int", "name": "string"})
    db_api_file.insert_into("users", {"id": 1, "name": "Alice"})
    result = db_api_file.execute_query("SELECT * FROM users")
    assert result == [[1, "Alice"]]


def test_execute_query(db_api_file: DatabaseAPI):
    db_api_file.create_table("users", {"id": "int", "name": "string"})
    db_api_file.insert_into("users", {"id": 1, "name": "Alice"})
    result = db_api_file.execute_query("SELECT name FROM users WHERE id = 1")
    assert result == [["Alice"]]


def test_convert_text_to_embedding(db_api_file: DatabaseAPI):
    text = "Hello world"
    embedding = db_api_file.convert_text_to_embedding(text)
    assert isinstance(embedding, list)
    assert len(embedding) > 0


def test_sql_embedding_search():
    storage = FileStorage("embeddings_test_db.json")
    db = SimpleSQLDatabase(storage)

    # Create a table with a vector column
    db.execute("CREATE TABLE vectors (id int, embedding list[float])")

    # Insert some data
    db.execute("INSERT INTO vectors (id, embedding) VALUES (1, [0.1, 0.2, 0.3])")
    db.execute("INSERT INTO vectors (id, embedding) VALUES (2, [0.4, 0.5, 0.6])")
    db.execute("INSERT INTO vectors (id, embedding) VALUES (3, [0.7, 0.8, 0.9])")

    # Perform a cosine similarity search
    target_vector = [0.1, 0.2, 0.35]
    result = db.execute(
        f"SELECT id FROM vectors LIMIT 1 COSINE SIMILARITY embedding WITH {target_vector}"
    )

    # Check if the result is as expected
    assert result == [[1, [0.1, 0.2, 0.3]]], f"Expected [[1]], but got {result}"
