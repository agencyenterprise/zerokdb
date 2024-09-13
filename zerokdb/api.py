from zerokdb.change_tracker import ChangeTracker
from zerokdb.simple_sql_db import SimpleSQLDatabase
from zerokdb.file_storage import FileStorage
from zerokdb.ipfs_storage import IPFSStorage
from zerokdb.text_to_embedding import TextToEmbedding


class DatabaseAPI:
    def __init__(self, storage_type="file", storage_location="database.json"):
        if storage_type == "file":
            self.storage = FileStorage(storage_location)
        elif storage_type == "ipfs":
            self.storage = IPFSStorage()
            raise ValueError("Unsupported storage type")
        self.change_tracker = ChangeTracker()
        self.db = SimpleSQLDatabase(self.storage, self.change_tracker)
        self.text_to_embedding = TextToEmbedding()

    def create_table(self, table_name, columns):
        """Create a new table."""
        columns_str = ", ".join([f"{name} {dtype}" for name, dtype in columns.items()])
        query = f"CREATE TABLE {table_name} ({columns_str})"
        self.db.execute(query)

    def insert_into(self, table_name, data):
        """Insert data into a table."""
        columns_str = ", ".join(data.keys())
        values_str = ", ".join(
            [f"'{v}'" if isinstance(v, str) else str(v) for v in data.values()]
        )
        query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({values_str})"
        self.db.execute(query)

    def execute_query(self, query):
        """Execute a SQL query."""
        return self.db.execute(query)

    def convert_text_to_embedding(self, text):
        """Convert text to embedding."""
        return self.text_to_embedding.convert(text)
