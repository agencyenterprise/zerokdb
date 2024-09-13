# ZeroKDB

ZeroKDB is a lightweight, file-based database system with support for basic SQL operations and vector similarity search. It is designed to be simple and easy to use, making it ideal for small projects or educational purposes.

## Features

- Create, insert, and query tables using SQL-like syntax.
- Support for various data types including strings, integers, floats, booleans, datetimes, and lists of floats.
- Perform cosine similarity searches on vector data.
- File-based storage with optional IPFS support for distributed storage.
- Change tracking for database operations.

## Installation

To install the necessary dependencies using Poetry, use the following command:

```bash
poetry install
```

## Usage

### Creating a Table

To create a table, use the `CREATE TABLE` command:

```sql
CREATE TABLE users (id int, name string)
```

### Inserting Data

To insert data into a table, use the `INSERT INTO` command:

```sql
INSERT INTO users (id, name) VALUES (1, 'Alice')
```

### Querying Data

To query data from a table, use the `SELECT` command:

```sql
SELECT * FROM users
```

### Vector Similarity Search

To perform a cosine similarity search on vector data, use the `COSINE SIMILARITY` clause:

```sql
SELECT id FROM vectors COSINE SIMILARITY embedding WITH [0.1, 0.2, 0.3]
```

### Limiting Results

To limit the number of results returned, use the `LIMIT` clause:

```sql
SELECT * FROM users LIMIT 10
```

## Testing

To run the tests, use the following command:

```bash
pytest tests/
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.

## License

This project is licensed under the MIT License.
