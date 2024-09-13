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
        else:
            raise ValueError("Unsupported SQL command")

    def _create_table(self, query):
        match = re.match(r"CREATE TABLE (\w+) \((.+)\)", query)
        if not match:
            raise ValueError("Invalid CREATE TABLE syntax")
        table_name, columns = match.groups()
        columns = [col.strip() for col in columns.split(",")]
        self.tables[table_name] = {"columns": columns, "rows": []}

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

    def _select(self, query):
        match = re.match(r"SELECT (.+) FROM (\w+)", query)
        if not match:
            raise ValueError("Invalid SELECT syntax")
        columns, table_name = match.groups()
        columns = [col.strip() for col in columns.split(",")]
        if table_name not in self.tables:
            raise ValueError(f"Table {table_name} does not exist")
        table = self.tables[table_name]
        if columns == ["*"]:
            columns = table["columns"]
        column_indices = [table["columns"].index(col) for col in columns]
        result = []
        for row in table["rows"]:
            result.append([row[i] for i in column_indices])
        return result
