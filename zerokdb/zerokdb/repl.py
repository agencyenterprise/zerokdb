import click
from zerokdb.simple_sql_db import SimpleSQLDatabase
from zerokdb.file_storage import FileStorage
from zerokdb.text_to_embedding import TextToEmbedding


@click.group()
def cli():
    pass


@cli.command()
@click.argument("query")
def execute(query):
    """Execute a SQL query."""
    storage = FileStorage("database.json")
    db = SimpleSQLDatabase(storage)
    result = db.execute(query)
    if result:
        click.echo(result)


@cli.command()
@click.argument("text")
def embed(text):
    """Convert text to embedding."""
    text_to_embedding = TextToEmbedding()
    embedding = text_to_embedding.convert(text)
    click.echo(embedding)


if __name__ == "__main__":
    cli()
