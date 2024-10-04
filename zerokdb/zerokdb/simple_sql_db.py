import re
import datetime
import numpy as np
from zerokdb.change_tracker import ChangeTracker
from typing import Optional, Union
from zerokdb.file_storage import FileStorage
from zerokdb.enhanced_file_storage import EnhancedFileStorage
import time
from zerokdb.zk.table_parser import generate_proof_of_membership


class SimpleSQLDatabase:
    selected_columns = []

    def __init__(
        self,
        storage: Union[EnhancedFileStorage, FileStorage],
        change_tracker: Optional[ChangeTracker] = None,
        cid: Optional[str] = "0x0",
        sequence_cid: Optional[str] = "0x0",
        table_id: Optional[str] = None,
        entityid: Optional[str] = None,
    ):
        self.cid = cid
        self.sequence_cid = sequence_cid
        self.entityid = entityid
        self.storage = storage
        self.change_tracker = change_tracker
        self.tables = self.storage.load(cid) if cid else {}

    def execute(
        self,
        query: str,
        cid: Optional[str] = None,
        sequence_cid: Optional[str] = None,
        generate_proof: bool = False,
    ):
        query = query.strip()
        self.cid = cid or self.cid
        self.sequence_cid = sequence_cid or self.sequence_cid
        if self.change_tracker:
            self.change_tracker.log_change(query, self.tables)
        if query.startswith("CREATE TABLE"):
            table_name = self._create_table(query)
            storage_data = self.storage.create_table(table_name, self.tables)
            self.cid = storage_data.get("data_cid", None)
            self.sequence_cid = storage_data.get("sequence_cid", None)
            rows = self.tables[table_name]["rows"]
            circuit, proof = generate_proof_of_membership(
                self.tables[table_name], [], []
            )
            if generate_proof:
                return rows, circuit, proof
            return rows

        elif query.startswith("INSERT INTO"):
            start = time.time()
            table_name, _, _ = self._process_insert_into(query)
            self.tables = self.storage.load(table_name) or {}

            new_table_chunk = self._insert_into(query)
            print(f"Inserted data locally in {time.time() - start} seconds")
            storage_data = self.storage.save(new_table_chunk, table_name)

            print(f"Saved updated data on IPFS in {time.time() - start} seconds")
            self.cid = storage_data.get("data_cid", None)
            self.sequence_cid = storage_data.get("sequence_cid", None)
            rows = new_table_chunk[table_name]["rows"]
            circuit, proof = generate_proof_of_membership(
                self.tables[table_name], new_table_chunk[table_name], []
            )
            if generate_proof:
                return rows, circuit, proof
            return rows
        elif query.startswith("SELECT"):
            table_name = self.parse_select_query(query)[1]
            self.tables = self.storage.load(table_name) or {}
            result = self._select(query)
            query_columns = self.selected_columns if self.selected_columns else []
            circuit, proof = generate_proof_of_membership(
                self.tables[table_name], {"rows": result}, query_columns
            )
            if generate_proof:
                return result, circuit, proof
            return result
        else:
            raise ValueError("Unsupported SQL command")

    def _create_table(self, query: str):
        match = re.match(r"CREATE TABLE (\w+) \((.+)\)", query)
        if not match:
            raise ValueError("Invalid CREATE TABLE syntax")
        table_name, columns = match.groups()
        columns = [col.strip() for col in columns.split(",")]
        column_defs = {}
        for col in columns:
            col_name, col_type = col.split()
            if col_type not in [
                "string",
                "int",
                "float",
                "bool",
                "datetime",
                "list[float]",
            ]:
                raise ValueError(f"Unsupported data type {col_type}")
            column_defs[col_name] = col_type
        self.tables[table_name] = {
            "columns": list(column_defs.keys()),
            "column_types": column_defs,
            "rows": [],
            "indexes": {},
        }
        return table_name

    def _process_insert_into(self, query: str):
        match = re.match(r"INSERT INTO (\w+) \((.+)\) VALUES (.+)", query, re.DOTALL)
        if not match:
            raise ValueError("Invalid INSERT INTO syntax")
        table_name, columns, values = match.groups()
        return table_name, columns, values

    def _insert_into(self, query: str):
        table_name, columns, values = self._process_insert_into(query)
        columns = [col.strip() for col in columns.split(",")]
        values_list = re.findall(r"\((.*?)\)", values, re.DOTALL)
        if table_name not in self.tables:
            raise ValueError(f"Table {table_name} does not exist")
        new_table_chunk = self.tables.copy()
        new_table_chunk[table_name]["rows"] = []
        if columns != new_table_chunk[table_name]["columns"]:
            raise ValueError("Column names do not match")
        for values in values_list:
            values = [
                val.strip()
                for val in re.split(r",(?=(?:[^\[\]]*\[[^\[\]]*\])*[^\[\]]*$)", values)
            ]
            # Validate and convert values based on column types
            converted_values = []
            for col_idx, (col, val) in enumerate(zip(columns, values)):
                col_type = new_table_chunk[table_name]["column_types"].get(col, None)
                if not col_type:
                    raise ValueError(
                        f"Column {col} does not exist in table {table_name}"
                    )
                if col_type == "int":
                    converted_values.append(int(val))
                elif col_type == "float":
                    converted_values.append(float(val))
                elif col_type == "bool":
                    converted_values.append(val.lower() in ["true", "1"])
                elif col_type == "string":
                    if col == columns[-1]:
                        if len(values) > len(columns):
                            val = ",".join(values[col_idx:])
                    converted_values.append(val.strip("'"))
                elif col_type == "datetime":
                    converted_values.append(datetime.datetime.fromisoformat(val))
                elif col_type == "list[float]":
                    converted_values.append(
                        [float(x) for x in val.strip("[]").split(",")]
                    )
            new_table_chunk[table_name]["rows"].append(converted_values)
        return new_table_chunk

    def _create_index(self, query: str):
        match = re.match(r"CREATE INDEX (\w+) ON (\w+) \((.+)\)", query)
        if not match:
            raise ValueError("Invalid CREATE INDEX syntax")
        index_name, table_name, column = match.groups()
        column = column.strip()
        if table_name not in self.tables:
            raise ValueError(f"Table {table_name} does not exist")
        table = self.tables[table_name]
        if column not in table["columns"]:
            raise ValueError(f"Column {column} does not exist in table {table_name}")
        index = {}
        column_index = table["columns"].index(column)
        for row in table["rows"]:
            key = row[column_index]
            if key not in index:
                index[key] = []
            index[key].append(row)
        table["indexes"][index_name] = index

    def parse_select_query(self, query):
        match = re.match(
            r"SELECT (.+) FROM (\w+)(?: WHERE (.+))?(?: GROUP BY (.+))?(?: ORDER BY (.+))?(?: LIMIT (\d+))?(?: COSINE SIMILARITY (.+))?$",
            query,
        )
        if not match:
            raise ValueError("Invalid SELECT syntax")
        (
            columns,
            table_name,
            where_clause,
            group_by_clause,
            order_by_clause,
            limit_clause,
            cosine_similarity_clause,
        ) = match.groups()
        return (
            columns,
            table_name,
            where_clause,
            group_by_clause,
            order_by_clause,
            limit_clause,
            cosine_similarity_clause,
        )

    def _select(self, query):
        (
            columns,
            table_name,
            where_clause,
            group_by_clause,
            order_by_clause,
            limit_clause,
            cosine_similarity_clause,
        ) = self.parse_select_query(query)
        columns = [col.strip() for col in columns.split(",")]
        if table_name not in self.tables:
            raise ValueError(f"Table {table_name} does not exist")
        table = self.tables[table_name]
        if columns == ["*"]:
            columns = table["columns"]
        column_indices = [table["columns"].index(col) for col in columns]
        if cosine_similarity_clause:
            vector_column, _ = cosine_similarity_clause.split(" WITH ")
            if vector_column not in columns:
                columns.append(vector_column)
                column_indices.append(table["columns"].index(vector_column))
        self.selected_columns = columns
        # Parse WHERE clause if present
        where_condition = None
        if where_clause:
            where_column = where_clause.split("=")[0].strip()
            if table["column_types"][where_column] == "int":
                where_match = re.match(r"(\w+) = (\d+)", where_clause)
            else:
                where_match = re.match(r"(\w+) = '(.+)'", where_clause)
            if not where_match:
                raise ValueError(
                    "Invalid WHERE syntax: Only equality assertions are supported"
                )
            where_column, where_value = where_match.groups()
            if where_column not in table["columns"]:
                raise ValueError(
                    f"Column {where_column} does not exist in table {table_name}"
                )
            where_condition = (where_column, where_value)
        self.where_condition = where_condition
        column_indices = [table["columns"].index(col) for col in columns]
        result = []

        # Check if we can use an index
        if len(columns) == 1 and columns[0] in table["indexes"]:
            index = table["indexes"][columns[0]]
            for key in index:
                for row in index[key]:
                    result.append([row[i] for i in column_indices])
            return result
        for row in table["rows"]:
            if where_condition:
                where_column, where_value = where_condition
                where_index = table["columns"].index(where_column)
                if table["column_types"][where_column] == "int":
                    where_value = int(where_value)
                if row[where_index] != where_value:
                    continue
            result.append([row[i] for i in column_indices])
        # Group results if GROUP BY clause is present
        if group_by_clause:
            group_by_column = group_by_clause.strip()
            if group_by_column not in table["columns"]:
                raise ValueError(
                    f"Column {group_by_column} does not exist in table {table_name}"
                )
            group_by_index = table["columns"].index(group_by_column)
            grouped_result = {}
            for row in result:
                key = row[group_by_index]
                if key not in grouped_result:
                    grouped_result[key] = []
                grouped_result[key].append(row)
            result = [group for group in grouped_result.values()]

        # Sort results if ORDER BY clause is present
        if order_by_clause:
            order_by_column = order_by_clause.strip()
            if order_by_column not in table["columns"]:
                raise ValueError(
                    f"Column {order_by_column} does not exist in table {table_name}"
                )
            order_by_index = table["columns"].index(order_by_column)
            result.sort(key=lambda row: row[order_by_index])

        # Perform cosine similarity if COSINE SIMILARITY clause is present
        if cosine_similarity_clause:
            vector_column, target_vector = cosine_similarity_clause.split(" WITH ")
            target_vector = np.fromstring(target_vector.strip("[]"), sep=",")
            if vector_column not in table["columns"]:
                raise ValueError(
                    f"Column {vector_column} does not exist in table {table_name}"
                )
            vector_index = table["columns"].index(vector_column)
            vector_index = table["columns"].index(vector_column)
            similarities = [
                (
                    row,
                    np.dot(row[vector_index], target_vector)
                    / (
                        np.linalg.norm(row[vector_index])
                        * np.linalg.norm(target_vector)
                    ),
                )
                for row in result
            ]
            similarities.sort(key=lambda x: x[1], reverse=True)
            for row, similarity in similarities:
                print(f"Row: {row}, Similarity: {similarity}")
            result = [row for row, _ in similarities]
        if limit_clause:
            result = result[: int(limit_clause)]

        return result
