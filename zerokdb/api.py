from zerokdb.change_tracker import ChangeTracker
from zerokdb.simple_sql_db import SimpleSQLDatabase
from zerokdb.file_storage import FileStorage
from zerokdb.enhanced_file_storage import EnhancedFileStorage
from zerokdb.text_to_embedding import TextToEmbedding
from typing import Optional, List


class DatabaseAPI:
    def __init__(
        self,
        storage_type="file",
        storage_location="database.json",
        database_name="database",
        api_host="http://localhost:8001",
        pinata_api_key="test",
    ):
        if storage_type == "file":
            self.storage = FileStorage(storage_location)
        elif storage_type == "ipfs":
            self.storage = EnhancedFileStorage(database_name, api_host=api_host, pinata_api_key=pinata_api_key)
        else:
            raise ValueError("Unsupported storage type")
        self.change_tracker = ChangeTracker()
        self.db = SimpleSQLDatabase(self.storage, self.change_tracker)
        self.text_to_embedding = TextToEmbedding()

    def create_table(
        self,
        table_name,
        columns,
        cid: Optional[str] = None,
        sequence_cid: Optional[str] = None,
        proof: bool = False,
    ):
        """Create a new table."""
        columns_str = ", ".join([f"{name} {dtype}" for name, dtype in columns.items()])
        query = f"CREATE TABLE {table_name} ({columns_str})"
        self.db.execute(query, cid=cid, sequence_cid=sequence_cid, generate_proof=proof)

    def insert_into(
        self,
        table_name,
        data,
        cid: Optional[str] = None,
        sequence_cid: Optional[str] = None,
    ):
        """Insert data into a table."""
        columns_str = ", ".join(data.keys())
        values_str = ", ".join(
            [f"'{v}'" if isinstance(v, str) else str(v) for v in data.values()]
        )
        query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({values_str})"
        self.db.execute(query, cid=cid, sequence_cid=sequence_cid)

    def execute_query(
        self,
        query,
        cid: Optional[str] = None,
        sequence_cid: Optional[str] = None,
        proof: bool = False,
    ):
        """Execute a SQL query."""
        return self.db.execute(
            query, cid=cid, sequence_cid=sequence_cid, generate_proof=proof
        )

    def convert_text_to_embedding(self, text) -> List[float]:
        """Convert text to embedding."""
        return self.text_to_embedding.convert(text)
