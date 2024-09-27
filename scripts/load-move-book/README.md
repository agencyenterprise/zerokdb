# IPFS Content Ingestion with ZeroKDB and Text Embeddings

This project demonstrates how to extract text from a PDF file, convert the text into embeddings using the Universal Sentence Encoder (USE), and then ingest the content into IPFS using the ZeroKDB API. The embeddings are stored in IPFS, making the content searchable and accessible.

## Project Structure

- `main.py`: Main script to extract PDF content, generate embeddings, and store the data in IPFS using ZeroKDB API.
- `requirements.txt`: Dependencies required for running the project.
- `README.md`: Project documentation.

## Features

- Extracts text content from a PDF file.
- Converts the text into embeddings using the Universal Sentence Encoder (USE).
- Ingests the data into IPFS using ZeroKDB and returns the CID of the stored content.
- Allows for easy interaction with IPFS for decentralized storage.

## Requirements

- Python 3.7+
- TensorFlow for USE embeddings
- ZeroKDB API for IPFS interaction

## Setup

1. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

1. Run the script:

   ```bash
   python main.py
   ```

## Configuration

- Place the PDF file you want to process in the `data/` directory or provide its path in the `main.py` script.
- Make sure the ZeroKDB API is configured with your credentials and access details.
