import os
import time
import requests
import PyPDF2
from langchain.text_splitter import RecursiveCharacterTextSplitter

api_url = os.getenv("ZORKDB_API_URL", "http://localhost:8001")

# Step 1: Extract text from PDF
def extract_text_from_pdf(pdf_path):
    reader = PyPDF2.PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Step 2: Split text into paragraphs (chunks)
def split_text_into_paragraphs(text, chunk_size=2000, chunk_overlap=200):

    # Using RecursiveCharacterTextSplitter from Langchain to split by paragraphs
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n"],  # Split by paragraph breaks
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len
    )

    pages = text.split("The Move Book\nhttps://move-book.com/print.html")

    # Create chunks
    chunks = text_splitter.create_documents(pages)

    # Extract the chunk text for each chunk
    chunk_list = [chunk.page_content for chunk in chunks]
    return chunk_list

# Step 3: Convert text to embeddings via HTTP request to ZeroKDB API
def generate_embeddings_via_api(paragraph):
    url = f"{api_url}/convert-to-embedding"  # Adjust the URL according to your API route
    payload = {"text": paragraph}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()['embedding']
    else:
        raise Exception(f"Failed to get embedding: {response.text}")

# Step 4: Create a table if needed via API
def create_table_if_not_exists(table_name):
    url = f"{api_url}/entity"
    payload = {
        "entity_name": table_name,
        "data": {}  # Assuming an empty initial data set
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print(f"Table '{table_name}' created successfully.")
    elif response.status_code == 400 and "already exists" in response.json().get("detail", ""):
        print(f"Table '{table_name}' already exists.")
    else:
        raise Exception(f"Failed to create table: {response.text}")

# Step 5: Store embeddings and text in the ZeroKDB table via API
def store_in_db_via_api(table_name, paragraphs, embeddings):
    url = f"{api_url}/append-data"
    for i, (paragraph, embedding) in enumerate(zip(paragraphs, embeddings), start=1):
        payload = {
            "table_name": table_name,
            "data": {
                "id": i,
                "paragraph": paragraph,
                "embedding": embedding
            }
        }
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            raise Exception(f"Failed to append data: {response.text}")

# Main function to handle the entire flow
def process_pdf_to_zerokdb(pdf_path, table_name="pdf_data", create_table=True):
    # Extract text
    text = extract_text_from_pdf(pdf_path)

    # Optionally create a new table
    if create_table:
        create_table_if_not_exists(table_name)

    # Split the text into paragraph chunks
    paragraphs = split_text_into_paragraphs(text)

    # Generate embeddings for each paragraph
    embeddings = [generate_embeddings_via_api(paragraph) for paragraph in paragraphs]

    # Store data in ZeroKDB via API
    store_in_db_via_api(table_name, paragraphs, embeddings)

# Entry point
if __name__ == "__main__":
    pdf_path = "data/move-book.pdf"
    table_name = f"move_book"

    try:
        process_pdf_to_zerokdb(pdf_path, table_name, create_table=True)
        print(f"Data from {pdf_path} has been successfully stored in table {table_name}")
    except Exception as e:
        print(f"An error occurred: {e}")
