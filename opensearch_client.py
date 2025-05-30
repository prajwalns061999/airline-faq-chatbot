# opensearch_client.py

from opensearchpy import OpenSearch, RequestsHttpConnection
import boto3
from requests_aws4auth import AWS4Auth
# import uuid # uuid is not currently used, can be removed or kept for future use

# ---------- Configuration ----------
region = "us-east-1" # Consider making this configurable if you might use different regions
host = "<YOUR_OPENSEARCH_ENDPOINT>" # Your OpenSearch endpoint

# Default index name, can be used if no specific index is provided to create_index
DEFAULT_INDEX_NAME = "skyconnect-knowledge-base"
EMBEDDING_DIM = 1536  # Titan Embedding model output size
# -----------------------------------

# AWS authentication
# Ensure your AWS environment (e.g., IAM role for EC2/Lambda, or local AWS CLI config)
# has permissions for aoss:ESHttpPut, aoss:ESHttpPost, aoss:ESHttpGet, etc. on the relevant collection.
credentials = boto3.Session().get_credentials()
aws_auth = AWS4Auth(
    credentials.access_key,
    credentials.secret_key,
    region,
    "aoss", # Service name for OpenSearch Serverless
    session_token=credentials.token
)

# OpenSearch client
client = OpenSearch(
    hosts=[{"host": host.replace("https://", ""), "port": 443}],
    http_auth=aws_auth, # Use the renamed auth object
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
    timeout=60,
    max_retries=3,
    retry_on_timeout=True
)

# Create index with knn_vector mapping
def create_index(index_to_create=DEFAULT_INDEX_NAME): # Function now accepts an argument
    """
    Creates an OpenSearch index with the specified name and KNN mapping.
    If the index already exists, it will be deleted and recreated.

    :param index_to_create: The name of the index to create.
                            Defaults to DEFAULT_INDEX_NAME.
    """
    if not index_to_create:
        print("⚠️ Index name cannot be empty. Using default.")
        index_to_create = DEFAULT_INDEX_NAME

    try:
        if client.indices.exists(index=index_to_create):
            client.indices.delete(index=index_to_create)
            print(f"🗑️ Deleted existing index: {index_to_create}")

        mapping = {
            "settings": {
                "index": {
                    "knn": True,
                    "knn.algo_param.ef_search": 100 # Optional: tune for search performance/accuracy
                }
            },
            "mappings": {
                "properties": {
                    "chunk_text": {"type": "text"},
                    "embedding": {
                        "type": "knn_vector",
                        "dimension": EMBEDDING_DIM,
                        "method": { # Required for OpenSearch Serverless vector search
                            "name": "hnsw",
                            "space_type": "l2", # Can also be "cosinesimil" or "innerproduct"
                            "engine": "nmslib", # Or "faiss" if supported and preferred
                            "parameters": {
                                "ef_construction": 256, # Tune based on dataset size/complexity
                                "m": 48                 # Tune based on dataset size/complexity
                            }
                        }
                    }
                }
            }
        }

        client.indices.create(index=index_to_create, body=mapping)
        print(f"✅ Created index: {index_to_create} with KNN mapping.")
    except Exception as e:
        print(f"❌ Error creating index {index_to_create}: {e}")
        # Potentially re-raise the exception if you want the calling script to handle it
        # raise e


# Index a single chunk with its embedding
def index_chunk(index_name, chunk_text, embedding):
    """
    Indexes a single document (chunk_text and its embedding) into the specified index.
    """
    if not index_name:
        print("⚠️ Index name cannot be empty for indexing. Skipping chunk.")
        return

    body = {
        "chunk_text": chunk_text,
        "embedding": embedding
    }
    try:
        client.index(index=index_name, body=body) # Added refresh for consistency in small ingest jobs
        # For large ingest jobs, consider removing refresh="wait_for" or setting it to False and refreshing manually at the end.
    except Exception as e:
        print(f"❌ Error indexing chunk into {index_name}: {e}")


# Search chunks by query embedding using k-NN
def search_chunks(index_name, query_embedding, k=5):
    """
    Searches for the top k similar chunks in the specified index based on the query embedding.
    """
    if not index_name:
        print("⚠️ Index name cannot be empty for searching. Returning empty results.")
        return []

    query = {
        "size": k,
        "query": {
            "knn": {
                "embedding": { # This 'embedding' matches the field name in your mapping
                    "vector": query_embedding,
                    "k": k
                }
            }
        }
        # You can also add a filter here if needed, e.g., based on metadata
        # "post_filter": {
        #     "term": {
        #         "metadata_field.keyword": "some_value"
        #     }
        # }
    }
    try:
        res = client.search(index=index_name, body=query)
        return res.get("hits", {}).get("hits", []) # Safer way to access nested keys
    except Exception as e:
        print(f"❌ Error searching in index {index_name}: {e}")
        return []