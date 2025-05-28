import boto3
import json

def get_bedrock_runtime(region="us-east-1"):
    return boto3.client("bedrock-runtime", region_name=region)

def get_embedding(text, model_id="amazon.titan-embed-text-v1"):
    client = get_bedrock_runtime()
    payload = {
        "inputText": text
    }

    response = client.invoke_model(
        modelId=model_id,
        contentType="application/json",
        body=json.dumps(payload)
    )

    response_body = json.loads(response['body'].read())
    return response_body['embedding']

def query_llm(question, context):
    # Updated prompt for more precise, context-bound answers
    prompt = f"""
Human: You are SkyConnect Airlines' friendly and helpful assistant. Greet and introduce yourself to the user if the user greets you.
Your primary goal is to answer the user's question accurately and concisely based **only** on the information available in the provided 'Context' below.
Do not use any external knowledge or make assumptions beyond what is stated in the context.
If the answer to the question cannot be found within the provided context, clearly state that you don't have enough information from the documents to answer.
Avoid speculation. Be direct and helpful.

Context:
{context}

Question: {question}

Assistant:"""

    bedrock = boto3.client('bedrock-runtime', region_name="us-east-1")

    body = {
        "prompt": prompt,
        "max_tokens_to_sample": 512, # Increased slightly for potentially more detailed context-based answers
        "temperature": 0.3, # Lowered for more factual, less creative responses
        "top_p": 0.9,
        "stop_sequences": ["\n\nHuman:"]
    }

    response = bedrock.invoke_model(
        body=json.dumps(body),
        modelId="anthropic.claude-v2:1", # Ensure this is the model you intend to use. Claude v2.1 or v3 Sonnet might offer better instruction following.
        accept="application/json",
        contentType="application/json"
    )

    response_body = json.loads(response['body'].read())
    return response_body['completion'].strip() 