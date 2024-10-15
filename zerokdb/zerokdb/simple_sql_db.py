import re
import sqlite3
import time
from typing import Optional, Union

import numpy as np

from zerokdb.change_tracker import ChangeTracker
from zerokdb.enhanced_file_storage import EnhancedFileStorage
from zerokdb.file_storage import FileStorage
from zerokdb.zk.table_parser import generate_proof_of_membership


class SimpleSQLDatabase:
    selected_columns = []

    def __init__(
        self,
        storage: Union[EnhancedFileStorage, FileStorage],
        change_tracker: Optional[ChangeTracker] = None,
    ):
        self.storage = storage
        self.change_tracker = change_tracker
        self.conn = sqlite3.connect(":memory:")
        self.cursor = self.conn.cursor()

    def _load_data_from_storage(self, table_name: str):
        data = self.storage.load(table_name)

        if not data or table_name not in data:
            return

        table_data = data[table_name]
        columns = ", ".join(
            [f"{col} {dtype}" for col, dtype in table_data["column_types"].items()]
        )
        self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({columns})")

        if table_data["rows"]:
            placeholders = ", ".join(["?" for _ in table_data["columns"]])
            self.cursor.execute(f"DELETE FROM {table_name}")
            self.cursor.executemany(
                f"INSERT INTO {table_name} VALUES ({placeholders})", table_data["rows"]
            )

        self.conn.commit()

    def execute(
        self,
        query: str,
        generate_proof: bool = False,
    ):
        query = query.strip()

        table_name = self._extract_table_name(query)
        self._load_data_from_storage(table_name)

        if self.change_tracker:
            self.change_tracker.log_change(query, self._get_tables_data())

        if query.startswith("CREATE TABLE"):
            table_name = self._create_table(query)
            self.storage.create_table(table_name, self._get_tables_data())
            rows = self._get_table_rows(table_name)
            circuit, proof = generate_proof_of_membership(
                self._get_table_data(table_name), [], []
            )
            if generate_proof:
                return rows, circuit, proof
            return rows

        elif query.startswith("INSERT INTO"):
            start = time.time()
            table_name = self._extract_table_name(query)
            self.cursor.execute(query)
            self.conn.commit()
            print(f"Inserted data locally in {time.time() - start} seconds")

            new_table_chunk = {table_name: self._get_table_data(table_name)}
            self.storage.save(new_table_chunk, table_name)

            print(f"Saved updated data on IPFS in {time.time() - start} seconds")
            rows = self._get_table_rows(table_name)
            circuit, proof = generate_proof_of_membership(
                self._get_table_data(table_name), new_table_chunk[table_name], []
            )
            if generate_proof:
                return rows, circuit, proof
            return rows

        elif query.startswith("SELECT"):
            if "COSINE SIMILARITY" in query.upper():
                return self._handle_cosine_similarity_query(query, generate_proof)
            else:
                self.cursor.execute(query)
                result = self.cursor.fetchall()
                table_name = self._extract_table_name(query)
                query_columns = self._get_query_columns(query)
                circuit, proof = generate_proof_of_membership(
                    self._get_table_data(table_name), {"rows": result}, query_columns
                )
                if generate_proof:
                    return result, circuit, proof
                return result

        else:
            raise ValueError("Unsupported SQL command")

    def _create_table(self, query: str):
        self.cursor.execute(query)
        self.conn.commit()
        return self._extract_table_name(query)

    def _extract_table_name(self, query: str):
        match = re.search(
            r"(?:CREATE TABLE|INSERT INTO|FROM)\s+(\w+)", query, re.IGNORECASE
        )
        if match:
            return match.group(1)
        raise ValueError("Could not extract table name from query")

    def _get_tables_data(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = self.cursor.fetchall()
        return {table[0]: self._get_table_data(table[0]) for table in tables}

    def _get_table_data(self, table_name: str):
        self.cursor.execute(f"PRAGMA table_info({table_name})")
        columns_info = self.cursor.fetchall()
        columns = [col[1] for col in columns_info]
        column_types = {col[1]: col[2] for col in columns_info}
        rows = self._get_table_rows(table_name)
        return {
            "columns": columns,
            "column_types": column_types,
            "rows": rows,
            "indexes": {},
        }

    def _get_table_rows(self, table_name: str):
        self.cursor.execute(f"SELECT * FROM {table_name}")
        return self.cursor.fetchall()

    def _get_query_columns(self, query: str):
        match = re.match(r"SELECT\s+(.+?)\s+FROM", query, re.IGNORECASE)
        if match:
            columns = match.group(1).split(",")
            return [col.strip() for col in columns]
        return []

    def _handle_cosine_similarity_query(self, query: str, generate_proof: bool):
        match = re.match(
            r"SELECT (.+) FROM (\w+)(?: WHERE (.+))?(?: LIMIT (\d+))? COSINE SIMILARITY (.+) WITH (.+)$",
            query,
            re.IGNORECASE,
        )
        if not match:
            raise ValueError("Invalid COSINE SIMILARITY query syntax")

        columns, table_name, where_clause, limit, vector_column, target_vector = (
            match.groups()
        )
        target_vector = np.fromstring(target_vector.strip("[]"), sep=",")

        # Fetch all rows
        where_sql = f"WHERE {where_clause}" if where_clause else ""
        self.cursor.execute(
            f"SELECT {columns}, {vector_column} FROM {table_name} {where_sql}"
        )
        rows = self.cursor.fetchall()

        # Calculate cosine similarities
        similarities = []
        for row in rows:
            vector = np.fromstring(row[-1].strip("[]"), sep=",")
            similarity = np.dot(vector, target_vector) / (
                np.linalg.norm(vector) * np.linalg.norm(target_vector)
            )
            similarities.append((row[:-1], similarity))

        # Sort by similarity and apply limit
        similarities.sort(key=lambda x: x[1], reverse=True)
        if limit:
            similarities = similarities[: int(limit)]

        result = [row for row, _ in similarities]

        if generate_proof:
            circuit, proof = generate_proof_of_membership(False, False, [])
            return result, circuit, proof
        return result

    def __del__(self):
        if hasattr(self, "conn"):
            self.conn.close()
