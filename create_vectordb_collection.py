from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
import argparse

# 1. Parse the command-line arguments
parser = argparse.ArgumentParser(description="Create a Qdrant collection for storing document embeddings.")
parser.add_argument("--db_url", type=str, default='https://530aa750-89da-4fe6-a9cb-19ed5528d94e.us-east4-0.gcp.cloud.qdrant.io', help="URL of the Qdrant database")
parser.add_argument("--api_key", type=str, default='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.3aeb4tAEot-_j4xHTI_Gmc9WKAmgXqXzWNxJTRWHGf4', help="API key for accessing the Qdrant database")
parser.add_argument("--collection_name", type=str, default='news_articles', help="Name of the collection to create")
parser.add_argument("--vector_size", type=int, default=768, help="Size of the document embeddings")
args = parser.parse_args()

# 1. the database URL (and API key, if applicable)
DB_URL = args.db_url  
API_KEY = args.api_key  

# Initialize the Qdrant client using the hardcoded URL
client = QdrantClient(url=DB_URL, api_key=API_KEY)

# 2. Create a collection to store your document embeddings
collection_name = args.collection_name
vector_size = args.vector_size  

# Check if the collection exists; if not, create it
if not client.collection_exists(collection_name):
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
    )
