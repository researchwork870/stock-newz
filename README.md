# Stock-Newz 📈

A comprehensive stock data collection and analysis tool for Indian markets, specifically designed to fetch financial data and share prices for NIFTY 500 companies.

## 🎯 Project Overview

Stock-Newz is a Python-based data ingestion system that automatically collects:
- **Financial Data**: Comprehensive financial metrics from Screener.in
- **Share Prices**: Historical price data using Yahoo Finance API
- **NIFTY 500 Coverage**: Complete dataset for all NIFTY 500 companies

## 🚀 Features

- **Automated Data Collection**: Batch processing of 500+ stock symbols
- **Dual Data Sources**: 
  - Screener.in for financial metrics
  - Yahoo Finance for price data
- **Robust Error Handling**: Retry logic and rate limiting
- **Comprehensive Logging**: Detailed logs with timestamps
- **Data Persistence**: Pickle format for efficient storage
- **Progress Tracking**: Real-time statistics and progress monitoring

## 📁 Project Structure

```
stock-newz/
├── src/
│   ├── data_ingestion.py    # Main data collection engine
│   ├── tickers.py           # NIFTY 500 symbol list
│   ├── helper.py            # Utility functions
│   └── logs/                # Log files directory
├── Data/
│   ├── share_prices/        # Historical price data
│   └── stock_financials/    # Financial metrics data
├── notebooks/
│   └── scraper.ipynb        # Jupyter notebook for analysis
├── newz-env/                # Python virtual environment
└── requirements.txt          # Python dependencies
```

## 🛠️ Installation

### Prerequisites
- Python 3.11+
- pip package manager

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd stock-newz
   ```

2. **Create virtual environment**
   ```bash
   python -m venv newz-env
   source newz-env/bin/activate  # On Windows: newz-env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 📦 Dependencies

The project uses the following key libraries:

- **requests**: HTTP requests for web scraping
- **bs4 (BeautifulSoup)**: HTML parsing
- **pandas**: Data manipulation and analysis
- **yfinance**: Yahoo Finance API integration
- **nltk**: Natural language processing
- **textblob**: Text analysis
- **lxml**: XML/HTML processing
- **tqdm**: Progress bars

## 🚀 Usage

### Basic Usage

Run the main data collection script:

```bash
python src/data_ingestion.py
```

### Programmatic Usage

```python
from src.data_ingestion import NIFTY500DataFetcher
from datetime import datetime

# Initialize the fetcher
fetcher = NIFTY500DataFetcher(log_level=logging.INFO)

# Start data collection
start_time = datetime.now().strftime('%Y%m%d_%H%M%S')
fetcher.ingest_data()
fetcher.save_data(start_time)
```

## 📊 Data Collection Process

### 1. Financial Data Collection
- **Source**: Screener.in
- **Method**: Web scraping with rotating user agents
- **Data**: Financial tables, ratios, and metrics
- **Rate Limiting**: 10-20 second delays between requests

### 2. Share Price Collection
- **Source**: Yahoo Finance API
- **Method**: yfinance library
- **Data**: 6 years of historical price data
- **Format**: OHLCV (Open, High, Low, Close, Volume)

### 3. Data Storage
- **Format**: Pickle files with timestamps
- **Location**: `Data/share_prices/` and `Data/stock_financials/`
- **Naming**: `YYYYMMDD_HHMMSS.pkl`

## 📈 Output Data

### Financial Data Structure
```python
{
    'SYMBOL': [
        {
            'header': 'Financial Ratios',
            'tables': [pandas.DataFrame, ...]
        },
        {
            'header': 'Profit & Loss',
            'tables': [pandas.DataFrame, ...]
        }
        # ... more sections
    ]
}
```

### Price Data Structure
```python
{
    'SYMBOL': pandas.DataFrame(
        columns=['Open', 'High', 'Low', 'Close', 'Volume'],
        index=DatetimeIndex
    )
}
```

## 🔧 Configuration

### Logging Levels
- `logging.DEBUG`: Detailed debugging information
- `logging.INFO`: General progress information (default)
- `logging.WARNING`: Only warnings and errors

### Rate Limiting
- **Financial Data**: 10-20 second delays between requests
- **Price Data**: No delays (API-based)
- **Progress Logging**: Every 10 symbols
- **Statistics Logging**: Every 50 symbols

## 📋 Statistics Tracking

The system tracks comprehensive statistics:
- Total symbols processed
- Successful/failed financial data fetches
- Successful/failed price data fetches
- Processing time and progress percentage

## 🛡️ Error Handling

- **Network Errors**: Automatic retry with exponential backoff
- **Rate Limiting**: Intelligent delays and user agent rotation
- **Data Validation**: Checks for empty responses and malformed data
- **Logging**: Detailed error logs with stack traces

## 📝 Logging

Logs are stored in `src/logs/` with timestamps:
- Console output for real-time monitoring
- File logs for detailed debugging
- Format: `nifty500_fetcher_YYYYMMDD_HHMMSS.log`

## 🔍 Data Analysis

Use the Jupyter notebook for data analysis:
```bash
jupyter lab notebooks/scraper.ipynb
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Important Notes

- **Rate Limiting**: Respect website terms of service
- **Data Freshness**: Run regularly for updated data
- **Storage**: Ensure sufficient disk space for data files
- **Network**: Stable internet connection required

## 🆘 Troubleshooting

### Common Issues

1. **Connection Errors**: Check internet connection and firewall settings
2. **Rate Limiting**: Increase delays between requests
3. **Memory Issues**: Process smaller batches of symbols
4. **Data Corruption**: Verify pickle file integrity

### Getting Help

- Check the logs in `src/logs/` for detailed error information
- Review the console output for real-time status
- Ensure all dependencies are properly installed

---

**Note**: This tool is for educational and research purposes. Always comply with the terms of service of data sources and respect rate limits. 