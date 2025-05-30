# ingest.py
import os
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter # Import LangChain's splitter
from bedrock_client import get_embedding
from opensearch_client import index_chunk, create_index

def read_and_split_pdf_text(file_path, chunk_size=500, chunk_overlap=75):
    """
    Reads text from a PDF and splits it into chunks using RecursiveCharacterTextSplitter.
    """
    reader = PdfReader(file_path)
    full_text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            full_text += page_text + "\n" # Add newline to help splitter identify page breaks if needed

    if not full_text.strip():
        print(f"⚠️ No text extracted from {file_path}")
        return []

    # Initialize the RecursiveCharacterTextSplitter
    # You can experiment with different separators.
    # The default ones are good: ["\n\n", "\n", " ", ""]
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        is_separator_regex=False, # If your separators are not regex
    )

    # Split the text into documents (LangChain's term for chunks)
    # LangChain's splitter returns Document objects, we need the page_content (text)
    documents = text_splitter.create_documents([full_text])
    
    # Extract the text content from each Document object
    text_chunks = [doc.page_content for doc in documents]
    
    print(f"📄 Extracted and split {file_path} into {len(text_chunks)} chunks.")
    return text_chunks

def ingest_pdf(file_path, index_name):
    print(f"\n📥 Ingesting: {file_path}")
    # Use the new function for reading and splitting
    chunks = read_and_split_pdf_text(file_path, chunk_size=1000, chunk_overlap=150) # Adjusted chunk_size and added overlap

    if not chunks:
        print(f"No chunks to ingest for {file_path}.")
        return

    for i, chunk_text in enumerate(chunks):
        if not chunk_text.strip(): # Skip empty chunks that might result from splitting
            print(f"⚠️ Skipping empty chunk {i+1}/{len(chunks)}")
            continue
        embedding = get_embedding(chunk_text)
        index_chunk(index_name, chunk_text, embedding)
        print(f"✅ Indexed chunk {i+1}/{len(chunks)}")

if __name__ == "__main__":
    # Set your OpenSearch index name
    # This should match one of the keys in CHATBOT_CONFIGS or be passed as an argument
    # For simplicity, keeping it hardcoded for SkyConnect for this example.
    # If you are using the multi-bot setup from app.py, you'd want to make this
    # dynamic (e.g., run this script separately for each bot's index_name).

    # To ingest for SkyConnect:
    target_index_name = "skyconnect-knowledge-base"
    target_pdf_files = [
        "data/SkyConnect_Flights.pdf",
        "data/SkyConnect_Baggage_And_Policies.pdf"
    ]
    
    # Or for University (assuming you have these PDFs):
    # target_index_name = "university-course-knowledge-base"
    # target_pdf_files = [
    #     "data/university_courses_catalog.pdf",
    #     "data/university_academic_policies.pdf"
    # ]

    print(f"\n--- Preparing to ingest data for index: {target_index_name} ---")
    create_index(index_to_create=target_index_name) # Assuming create_index is modified

    # Step 2: PDF files to ingest
    for pdf in target_pdf_files:
        if os.path.exists(pdf):
            ingest_pdf(pdf, target_index_name)
        else:
            print(f"⚠️ PDF file not found: {pdf}. Skipping.")
    
    print("\n--- Ingestion process complete. ---")