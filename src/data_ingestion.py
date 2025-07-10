import logging
import json
import time
import random
import re
import pandas as pd
import pickle
import requests
import yfinance as yf
from requests.exceptions import RequestException
from tickers import symbol_list
from datetime import datetime
import os

import warnings
warnings.filterwarnings("ignore")

# Configure logging
def setup_logging(log_level=logging.INFO):
    """Set up logging configuration with both file and console handlers"""
    
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    # Create logger
    logger = logging.getLogger('NIFTY500DataFetcher')
    logger.setLevel(log_level)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    file_handler = logging.FileHandler(f'{log_dir}/nifty500_fetcher_{timestamp}.log')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger

class NIFTY500DataFetcher:
    def __init__(self, log_level=logging.INFO):
        self.logger = setup_logging(log_level)
        self.stock_financials = {}
        self.share_prices = {}
        self.nifty500_symbols = symbol_list  # Assuming this is defined elsewhere
        
        # Statistics tracking
        self.stats = {
            'total_symbols': len(self.nifty500_symbols),
            'successful_financials': 0,
            'failed_financials': 0,
            'successful_prices': 0,
            'failed_prices': 0,
            'start_time': None,
            'end_time': None
        }
        
        self.logger.info(f"Initialized NIFTY500DataFetcher with {self.stats['total_symbols']} symbols")

    def get_stock_financials(self, symbol):
        """Fetch financial data for a given stock symbol"""
        self.logger.debug(f"Starting financial data fetch for symbol: {symbol}")
        
        url = f"https://www.screener.in/company/{symbol}/consolidated/"
        
        USER_AGENTS = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:112.0) Gecko/20100101 Firefox/112.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.0.0",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_4_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (iPad; CPU OS 16_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Mobile/15E148 Safari/604.1",
            "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.196 Mobile Safari/537.36"
        ]

        # Choose a random user agent to avoid being blocked
        selected_agent = random.choice(USER_AGENTS)
        headers = {'User-Agent': selected_agent}
        
        self.logger.debug(f"Using User-Agent: {selected_agent[:50]}...")
        self.logger.debug(f"Requesting URL: {url}")

        try:
            response = self.safe_request(url, headers)
            if response is None:
                self.logger.error(f"Failed to get response for {symbol}")
                self.stats['failed_financials'] += 1
                return
                
            text = response.text
            self.logger.debug(f"Received response with {len(text)} characters for {symbol}")
            
        except Exception as e:
            self.logger.error(f"Exception while fetching financials for {symbol}: {e}", exc_info=True)
            self.stats['failed_financials'] += 1
            return

        try:
            # Extract all <h2> headers
            h2_section_pattern = re.compile(r'(<h2[^>]*>(.*?)</h2>)(.*?)(?=<h2[^>]*>|$)', re.DOTALL)
            matches = h2_section_pattern.findall(text)
            
            self.logger.debug(f"Found {len(matches)} sections for {symbol}")
            
            # Extract all blocks inside each header as strings
            sections = []
            for i, (full_tag, header_text, content) in enumerate(matches, 1):
                clean_header = re.sub(r'<.*?>', '', header_text).strip()
                
                # Extract list of <table> blocks inside the section
                html_tables = re.findall(r'<table.*?>.*?</table>', content, re.DOTALL)
                
                self.logger.debug(f"Section '{clean_header}' has {len(html_tables)} tables")
                
                # Read html tables into pandas dataframes
                df_tables_ls = []
                if len(html_tables) > 0:
                    for j, table in enumerate(html_tables):
                        try:
                            parsed_tables = pd.read_html(table)
                            if len(parsed_tables) > 0:
                                df_tables_ls.append(parsed_tables[0])
                                self.logger.debug(f"Successfully parsed table {j+1} in section '{clean_header}'")
                        except Exception as e:
                            self.logger.warning(f"Failed to parse table {j+1} in section '{clean_header}': {e}")

                sections.append({
                    "header": clean_header,
                    "tables": df_tables_ls
                })
            
            self.stock_financials[symbol] = sections
            self.stats['successful_financials'] += 1
            self.logger.info(f"Successfully fetched financial data for {symbol} with {len(sections)} sections")
            
        except Exception as e:
            self.logger.error(f"Error processing financial data for {symbol}: {e}", exc_info=True)
            self.stats['failed_financials'] += 1
    
    def safe_request(self, url, headers, max_retries=3):
        """Make a safe HTTP request with retry logic"""
        self.logger.debug(f"Making request to {url} with {max_retries} max retries")
        
        for attempt in range(max_retries):
            try:
                self.logger.debug(f"Attempt {attempt + 1} for {url}")
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    self.logger.debug(f"Successful request to {url} on attempt {attempt + 1}")
                    return response
                elif response.status_code in (429, 503):
                    wait = random.uniform(10, 20)
                    self.logger.warning(f"Rate limit hit (status {response.status_code}). Sleeping for {wait:.1f} seconds...")
                    time.sleep(wait)
                else:
                    self.logger.error(f"Unexpected status code {response.status_code} for {url}")
                    break
                    
            except RequestException as e:
                self.logger.error(f"RequestException on attempt {attempt + 1} for {url}: {e}")
                if attempt < max_retries - 1:
                    wait = random.uniform(5, 10)
                    self.logger.info(f"Retrying in {wait:.1f} seconds...")
                    time.sleep(wait)
                else:
                    self.logger.error(f"Max retries exceeded for {url}")
                    return None
        
        return None
        
    def get_share_prices(self, symbol):
        """Fetch current share prices using yfinance"""
        self.logger.debug(f"Starting share price fetch for symbol: {symbol}")
        
        try:
            # Add .NS suffix for NSE symbols
            ticker = f"{symbol}.NS"
            self.logger.debug(f"Using ticker: {ticker}")
            
            stock = yf.Ticker(ticker)
            
            # Get current price and basic info
            info = stock.info
            hist = stock.history(period="2190d")
            
            if not hist.empty:
                self.share_prices[symbol] = hist
                self.stats['successful_prices'] += 1
                self.logger.info(f"Successfully fetched share prices for {symbol} - {len(hist)} days of data")
            else:
                self.stats['failed_prices'] += 1
                self.logger.warning(f"No historical data found for {symbol}")
                
        except Exception as e:
            self.stats['failed_prices'] += 1
            self.logger.error(f"Error fetching share prices for {symbol}: {e}", exc_info=True)

    def ingest_data(self):
        """Main method to ingest data for all symbols"""
        self.logger.info("Starting data ingestion process")
        self.stats['start_time'] = datetime.now()
        
        total_symbols = len(self.nifty500_symbols)
        
        for index, symbol in enumerate(self.nifty500_symbols, 1):
            self.logger.info(f"Processing symbol {index}/{total_symbols}: {symbol}")
            
            # Fetch financial data
            self.get_stock_financials(symbol)
            
            # Fetch share prices
            self.get_share_prices(symbol)
            
            # Progress logging
            if index % 10 == 0:
                self._log_progress(index, total_symbols)
                wait_time = random.uniform(10, 20)
                self.logger.info(f"Rate limiting: sleeping for {wait_time:.1f} seconds")
                time.sleep(wait_time)
            
            # Log current statistics
            if index % 50 == 0:
                self._log_statistics()
        
        self.stats['end_time'] = datetime.now()
        self.logger.info("Data ingestion process completed")
        self._log_final_statistics()
    
    def _log_progress(self, current, total):
        """Log progress information"""
        percentage = (current / total) * 100
        elapsed = datetime.now() - self.stats['start_time']
        
        self.logger.info(f"Progress: {current}/{total} ({percentage:.1f}%) - Elapsed: {elapsed}")
    
    def _log_statistics(self):
        """Log current statistics"""
        self.logger.info(f"Current Statistics:")
        self.logger.info(f"  Successful financials: {self.stats['successful_financials']}")
        self.logger.info(f"  Failed financials: {self.stats['failed_financials']}")
        self.logger.info(f"  Successful prices: {self.stats['successful_prices']}")
        self.logger.info(f"  Failed prices: {self.stats['failed_prices']}")
    
    def _log_final_statistics(self):
        """Log final statistics"""
        duration = self.stats['end_time'] - self.stats['start_time']
        
        self.logger.info("=" * 60)
        self.logger.info("FINAL STATISTICS")
        self.logger.info("=" * 60)
        self.logger.info(f"Total symbols processed: {self.stats['total_symbols']}")
        self.logger.info(f"Successful financials: {self.stats['successful_financials']}")
        self.logger.info(f"Failed financials: {self.stats['failed_financials']}")
        self.logger.info(f"Successful prices: {self.stats['successful_prices']}")
        self.logger.info(f"Failed prices: {self.stats['failed_prices']}")
        self.logger.info(f"Total duration: {duration}")
        self.logger.info(f"Average time per symbol: {duration / self.stats['total_symbols']}")
        
        # Calculate success rates
        financial_success_rate = (self.stats['successful_financials'] / self.stats['total_symbols']) * 100
        price_success_rate = (self.stats['successful_prices'] / self.stats['total_symbols']) * 100
        
        self.logger.info(f"Financial data success rate: {financial_success_rate:.1f}%")
        self.logger.info(f"Price data success rate: {price_success_rate:.1f}%")
        self.logger.info("=" * 60)
                
    def save_data(self, start_time):
        """Save collected data to JSON files"""
        self.logger.info("Starting data save process")
        
        # Ensure directories exist
        financials_dir = "/Users/agrimrustagi/Desktop/Projects/stock-newz/Data/stock_financials"
        prices_dir = "/Users/agrimrustagi/Desktop/Projects/stock-newz/Data/share_prices"
        
        for directory in [financials_dir, prices_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
                self.logger.info(f"Created directory: {directory}")

        stock_financials_path = f"{financials_dir}/{start_time}.pkl"
        share_prices_path = f"{prices_dir}/{start_time}.pkl"

        try:
            # Save financial data
            with open(stock_financials_path, 'wb') as f:
                pickle.dump(self.stock_financials, f)
            
            self.logger.info(f"Successfully saved financial data to {stock_financials_path}")
            self.logger.info(f"Financial data contains {len(self.stock_financials)} symbols")
            
            # Save price data
            with open(share_prices_path, 'wb') as f:
                pickle.dump(self.share_prices, f)
            
            self.logger.info(f"Successfully saved price data to {share_prices_path}")
            self.logger.info(f"Price data contains {len(self.share_prices)} symbols")
            
        except Exception as e:
            self.logger.error(f"Error saving data: {e}", exc_info=True)
            raise

# Example usage
if __name__ == "__main__":
    # You can adjust log level as needed
    fetcher = NIFTY500DataFetcher(log_level=logging.INFO)
    
    # Start the ingestion process
    start_time = datetime.now().strftime('%Y%m%d_%H%M%S')
    fetcher.ingest_data()
    fetcher.save_data(start_time)