from create_datasets.DB_utils import *
import pdfplumber
import re

def split_text_into_chunks(text, chunk_size):
    enc = tiktoken.get_encoding("cl100k_base")

    # Tokenize the input text
    tokens = enc.encode(text)

    # Calculate the number of chunks
    num_chunks = (len(tokens) + chunk_size - 1) // chunk_size

    # Split tokens into chunks
    chunks = [
        enc.decode(tokens[i * chunk_size: (i + 1) * chunk_size])
        for i in range(num_chunks)
    ]
    return chunks


def filter_last_occurrences(items):
    """
    Given a dictionary of extracted items (with keys as the full item header),
    return a new dictionary containing only the last occurrence for each item number.

    The returned dictionary has item numbers as keys, and a tuple (full_key, content) as values.
    """
    filtered_items = {}

    # Iterate over the items in insertion order (Python 3.7+ preserves order)
    for full_key, content in items.items():
        # Extract the item number from the key using a regex.
        # This matches "Item " followed by one or more digits.
        match = re.match(r"item\s*(\d+)", full_key)
        if match:
            item_num = match.group(1)
            # Overwrite any previous occurrence for this item number.
            filtered_items[item_num] = (full_key, content)

    return filtered_items


def extract_items(pdf_path):
    # Open the PDF and extract text
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()]).lower()

    # Define a regex pattern for matching Q10 item headers
    item_pattern = r"(item\s\d+\.\s[^\n]+)"  # Matches "Item 1. Description"

    # Split the text into sections based on "Item X." headers
    sections = re.split(item_pattern, text)

    # Organize extracted items
    q10_items = {}
    for i in range(1, len(sections), 2):
        item_name = sections[i].strip()  # The item header (e.g., "Item 1. Financial Statements")
        item_content = sections[i + 1].strip()  # The corresponding text content
        q10_items[item_name] = item_content

    return [val[0] + '\n' + val[1] for val in filter_last_occurrences(q10_items).values()]


def create_literal_earnings_report_dataset(stock_ticker):
    """
    :param stock_ticker: A ticker of a stock
    The function creates a dataset for the sections of the given stock's literal earnings report sections
    and inserts the sections to the dataset
    """
    q10_sections = extract_items(f"create_datasets/q10_filings/Q10_{stock_ticker}.pdf")
    q10_chunks = [chunk for item in q10_sections for chunk in split_text_into_chunks(item, 1500)]

    # Create Qdrant dataset and insert News.
    create_dataset(f'Q10_{stock_ticker}')
    insert_dataset(f'Q10_{stock_ticker}', q10_chunks)

