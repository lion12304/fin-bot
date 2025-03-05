from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from langchain_openai import AzureOpenAIEmbeddings
import tiktoken
from tqdm import tqdm
import os

from dotenv import load_dotenv

load_dotenv()

# 1. the database URL (and API key, if applicable)
QDRANT_URL = "https://530aa750-89da-4fe6-a9cb-19ed5528d94e.us-east4-0.gcp.cloud.qdrant.io"
QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.3aeb4tAEot-_j4xHTI_Gmc9WKAmgXqXzWNxJTRWHGf4"

# Initialize the Qdrant client using the hardcoded URL
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

# Azure settings
AZURE_OPENAI_API_KEY = os.getenv("API_KEY")
AZURE_OPENAI_ENDPOINT = "https://096290-oai.openai.azure.com"
API_VERSION = "2023-05-15"

# Max tokens in a tokenized news
max_input_tokens = 8192

# Embedder Dim
vector_size = 1536

# Initialize the AzureOpenAIEmbeddings class
embedder = AzureOpenAIEmbeddings(
    azure_deployment="team7-embedding",
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
    openai_api_type="azure",
    openai_api_version=API_VERSION
)

# Embed given document using LangChain
def embed(document: str) -> list:
    # Use the tiktoken tokenizer from LangChain to handle the token limit
    enc = tiktoken.get_encoding("cl100k_base")
    if len(enc.encode(document)) > max_input_tokens:
        document = enc.decode(enc.encode(document)[:max_input_tokens])  # Truncate to max tokens

    # Generate the embedding
    embedding = embedder.embed_query(document)

    return embedding

def create_dataset(collection_name):
    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
        )
        print("Dataset created!")
    else:
        print("Dataset already exists!")


# Inserts documents into dataset
def insert_dataset(collection_name, documents):
    # Prepare points to insert into Qdrant
    points = [
        PointStruct(
            id=i,
            vector=embed(doc),
            payload={"text": doc}
        )
        for i, doc in tqdm(enumerate(documents))
    ]


    # Upsert (insert or update) the points into Qdrant
    client.upsert(collection_name=collection_name, points=points)

    print(f"Documents loaded into Qdrant dataset: {collection_name}.")


def retrieve_docs(query, collection_name, number_of_docs=5):
    # Embed the query using the same embedding function (or model)
    query_vector = embed(query)

    # Perform a similarity search in Qdrant
    search_result = client.query_points(
        collection_name=collection_name,
        query=query_vector,
        limit=number_of_docs  # Retrieve top 3 most similar documents
    )

    # Extract the payloads (e.g., the text content)
    retrieved_docs = [f'{i + 1}. {point.payload["text"]}' for i, point in enumerate(search_result.points)]

    # Combine the retrieved documents into a context string
    context = "\n\n".join(retrieved_docs)
    return context
