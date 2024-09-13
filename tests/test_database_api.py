import pytest
from zerokdb.api import DatabaseAPI


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
