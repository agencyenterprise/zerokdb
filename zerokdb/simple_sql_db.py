import re
import datetime
import numpy as np
from zerokdb.change_tracker import ChangeTracker
from typing import Optional, Union
from zerokdb.file_storage import FileStorage
from zerokdb.ipfs_storage import IPFSStorage
from zerokdb.enhanced_file_storage import EnhancedFileStorage


class SimpleSQLDatabase:
    def __init__(
        self,
        storage: EnhancedFileStorage,
        change_tracker: Optional[ChangeTracker] = None,
    ):
        self.storage = storage
        self.change_tracker = change_tracker
        self.tables = self.storage.load() or {}

    def execute(self, query: str):
        query = query.strip()
        if self.change_tracker:
            self.change_tracker.log_change(query, self.tables)
        if query.startswith("CREATE TABLE"):
            table_name = self._create_table(query)
            self.storage.create_table(table_name)
            self.storage.save(self.tables, table_name)
        elif query.startswith("INSERT INTO"):
            table_name = self._insert_into(query)
            self.storage.save(self.tables, table_name)
        elif query.startswith("SELECT"):
            result = self._select(query)
            self.storage.save(self.tables)
            return result

        elif query.startswith("CREATE INDEX"):
            self._create_index(query)
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

    def _insert_into(self, query: str):
        match = re.match(
            r"INSERT INTO (\w+) \((.+)\) VALUES \((.+)\)", query, re.DOTALL
        )
        if not match:
            raise ValueError("Invalid INSERT INTO syntax")
        table_name, columns, values = match.groups()
        columns = [col.strip() for col in columns.split(",")]
        values = [
            val.strip()
            for val in re.split(r",(?=(?:[^\[\]]*\[[^\[\]]*\])*[^\[\]]*$)", values)
        ]
        if table_name not in self.tables:
            raise ValueError(f"Table {table_name} does not exist")
        table = self.tables[table_name]
        if columns != table["columns"]:
            raise ValueError("Column names do not match")
        # Validate and convert values based on column types
        converted_values = []
        for col, val in zip(columns, values):
            col_type = table["column_types"][col]
            if col_type == "int":
                converted_values.append(int(val))
            elif col_type == "float":
                converted_values.append(float(val))
            elif col_type == "bool":
                converted_values.append(val.lower() in ["true", "1"])
            elif col_type == "string":
                converted_values.append(val.strip("'"))
            elif col_type == "datetime":
                converted_values.append(datetime.datetime.fromisoformat(val))
            elif col_type == "list[float]":
                converted_values.append([float(x) for x in val.strip("[]").split(",")])
        table["rows"].append(converted_values)
        return table_name

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

    def _select(self, query):
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

        # Parse WHERE clause if present
        where_condition = None
        if where_clause:
            where_column = where_clause.split("=")[0].strip()
            if table["column_types"][where_column] == "int":
                where_match = re.match(r"(\w+) = (\d+)", where_clause)
            else:
                where_match = re.match(r"(\w+) = '(.+)'", where_clause)
            if not where_match:
                raise ValueError("Invalid WHERE syntax")
            where_column, where_value = where_match.groups()
            if where_column not in table["columns"]:
                raise ValueError(
                    f"Column {where_column} does not exist in table {table_name}"
                )
            where_condition = (where_column, where_value)

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
