# ✈️ SkyConnect Airlines Concierge Chatbot

This project is an initial draft of a Retrieval Augmented Generation (RAG) chatbot designed to answer user queries about SkyConnect Airlines' flight schedules, baggage policies, and other related information. It leverages AWS Bedrock for LLM and embedding capabilities and Amazon OpenSearch Serverless as a vector database.

## ✨ Features

*   Conversational interface for asking questions.
*   Retrieves relevant information from PDF documents.
*   Uses AWS Bedrock (Amazon Titan for embeddings, Anthropic Claude for generation).
*   Stores and searches knowledge using Amazon OpenSearch Serverless.
*   User interface built with Streamlit.
*   Conversation history.

## 🔧 Prerequisites

Before you begin, ensure you have the following installed and configured:

1.  **Python 3.8+**
2.  **Git**
3.  **AWS Account**: You'll need an active AWS account.
4.  **AWS CLI**: Configured with credentials that have permissions for AWS Bedrock and Amazon OpenSearch Serverless.
    *   Ensure you have enabled model access for `amazon.titan-embed-text-v1` and `anthropic.claude-v2:1` (or `anthropic.claude-v2.1`, `anthropic.claude-3-sonnet-20240229-v1:0` etc. depending on your choice) in the Bedrock console for the region you intend to use.
5.  **Amazon OpenSearch Serverless Domain**:
    *   Create an OpenSearch Serverless collection (vector search type).
    *   Note down the **OpenSearch domain endpoint URL**.
    *   Ensure your AWS user/role has network access and data access policies configured for this collection.

## ⚙️ Setup and Installation

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git
    cd YOUR_REPOSITORY_NAME
    ```
    *(Replace `YOUR_USERNAME/YOUR_REPOSITORY_NAME` with your actual GitHub repository path)*

2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv myenv
    ```
    *   Activate the environment:
        *   Windows: `myenv\Scripts\activate`
        *   macOS/Linux: `source myenv/bin/activate`

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Prepare Data Files:**
    *   Ensure you have the following PDF files in the `data/` directory:
        *   `data/SkyConnect_Flights.pdf`
        *   `data/SkyConnect_Baggage_And_Policies.pdf` (or `SkyConnect_BaggagePolicies.pdf` if you named it that)
    *(You can use the sample PDFs you created or your own versions)*

5.  **Configure AWS and OpenSearch Details:**

    *   **Open `opensearch_client.py`:**
        *   Update the `region` variable to your AWS region (e.g., `"us-east-1"`).
        *   Update the `host` variable with your **OpenSearch Serverless domain endpoint URL**.
            ```python
            # opensearch_client.py
            region = "us-east-1" # <-- YOUR AWS REGION
            host = "https://YOUR_OPENSEARCH_ENDPOINT.aoss.amazonaws.com" # <-- YOUR OPENSEARCH ENDPOINT
            INDEX_NAME = "skyconnect-knowledge-base"
            EMBEDDING_DIM = 1536
            ```

    *   **Open `bedrock_client.py`:**
        *   Ensure the `region` variable in `get_bedrock_runtime()` and `query_llm()` matches your AWS region.
            ```python
            # bedrock_client.py
            def get_bedrock_runtime(region="us-east-1"): # <-- YOUR AWS REGION
                return boto3.client("bedrock-runtime", region_name=region)

            # ... ensure region is consistent in query_llm if explicitly set there
            bedrock = boto3.client('bedrock-runtime', region_name="us-east-1") # <-- YOUR AWS REGION
            ```

## 🚀 Running the Application

There are two main steps to run the application:

1.  **Ingest Data into OpenSearch:**
    This script will read the PDF files, chunk them, generate embeddings, create an OpenSearch index (if it doesn't exist or deletes the old one), and index the chunks.
    ```bash
    python ingest.py
    ```
    You should see output indicating chunks being indexed.

2.  **Run the Streamlit Chatbot Application:**
    ```bash
    streamlit run app.py
    ```
    This will open the chatbot interface in your web browser.

## 🛠️ Key Technologies Used

*   **Python**
*   **Streamlit**: For the web application UI.
*   **AWS Bedrock**:
    *   **Amazon Titan Embeddings**: For generating text embeddings.
    *   **Anthropic Claude**: For generating conversational responses.
*   **Amazon OpenSearch Serverless**: As a vector database for semantic search.
*   **PyPDF2**: For reading text from PDF files.
*   **Boto3**: AWS SDK for Python.
*   **Requests-AWS4Auth**: For AWS SigV4 authentication with OpenSearch.

## 🔮 Future Enhancements (Ideas)

*   Support for more document types (e.g., .txt, .docx).
*   More sophisticated chunking strategies.
*   Fine-tuning prompts for specific use cases.
*   Integration with actual booking systems (advanced).
*   User authentication and personalized experiences.

---
*This is an initial draft. Setup and configuration, especially for AWS services, need to be done carefully.*
