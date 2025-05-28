# opensearch_client.py

from opensearchpy import OpenSearch, RequestsHttpConnection
import boto3
from requests_aws4auth import AWS4Auth
import uuid

# ---------- Configuration ----------
region = "us-east-1"
host = "Your_OpenSearch_Endpoint"
INDEX_NAME = "skyconnect-knowledge-base"
EMBEDDING_DIM = 1536  # Titan Embedding model output size
# -----------------------------------

# AWS authentication
credentials = boto3.Session().get_credentials()
auth = AWS4Auth(credentials.access_key, credentials.secret_key, region, "aoss", session_token=credentials.token)

# OpenSearch client
client = OpenSearch(
    hosts=[{"host": host.replace("https://", ""), "port": 443}],
    http_auth=auth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
    timeout=60,
    max_retries=3,
    retry_on_timeout=True
)

# Create index with knn_vector mapping
def create_index():
    if client.indices.exists(index=INDEX_NAME):
        client.indices.delete(index=INDEX_NAME)
        print(f"🗑️ Deleted existing index: {INDEX_NAME}")

    mapping = {
        "settings": {
            "index": {
                "knn": True
            }
        },
        "mappings": {
            "properties": {
                "chunk_text": {"type": "text"},
                "embedding": {
                    "type": "knn_vector",
                    "dimension": EMBEDDING_DIM
                }
            }
        }
    }

    client.indices.create(index=INDEX_NAME, body=mapping)
    print(f"✅ Created index: {INDEX_NAME}")

# Index a single chunk with its embedding
def index_chunk(index_name, chunk_text, embedding):
    body = {
        "chunk_text": chunk_text,
        "embedding": embedding
    }
    client.index(index=index_name, body=body)

# Search chunks by query embedding using k-NN
def search_chunks(index_name, query_embedding, k=5):
    query = {
        "size": k,
        "query": {
            "knn": {
                "embedding": {
                    "vector": query_embedding,
                    "k": k
                }
            }
        }
    }
    res = client.search(index=index_name, body=query)
    return res["hits"]["hits"]


