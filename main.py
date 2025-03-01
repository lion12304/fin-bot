import yfinance as yf
import pandas as pd
import mplfinance as mpf
from PIL import Image

DAY_AFTER_HOUR = 16

def return_dates_range(stock_name):
    """
    :param stock_name: A name of a stock
    :return: The function returns two earnings report publication dates, during which a total of
    five earnings reports were published.
    """
    stock = yf.Ticker(stock_name)
    earnings_calendar = stock.earnings_dates
    # sorting the earning dates according to date of release
    earnings_calendar = earnings_calendar.sort_index(ascending=False)
    # Four quantiles a year, we want 5 earning reports
    df_filtered = earnings_calendar.dropna().head(5)
    earliest_date = df_filtered.index.min()
    latest_date = df_filtered.index.max()

    earliest_date_date = earliest_date.date()
    latest_date_date = latest_date.date()
    assert earliest_date_date.month == latest_date_date.month
    assert earliest_date_date.year == latest_date_date.year - 1

    # If the lower bound for hour of releasing the report is below 16:00, it means that
    # the report came out a day before, so we should rectify this
    discard_earliest = False
    if earliest_date.hour < DAY_AFTER_HOUR:
        discard_earliest = True
    discard_latest = False
    if latest_date.hour < DAY_AFTER_HOUR:
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


def candle_plot(stock, stock_prices_df):
    """
    :param stock: A name of a stock
    :param stock_prices_df: A dataframe with the stock prices of the stock, in a specific range of dates
    (approximately a year), with Close, Open, High, Low prices.
    :return: The function saves a .png file of the candle plot corresponding to the stock prices dataframe
    """
    # Define bright colors for the candlestick chart
    mc = mpf.make_marketcolors(up='#00FF00', down='#FF0000', wick='black', edge='black')
    s = mpf.make_mpf_style(marketcolors=mc)

    # Creating the candle plot and saving it to .png file
    output_file = f"{stock}.png"
    mpf.plot(
        stock_prices_df,
        type="candle",
        style=s,
        title=f"Stock Price Candlestick Chart, {stock}",
        ylabel="Price (USD)",
        figsize=(18, 6),  # Make the plot wider
        savefig=output_file  # Save as PNG
    )


def main():
    stock = "NVDA"
    # company_numbers_df, a.k.a "Earnings numbers"
    start_date, end_date, company_numbers_df = return_dates_range(stock)
    # stock_prices_df, a.k.a "Stock prices"
    stock_prices_df = yf.download(stock, period="5y")
    stock_prices_df.index = pd.to_datetime(stock_prices_df.index)
    stock_prices_df = stock_prices_df.loc[start_date:end_date]
    stock_prices_df.columns = stock_prices_df.columns.droplevel('Ticker')
    stock_prices_df.columns.name = None
    print(stock_prices_df)

    candle_plot(stock, stock_prices_df)


if __name__ == "__main__":
    main()


