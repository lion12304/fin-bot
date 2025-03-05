from langchain.chat_models import AzureChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

load_dotenv()

class Agent:
    def __init__(self, system="You are finBot, an AI-driven finance agent."):
        self.AZURE_OPENAI_API_KEY = os.getenv("API_KEY")
        self.DEPLOYMENT_NAME = "team7-gpt4o"  # team7-embedding
        self.AZURE_OPENAI_ENDPOINT = "https://096290-oai.openai.azure.com"
        self.API_VERSION = "2023-05-15"
        self.max_tokens = 1000

        # Initialize the Azure OpenAI chat model
        self.chat = AzureChatOpenAI(
            azure_deployment=self.DEPLOYMENT_NAME,
            azure_endpoint=self.AZURE_OPENAI_ENDPOINT,
            api_key=self.AZURE_OPENAI_API_KEY,
            openai_api_type="azure",
            openai_api_version=self.API_VERSION,
            temperature=0,
            max_tokens=self.max_tokens
        )

        self.QDRANT_URL = "https://530aa750-89da-4fe6-a9cb-19ed5528d94e.us-east4-0.gcp.cloud.qdrant.io"
        self.QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.3aeb4tAEot-_j4xHTI_Gmc9WKAmgXqXzWNxJTRWHGf4"
        self.qdrant_client = QdrantClient(url=self.QDRANT_URL, api_key=self.QDRANT_API_KEY)

        self.system = system

    def generate_response(self, user_input: str) -> str:
        # Render the final prompt
        if self.system:
            messages = [
                SystemMessage(content=self.system),
                HumanMessage(content=user_input)
            ]
        else:
            messages = [
                HumanMessage(content=user_input)
            ]
        # Call the chat model
        response = self.chat(messages=messages)
        return response.content