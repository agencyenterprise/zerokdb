import os
import time
import requests
import PyPDF2

api_url = os.getenv("ZORKDB_API_URL", "http://localhost:8000")

# Step 1: Extract text from PDF
def extract_text_from_pdf(pdf_path):
    reader = PyPDF2.PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

# Step 2: Convert text to embeddings via HTTP request to ZeroKDB API
def generate_embeddings_via_api(sentence):
    url = f"{api_url}/convert-to-embedding"  # Adjust the URL according to your API route
    payload = {"text": sentence}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()['embedding']
    else:
        raise Exception(f"Failed to get embedding: {response.text}")

# Step 3: Store embeddings and text in the ZeroKDB table via API
def store_in_db_via_api(table_name, sentences, embeddings):
    url = f"{api_url}/append-data"
    for i, (sentence, embedding) in enumerate(zip(sentences, embeddings), start=1):
        payload = {
            "table_name": table_name,
            "data": {
                "id": i,
                "sentence": sentence,
                "embedding": embedding
            }
        }
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            raise Exception(f"Failed to append data: {response.text}")

# Main function to handle the entire flow
def process_pdf_to_ipfs(pdf_path, table_name="pdf_data"):
    # Extract text
    text = extract_text_from_pdf(pdf_path)

    # Generate embeddings for each sentence
    sentences = text.split(". ")

    print('test', sentences)


    #embeddings = [generate_embeddings_via_api(sentence) for sentence in sentences]

    # Store data in ZeroKDB via API
    #store_in_db_via_api(table_name, sentences, embeddings)

# Entry point
if __name__ == "__main__":
    pdf_path = "data/move-book.pdf"
    table_name = f"move-book"

    try:
        process_pdf_to_ipfs(pdf_path, table_name)
        print(f"Data from {pdf_path} has been successfully stored in table {table_name}")
    except Exception as e:
        print(f"An error occurred: {e}")
