import json
import requests
from DB_utils import *

def get_articles(stock_name):
    url = f'https://api.finlight.me/v1/articles/extended?query={stock_name}%20stock'
    headers = {
        'accept': 'application/json',
        'X-API-KEY': 'sk_862aaf66613d80b143f9d75763c8492e6793287cd677aea34a476dcd7a87dfad',
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises an exception for HTTP errors
        return response.json()['articles']
    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'An error occurred: {err}')



stocks_names = ['Nvidia', 'Apple', 'Meta', 'Google', 'Amazon', 'Advanced Micro Devices', 'Netflix']
stocks_ticks = ['NVDA', 'AAPL', 'META', 'GOOG', 'AMZN', 'AMD', 'NFLX']

news_dict = {}

for stock_name, ticker in zip(stocks_names, stocks_ticks):
    news_dict[ticker] = get_articles(stock_name)

news_dict = {key: [f"{item['title']}\n{item['content']}\nBy: {item['authors']}\nSentiment is {item['sentiment']} with confidence of {item['confidence']}." for item in news] for key, news in news_dict.items()}

# Merge stocks news into one list
whole_dataset = []
for news in news_dict.values():
    whole_dataset += news

# Create Qdrant dataset and insert News.
create_dataset('NewsDatabase_Final')
insert_dataset('NewsDatabase_Final', whole_dataset)

