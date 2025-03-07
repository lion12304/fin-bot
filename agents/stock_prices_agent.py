from agent import *
import yfinance as yf
import pandas as pd
import mplfinance as mpf
import os
import base64

FIGURES_DIR = "StocksPricesFigures"


def candle_plot(stock_ticker, stock_prices_df):
    """
    :param stock_ticker: A ticker of a stock
    :param stock_prices_df: A dataframe with the stock prices of the stock, in a specific range of dates
    (approximately a year), with Close, Open, High, Low prices.
    :return: The function saves a .JPEG file of the candle plot corresponding to the stock prices dataframe
    """
    # Define bright colors for the candlestick chart
    mc = mpf.make_marketcolors(up='#00FF00', down='#FF0000', wick='black', edge='black')
    s = mpf.make_mpf_style(marketcolors=mc)

    # Creating the candle plot and saving it to .jpeg file
    os.makedirs(FIGURES_DIR, exist_ok=True)

    output_file = f"{FIGURES_DIR}/{stock_ticker}.jpeg"
    mpf.plot(
        stock_prices_df,
        type="candle",
        style=s,
        title=f"Stock Price Candlestick Chart, {stock_ticker}",
        ylabel="Price (USD)",
        figsize=(18, 6),  # Make the plot wider
        savefig=output_file  # Save as JPEG
    )


def return_image_content(stock_ticker):
    """
    :param stock_ticker: A ticker of a stock
    :return: The function reads the candlestick chart of the stock prices and returns its content
    """
    output_file = f"{FIGURES_DIR}/{stock_ticker}.jpeg"
    with open(output_file, "rb") as image_file:
        image_data = base64.b64encode(image_file.read()).decode("utf-8")
    return image_data


class StockPricesAgent(Agent):
    """The agent handles the stock prices (as a graph saved in .jpeg format)"""
    def __init__(self):
        super().__init__()
        self.DAY_AFTER_HOUR = 16

    def return_dates_range(self, stock_ticker):
        """
        :param stock_ticker: A ticker of a stock
        :return: The function returns two earnings report publication dates, during which a total of
        five earnings reports were published.
        """
        stock = yf.Ticker(stock_ticker)
        earnings_calendar = stock.earnings_dates
        # sorting the earning dates according to date of release
        earnings_calendar = earnings_calendar.sort_index(ascending=False)
        # Four quantiles a year, we want 5 earning reports
        df_filtered = earnings_calendar.dropna().head(5)
        earliest_date = df_filtered.index.min()
        latest_date = df_filtered.index.max()

        earliest_date_date = earliest_date.date()
        latest_date_date = latest_date.date()

        # If the lower bound for hour of releasing the report is below 16:00, it means that
        # the report came out a day before, so we should rectify this
        discard_earliest = False
        if earliest_date.hour < self.DAY_AFTER_HOUR:
            discard_earliest = True
        discard_latest = False
        if latest_date.hour < self.DAY_AFTER_HOUR:
            discard_latest = True
        df_filtered.index = df_filtered.index.strftime('%Y-%m-%d')  # Removing hours
        # Rectifying the dates of release for the latest and earliest reports, which determine the range of dates
        # we look at when considering the stock prices
        if discard_earliest:
            earliest_date_date = earliest_date_date - pd.Timedelta(days=1)
        if discard_latest:
            latest_date_date = latest_date_date - pd.Timedelta(days=1)
        # Updating changes in dates (if there are any)
        index_list = df_filtered.index.to_list()
        index_list[0] = latest_date_date
        index_list[-1] = earliest_date_date
        df_filtered.index = pd.to_datetime(index_list)

        return earliest_date_date, latest_date_date, df_filtered

    def generate_response(self, stock_name: str, stock_ticker: str):
        """
        :param stock_name: A name of a stock
        :param stock_ticker: A ticker of a stock
        :return: The function issues a call to the LLM and returns its response to whether does it think the stock
        will make profit on the next quarter, based on the candlestick chart of the stock's prices
        """
        start_date, end_date, company_numbers_df = self.return_dates_range(stock_ticker)
        # stock_prices_df, a.k.a "Stock prices"
        stock_prices_df = yf.download(stock_ticker, period="5y", auto_adjust=True, progress=False)
        stock_prices_df.index = pd.to_datetime(stock_prices_df.index)
        stock_prices_df = stock_prices_df.loc[start_date:end_date]
        stock_prices_df.columns = stock_prices_df.columns.droplevel('Ticker')
        stock_prices_df.columns.name = None
        candle_plot(stock_ticker, stock_prices_df)
        image_content = return_image_content(stock_ticker)

        messages = []
        if self.system:
            messages.append(SystemMessage(content=self.system))

        image_message = HumanMessage(
            content=[
                {"type": "text",
                 "text": f"Based on the following candlestick chart of the stock's prices, What do you think {stock_name} ({stock_ticker}) "
                         f"stock performance will be in the next quarter? First, state whether the stock is likely to go up or down in the "
                         f"next quarter. Then, provide a brief explanation supporting your prediction."
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{image_content}"},
                },
            ],
        )
        messages.append(image_message)
        # Call the chat model
        response = self.chat(messages=messages)
        return response.content
