import os
from PyPDF2 import PdfReader
from bedrock_client import get_embedding
from opensearch_client import index_chunk, create_index

def read_pdf_chunks(file_path, chunk_size=500):
    reader = PdfReader(file_path)
    full_text = " ".join([page.extract_text() for page in reader.pages if page.extract_text()])
    chunks = [full_text[i:i+chunk_size] for i in range(0, len(full_text), chunk_size)]
    return chunks

def ingest_pdf(file_path, index_name):
    print(f"\n📥 Ingesting: {file_path}")
    chunks = read_pdf_chunks(file_path)
    for i, chunk in enumerate(chunks):
        embedding = get_embedding(chunk)
        index_chunk(index_name, chunk, embedding)
        print(f"✅ Indexed chunk {i+1}/{len(chunks)}")

if __name__ == "__main__":
    # Set your OpenSearch index name
    index_name = "skyconnect-knowledge-base"

    # Step 1: Create index with correct mapping
    create_index()

    # Step 2: PDF files to ingest
    pdf_files = [
        "data/SkyConnect_Flights.pdf",
        "data/SkyConnect_Baggage_And_Policies.pdf"
    ]

    for pdf in pdf_files:
        ingest_pdf(pdf, index_name)
