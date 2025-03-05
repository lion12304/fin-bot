from agent import *
from create_datasets.DB_utils import *


class NewsAgent(Agent):
    def __init__(self):
        super().__init__()

    def generate_response_rag(self, stock_name: str, stock_ticker: str):
        # 1. Retrieve the most relevant News for a stock.
        query = (f"Retrieve the most relevant and impactful news about {stock_name} ({stock_ticker}) that could influence its stock price. "
                 f"Focus on recent developments related to financial performance, market trends, key risks, new products, leadership changes, "
                 f"and any major events or announcements.")
        stock_news = retrieve_docs(query, 'NewsDatabase_Final')

        # 2. Use retrieved docs for recommendation generation.
        formatted_prompt = (f"Based on the following three news documents:\n\n{stock_news}\n\nWhat do you think {stock_name} ({stock_ticker}) "
                            f"stock performance will be in the next quarter? First, state whether the stock is likely to go up or down in the "
                            f"next quarter. Then, provide a brief explanation supporting your prediction.")
        response = super().generate_response(formatted_prompt)

        return response

