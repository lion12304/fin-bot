from agent import *
import yfinance as yf
import pandas as pd
from tabulate import tabulate

def format_EPS_table_company_numbers(numbers_df):
    """
    :param numbers_df: A dataframe of the earning reports numbers of the stock
    :return: A string format of the dataframe to be inserted to the LLM
    """
    header = "Date       | EPS Estimate | Reported EPS | Surprise (%)"
    separator = "-" * len(header)
    rows = [f"{index.strftime('%Y-%m-%d')} | {row['EPS Estimate']:.2f}        | {row['Reported EPS']:.2f}         | {row['Surprise(%)']:.2f}"
        for index, row in numbers_df.iterrows()]

    table = "\n".join([header, separator] + rows)
    return table

def format_table_company_numbers(stock_ticker):
    stock = yf.Ticker(stock_ticker)
    quarterly_income_stmt = stock.quarterly_income_stmt.iloc[:, :5].T

    # Replace NaN with a nicer value (e.g., "N/A")
    df = quarterly_income_stmt.fillna("N/A")

    # Create a pipe-separated table string using tabulate
    table_str = tabulate(df, headers='keys', tablefmt='pipe')
    return table_str



class CompanyNumbersAgent(Agent):
    """The agent handles company numbers about the stock"""
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
        will make profit on the next quarter, based on the numerical values of the company's earning reports
        """
        _, _, company_numbers_df = self.return_dates_range(stock_ticker)
        table = format_EPS_table_company_numbers(company_numbers_df)

        formatted_prompt = (f"The following table contains numerical statistics on the last five quarterly earnings reports of {stock_name} "
                            f"({stock_ticker}). It includes the earnings per share (EPS) estimate, the reported EPS, and the earnings surprise "
                            f"percentage for each quarter.\n**Company Earnings Data:**\n\n{table}\n\nAdditionally, here is a table which compares "
                            f"the financial performance of the company according to the last five earning reports (including the last):\n"
                            f"**Company Earnings Data:**\n\n{format_table_company_numbers(stock_ticker)}\n\nBased on this information, "
                            f"what do you think {stock_name} ({stock_ticker}) stock performance will be in the next quarter? First, "
                            f"state whether the stock is likely to go up or down in the next quarter. Then, provide a brief explanation "
                            f"supporting your prediction.")

        response = super().generate_response(formatted_prompt)
        return response
