from langchain.chat_models import AzureChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

import os
from dotenv import load_dotenv

load_dotenv()

class Agent:
    def __init__(self, system=""):
        AZURE_OPENAI_API_KEY = os.getenv("API_KEY")
        DEOLOYMENT_NAME = "team7-gpt4o" # team7-embedding
        AZURE_OPENAI_ENDPOINT = "https://096290-oai.openai.azure.com"
        API_VERSION = "2023-05-15"

        # Initialize the Azure OpenAI chat model
        self.chat = AzureChatOpenAI(
            azure_deployment=DEOLOYMENT_NAME,
            azure_endpoint=AZURE_OPENAI_ENDPOINT,
            api_key=AZURE_OPENAI_API_KEY,
            openai_api_type="azure",
            openai_api_version=API_VERSION,
            temperature=0.7
        )
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