from agent import Agent
from create_datasets import create_literal_earnings_report_dataset
from create_datasets.DB_utils import *
import time


class LiteralQuarterlyReportAgent(Agent):
    def __init__(self):
        super().__init__()
        self.QDRANT_URL = "https://530aa750-89da-4fe6-a9cb-19ed5528d94e.us-east4-0.gcp.cloud.qdrant.io"
        self.QDRANT_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.3aeb4tAEot-_j4xHTI_Gmc9WKAmgXqXzWNxJTRWHGf4"

        self.client = QdrantClient(url=self.QDRANT_URL, api_key=self.QDRANT_API_KEY)


    def generate_response_rag(self, stock_name: str, stock_ticker: str):
        # Creates the corpus out of the Q10 filing.
        create_literal_earnings_report_dataset.create_literal_earnings_report_dataset(stock_ticker)

        print('Waiting 30 seconds before generating response due to api calls limit.')
        time.sleep(30)

        # 1. Retrieve the most relevant News for a stock.
        query = "What information in this Q10 filing indicates whether the company’s stock is likely to go up or down in the next quarter? Focus on financial performance, future guidance, risks, and significant events."
        stock_news = retrieve_docs(query, f'Q10_{stock_ticker}', 3)

        # 2. Use retrieved docs for recommendation generation.
        formatted_prompt = (f"Based on the following sections from the last Q10 filing:\n\n{stock_news}\n\nWhat do you think {stock_name} "
                            f"({stock_ticker}) stock performance will be in the next quarter? First, state whether the stock is likely to go "
                            f"up or down in the next quarter. Then, provide a brief explanation supporting your prediction.")
        response = super().generate_response(formatted_prompt)

        return response