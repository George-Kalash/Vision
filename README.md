# Vision - Stock Analyzer

Vision is a comprehensive stock analysis toolkit that combines SEC EDGAR data, XBRL financial statements, and real-time market data from multiple sources. The project includes both Python and JavaScript implementations for retrieving and analyzing company financial information.

## Features

- **SEC EDGAR Data Access**: Retrieve official company filings (10-K, 10-Q) using the SEC EDGAR API
- **XBRL Financial Statements**: Parse and analyze structured financial data (Income Statements, Balance Sheets, Cash Flow Statements)
- **Real-time Market Data**: Fetch current stock prices and quotes using yfinance and TwelveData APIs
- **Company Profile Analysis**: Comprehensive company information including market cap, sector, industry data
- **Multi-Language Support**: Both Python and JavaScript implementations
- **Data Export**: Export financial data to CSV and JSON formats

## Project Structure

```
Vision/
├── python/           # Python implementation
│   ├── Enterprize.py        # Main class for company analysis
│   ├── utilities.py         # XBRL data retrieval utilities
│   ├── getFilingsEDGAR.py  # SEC filing retrieval
│   ├── example_usage.py    # Usage examples
│   ├── getPrice.py         # Real-time price data
│   ├── xbrlPull.py         # XBRL data extraction
│   ├── testGetStock.py     # Unit tests
│   └── requirements.txt    # Python dependencies
├── js/               # JavaScript implementation
│   ├── tryAccessSECAPI.js  # SEC API access example
│   ├── getStock.js         # Stock price fetching (browser)
│   ├── editablePricePull.js # Price data utilities
│   └── *.html              # Web interfaces
├── csv/              # Sample CSV data files
│   ├── quotes.csv
│   ├── sp500_top10_quotes.csv
│   └── top_20_NYSE_by_market_cap.csv
├── random/           # Utility scripts
│   ├── check_tickers.py    # Ticker validation
│   └── parsing.py          # Data parsing utilities
└── requirements.txt  # Root-level Python dependencies
```

## Setup & Usage

### Python Setup

1. **Create and activate a Python virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install required packages:**
   ```bash
   pip install -r requirements.txt
   # Or install from the python directory:
   pip install -r python/requirements.txt
   ```

   **Key Dependencies:**
   - `edgartools` - SEC EDGAR data access
   - `yfinance` - Yahoo Finance data
   - `yahooquery` - Alternative Yahoo Finance API
   - `pandas` - Data manipulation
   - `google-genai` - AI-powered analysis (optional)

3. **Set up environment variables:**
   
   Create a `.env` file or export environment variables:
   ```bash
   # SEC requires a User-Agent for API access
   export SEC_UA="Your Name your@email.com (YourApp/1.0)"
   # Or use EDGAR_IDENTITY
   export EDGAR_IDENTITY="Your Name your@email.com"
   ```

4. **Run Python scripts:**
   ```bash
   # Example: Fetch company data using the Enterprize class
   python3 python/example_usage.py
   
   # Get financial statements using XBRL
   python3 python/xbrlPull.py
   
   # Access SEC filings
   python3 python/getFilingsEDGAR.py AAPL
   
   # Run tests
   python3 python/testGetStock.py
   ```

### JavaScript Setup

1. **Prerequisites:**
   - Node.js (v14 or higher recommended)

2. **Set environment variable:**
   ```bash
   export SEC_UA="Your Name your@email.com (YourApp/1.0)"
   ```

3. **Run JavaScript scripts:**
   ```bash
   # Access SEC API
   node js/tryAccessSECAPI.js
   
   # For browser-based scripts, open the HTML files:
   # - js/home.html
   # - js/webload.html
   ```

## Usage Examples

### Python: Using the Enterprize Class

```python
from Enterprize import Enterprize

# Create a company instance
company = Enterprize('AAPL')

# Get company information
print(company)  # Displays name, market cap, sector, etc.
print(f"Latest Price: ${company.latestPrice}")

# Retrieve financial statements
income_stmt = company.getFilings(filingType="10-K", stmtType="IS", periods=10)
balance_sheet = company.getFilings(filingType="10-K", stmtType="BS", periods=10)
cashflow = company.getFilings(filingType="10-K", stmtType="CF", periods=10)
```

### Python: XBRL Data Extraction

```python
from utilities import getStatementXBRL

# Get latest 10-K income statement
stmt = getStatementXBRL(ticker="MSFT", form="10-K", statement="IS")

# Get quarterly data
stmt = getStatementXBRL(ticker="AAPL", form="10-Q", statement="IS", 
                         year=2024, quarter=3)
```

### JavaScript: SEC API Access

```javascript
// Set your User-Agent
const ua = process.env.SEC_UA;

// Fetch company facts from SEC
const url = 'https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json';
const response = await fetch(url, {
  headers: { 'User-Agent': ua }
});
const data = await response.json();
```

## Key Components

### Enterprize Class (`python/Enterprize.py`)
The main Python class for comprehensive company analysis:
- Integrates yfinance, yahooquery, and SEC EDGAR data
- Provides unified access to market data and financial statements
- Supports multiple statement types (IS, BS, CF)
- Includes historical data retrieval

### Utilities (`python/utilities.py`)
Core functions for XBRL data processing:
- `getStatementXBRL()` - Retrieve financial statements from SEC filings
- `listRecentFilings()` - List recent company filings
- Date filtering and quarter-based retrieval

## Data Sources

- **SEC EDGAR**: Official company filings and financial statements
- **Yahoo Finance**: Real-time market data and company information
- **TwelveData API**: Alternative market data source (JavaScript)

## Development Status

This project is actively under development. Some features may be experimental or subject to change. Please report any issues or contribute improvements via GitHub.

## License

MIT License - See LICENSE file for details.

## Contributing

Contributions are welcome! Please ensure:
- Code follows existing style conventions
- Tests are included for new features
- Documentation is updated accordingly

## Notes

- Always comply with SEC API guidelines (provide proper User-Agent)
- Be mindful of API rate limits for external data sources
- Some features require API keys (e.g., TwelveData for JavaScript examples)
