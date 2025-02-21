import argparse
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
import os
import openai

# 1. Parse the command-line arguments
parser = argparse.ArgumentParser(description="Create a Qdrant collection for storing document embeddings.")
parser.add_argument("--db_url", type=str, default='https://530aa750-89da-4fe6-a9cb-19ed5528d94e.us-east4-0.gcp.cloud.qdrant.io', help="URL of the Qdrant database")
parser.add_argument("--api_key", type=str, default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.3aeb4tAEot-_j4xHTI_Gmc9WKAmgXqXzWNxJTRWHGf4', help="API key for accessing the Qdrant database")
parser.add_argument("--collection_name", type=str, default='news_articles', help="Name of the collection to create")
parser.add_argument("--vector_size", type=int, default=768, help="Size of the document embeddings")
parser.add_argument("--azure_endpoint", type=str, help="Azure OPENAI ENDPOINT")
parser.add_argument("--azure_api_key", type=str, help="Azure OpenAI API key")
args = parser.parse_args()

# 1. the database URL (and API key, if applicable)
DB_URL = args.db_url
API_KEY = args.api_key

# Initialize the Qdrant client using the hardcoded URL
client = QdrantClient(url=DB_URL, api_key=API_KEY)

# 2. Create a collection to store your document embeddings
collection_name = args.collection_name
vector_size = args.vector_size

# Dummy function to generate embeddings; replace with your actual embedding logic
def embed(document: str) -> list:
    # Set your Azure OpenAI resource variables
    openai.api_type = "azure"
    openai.api_base = os.getenv("AZURE_OPENAI_ENDPOINT", args.azure_endpoint)
    openai.api_version = "2023-03-15-preview"
    openai.api_key = os.getenv("AZURE_OPENAI_API_KEY", args.azure_api_key)

    # Call the embedder "text-embedding-ada-002"
    response = openai.Embedding.create(
        input=document,
        deployment_id="text-embedding-ada-002"
    )

    # Extract and print the embedding vector
    embedding = response["data"][0]["embedding"]
    return embedding

def insert_dataset(collection_name, vector_size, documents, client):
    # Create collection if it doesn't exist
    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
        )

    # Prepare points to insert into Qdrant
    points = [
        PointStruct(
            id=i,
            vector=embed(doc),
            payload={"text": doc}
        )
        for i, doc in enumerate(documents)
    ]

    # Upsert (insert or update) the points into Qdrant
    client.upsert(collection_name=collection_name, points=points)

    print(f"Documents loaded into Qdrant dataset: {collection_name}.")


def retrieve_docs(query):
    # Embed the query using the same embedding function (or model)
    query_vector = embed(query)

    # Perform a similarity search in Qdrant
    search_result = client.query_points(
        collection_name=collection_name,
        query=query_vector,
        limit=3  # Retrieve top 3 most similar documents
    )

    # Extract the payloads (e.g., the text content)
    retrieved_docs = [point.payload["text"] for point in search_result.points]

    # Combine the retrieved documents into a context string
    context = "\n\n".join(retrieved_docs)
    return context


def rag_generate(context, query_text):
    prompt = f"Based on the following documents:\n\n{context}\n\nAnswer the following question:\n{query_text}"
    openai.api_key = "YOUR_OPENAI_API_KEY"

    response = openai.Completion.create(
        engine="gpt-o4",
        prompt=prompt,
        max_tokens=150,
        temperature=0.7,
    )

    print("Generated answer:", response.choices[0].text.strip())

