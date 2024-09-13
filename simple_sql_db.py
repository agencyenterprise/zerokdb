import re

class SimpleSQLDatabase:
    def __init__(self):
        self.tables = {}

    def execute(self, query):
        query = query.strip()
        if query.startswith("CREATE TABLE"):
            self._create_table(query)
        elif query.startswith("INSERT INTO"):
            self._insert_into(query)
        elif query.startswith("SELECT"):
            return self._select(query)
        elif query.startswith("CREATE INDEX"):
            self._create_index(query)
            raise ValueError("Unsupported SQL command")

    def _create_table(self, query):
        match = re.match(r"CREATE TABLE (\w+) \((.+)\)", query)
        if not match:
            raise ValueError("Invalid CREATE TABLE syntax")
        table_name, columns = match.groups()
        columns = [col.strip() for col in columns.split(",")]
        self.tables[table_name] = {"columns": columns, "rows": [], "indexes": {}}

    def _insert_into(self, query):
        match = re.match(r"INSERT INTO (\w+) \((.+)\) VALUES \((.+)\)", query)
        if not match:
            raise ValueError("Invalid INSERT INTO syntax")
        table_name, columns, values = match.groups()
        columns = [col.strip() for col in columns.split(",")]
        values = [val.strip().strip("'") for val in values.split(",")]
        if table_name not in self.tables:
            raise ValueError(f"Table {table_name} does not exist")
        table = self.tables[table_name]
        if columns != table["columns"]:
            raise ValueError("Column names do not match")
        table["rows"].append(values)

    def _create_index(self, query):
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
        match = re.match(r"SELECT (.+) FROM (\w+)(?: WHERE (.+))?", query)
        if not match:
            raise ValueError("Invalid SELECT syntax")
        columns, table_name, where_clause = match.groups()
        columns = [col.strip() for col in columns.split(",")]
        if table_name not in self.tables:
            raise ValueError(f"Table {table_name} does not exist")
        table = self.tables[table_name]
        column_indices = [table["columns"].index(col) for col in columns]

        # Parse WHERE clause if present
        where_condition = None
        if where_clause:
            where_match = re.match(r"(\w+) = '(.+)'", where_clause)
            if not where_match:
                raise ValueError("Invalid WHERE syntax")
            where_column, where_value = where_match.groups()
            if where_column not in table["columns"]:
                raise ValueError(f"Column {where_column} does not exist in table {table_name}")
            where_condition = (where_column, where_value)
        if columns == ["*"]:
            columns = table["columns"]
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
                if row[where_index] != where_value:
                    continue
            result.append([row[i] for i in column_indices])
        return result
