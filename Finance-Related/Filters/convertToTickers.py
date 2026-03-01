import yfinance as yf
import re
from urllib.error import HTTPError

def is_valid_ticker(ticker):
    """
    Checks if a string is likely a valid ticker symbol.
    """
    pattern = r"^[A-Z0-9]{1,5}$"  # 1-5 uppercase letters or numbers
    return bool(re.match(pattern, ticker))

def get_ticker_symbol(company_name):
    """
    Converts a public company name to its ticker symbol using yfinance,
    with improved error handling and ticker validation.

    Args:
        company_name (str): The name of the company.

    Returns:
        str: The ticker symbol if found, otherwise None.
    """
    try:
        ticker = yf.Ticker(company_name)
        info = ticker.info

        if info and 'symbol' in info:
            symbol = info['symbol']
            if is_valid_ticker(symbol):
                return symbol
            else:
                print(f"Warning: Invalid ticker format: {symbol}")
                return None  # Flag as invalid

    except HTTPError as e:
        print(f"HTTPError for {company_name}: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error for {company_name}: {e}")
        return None

    return None  # Ticker not found

# Example usage:
company_name = "Apple"
ticker_symbol = get_ticker_symbol(company_name)

if ticker_symbol:
    print(f"The ticker symbol for {company_name} is {ticker_symbol}")
else:
    print(f"Could not find the ticker symbol for {company_name}")

company_name = "Microsoft"
ticker_symbol = get_ticker_symbol(company_name)

if ticker_symbol:
    print(f"The ticker symbol for {company_name} is {ticker_symbol}")
else:
    print(f"Could not find the ticker symbol for {company_name}")

company_name = "Random Company That Does Not Exist"
ticker_symbol = get_ticker_symbol(company_name)

if ticker_symbol:
    print(f"The ticker symbol for {company_name} is {ticker_symbol}")
else:
    print(f"Could not find the ticker symbol for {company_name}")