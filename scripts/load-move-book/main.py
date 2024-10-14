import os
import requests
import PyPDF2
import time
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List

api_url = os.getenv("ZORKDB_API_URL", "http://localhost:8001")

# Step 1: Extract text from PDF
def extract_text_from_pdf(pdf_path: str) -> str:
    print("Extracting text from PDF...")
    reader = PyPDF2.PdfReader(pdf_path)
    text = "".join(page.extract_text() for page in reader.pages)
    print("Text extraction complete.")
    return text

# Step 2: Split text into paragraphs (chunks)
def split_text_into_paragraphs(text: str, chunk_size: int = 2000, chunk_overlap: int = 200) -> List[str]:
    print("Splitting text into paragraphs...")
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n"],
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )

    pages = text.split("The Move Book\nhttps://move-book.com/print.html")
    chunks = text_splitter.create_documents(pages)
    chunk_list = [chunk.page_content for chunk in chunks]
    total_chunks = len(chunk_list)
    print(f"Text split into {total_chunks} paragraphs.")

    return chunk_list

# Step 3: Convert text to embeddings via HTTP request to ZeroKDB API
def generate_embeddings_via_api(paragraph: str) -> List[float]:
    print("Generating embedding for paragraph...")
    url = f"{api_url}/convert-to-embedding"
    payload = {"text": paragraph}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("Embedding generated successfully.")
        return response.json()['embedding']
    else:
        raise Exception(f"Failed to get embedding: {response.text}")

# Step 4: Create a table if needed via API
def create_table_if_not_exists(table_name: str) -> None:
    print(f"Creating table '{table_name}' if it doesn't exist...")
    url = f"{api_url}/entity"
    payload = {
        "entity_name": table_name,
        "data": {
            table_name: {
                "columns": ["id", "embedding", "text"],
                "column_types": {"id": "INT", "embedding": "TEXT", "text": "TEXT"},
                "rows": [],
                "indexes": {}
            }
        }
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print(f"Table '{table_name}' created successfully.")
    elif response.status_code == 400 and "already exists" in response.json().get("detail", ""):
        print(f"Table '{table_name}' already exists.")
    else:
        raise Exception(f"Failed to create table: {response.text}")

# Step 5: Store embeddings and text in the ZeroKDB table via API
def store_in_db_via_api(table_name: str, paragraphs: List[str], embeddings: List[List[float]]) -> None:
    print("Storing embeddings and text in the database...")
    url = f"{api_url}/append-data"
    for i, (paragraph, embedding) in enumerate(zip(paragraphs, embeddings), start=1):
        print(f"Storing data for paragraph {i}/{len(paragraphs)}")
        payload = {
            "table_name": table_name,
            "data": {
                table_name: {
                    "columns": ["id", "embedding", "text"],
                    "column_types": {"id": "INT", "embedding": "TEXT", "text": "TEXT"},
                    "indexes": {},
                    "rows": [[i, str(embedding), paragraph]]
                }
            }
        }
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            raise Exception(f"Failed to append data: {response.text}")
        print(f"Data for paragraph {i} stored successfully.")
        time.sleep(6)  # Sleep for 2 seconds between requests

# Main function to handle the entire flow
def process_pdf_to_zerokdb(pdf_path: str, table_name: str = "pdf_data", create_table: bool = True) -> None:
    print(f"Processing PDF: {pdf_path}")
    text = extract_text_from_pdf(pdf_path)
    if create_table:
        create_table_if_not_exists(table_name)
    paragraphs = split_text_into_paragraphs(text)
    print("Generating embeddings for all paragraphs...")
    embeddings = [generate_embeddings_via_api(paragraph) for paragraph in paragraphs]
    print("Embeddings generated for all paragraphs.")
    store_in_db_via_api(table_name, paragraphs, embeddings)
    print("Processing complete.")

# Entry point
if __name__ == "__main__":
    pdf_path = "data/move-book.pdf"
    table_name = "move_book"

    try:
        print(f"Starting process for PDF: {pdf_path}")
        process_pdf_to_zerokdb(pdf_path, table_name, create_table=True)
        print(f"Data from {pdf_path} has been successfully stored in table {table_name}")
    except Exception as e:
        print(f"An error occurred: {e}")
