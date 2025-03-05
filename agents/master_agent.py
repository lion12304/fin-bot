from copmany_numbers_agent import CompanyNumbersAgent
from literal_quarterly_report_agent import LiteralQuarterlyReportAgent
from news_agent import NewsAgent
from stock_prices_agent import StockPricesAgent
from agent import Agent
import json
from Levenshtein import distance as lev_distance

class MasterAgent(Agent):
    def __init__(self):
        super().__init__()
        self.our_stocks = [('Netflix', 'NFLX'), ('Apple', 'AAPL'), ('Google', 'GOOGL'), ('Amazon', 'AMZN'), ('NVIDIA', 'NVDA'), ('AMD', 'AMD'), ('Meta', 'META')]
        
    def choose_stock_and_return_result(self):
        print('Hi, I am finBot, an AI-driven finance agent. I can help you predict whether a stock is likely to go up or down in the next quarter.\n Please provide me with the name or the ticker symbol of the stock you would like me to analyze.')
        while True:
            user_input = input().lower()
            stock_name, stock_ticker = None, None
            best_distance = float('inf')
            for stock_name, stock_ticker in self.our_stocks:
                stock_name_lower = stock_name.lower()
                stock_ticker_lower = stock_ticker.lower()
                distance = min(lev_distance(user_input, stock_name_lower), lev_distance(user_input, stock_ticker_lower))
                if distance < best_distance:
                    best_distance = distance
                    stock_name, stock_ticker = stock_name, stock_ticker
            if distance != 0:
                print('Sorry, we don\'t have information on this stock yet. Did you mean to ask about', stock_name, '(', stock_ticker, ')? \n Please provide me with the name or the ticker symbol of the stock you would like me to analyze.')
            else:
                result = self.generate_response(stock_name, stock_ticker)
                print(f"Based on the information provided, the stock of {stock_name} ({stock_ticker}) is likely to go {'up' if result else 'down'} in the next quarter.")
                break

    def generate_response(self, stock_name: str, stock_ticker: str) -> bool:
        print('Generating Response according to News:')
        news_agent = NewsAgent()
        news_summary = news_agent.generate_response_rag(stock_name, stock_ticker)

        print('Generating Response according to Q10 filing:')
        literal_quarterly_report_agent = LiteralQuarterlyReportAgent()
        q10_summary = literal_quarterly_report_agent.generate_response_rag(stock_name, stock_ticker)

        print('Generating Response according to Stock Prices:')
        stock_prices_agent = StockPricesAgent()
        graph_summary = stock_prices_agent.generate_response(stock_name, stock_ticker)

        print('Generating Response according to Company Numbers:')
        company_numbers_agent = CompanyNumbersAgent()
        financial_summary = company_numbers_agent.generate_response(stock_name, stock_ticker)

        formatted_prompt = f"Based on the following summaries of predictions from four models, predict whether the stock of {stock_name} ({stock_ticker}) is likely to go up or down in the next quarter.\n\n"

        formatted_prompt += "1. **News about the stock:**\n"
        formatted_prompt += f"{news_summary}\n\n"

        formatted_prompt += "2. **Stock price graph analysis:**\n"
        formatted_prompt += f"{graph_summary}\n\n"

        formatted_prompt += "3. **Q10 filing analysis:**\n"
        formatted_prompt += f"{q10_summary}\n\n"

        formatted_prompt += "4. **Financial numbers (e.g., EPS, revenue, etc.):**\n"
        formatted_prompt += f"{financial_summary}\n\n"

        formatted_prompt += "Based on these explanations, please predict the stock's movement in the next quarter with a simple 'up' or 'down' as your answer."

        response = super().generate_response(formatted_prompt)

        return True if 'up' in response.lower() else False

