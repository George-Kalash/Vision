from datetime import date
import re

# Check if required packages are installed

try: 
  import yahooquery as yq
  print("✓ yahooquery imported successfully")
except ImportError:
    print("✗ yahooquery not found. Install with: pip install yahooquery")
    exit(1)


try:
  import yfinance as yf
  print("✓ yfinance imported successfully")
except ImportError:
  print("✗ yfinance not found. Install with: pip install yfinance")
  exit(1)

try:
  from edgar import Company
  from edgar import *  
  from edgar.xbrl.xbrl import XBRL
  from edgar.xbrl import XBRLS
  from edgar.entity import public_companies
  print("✓ edgartools imported successfully")
except ImportError:
  print("✗ edgartools not found. Install with: pip install edgartools")
  exit(1)

try:
  import pandas as pd
  print("✓ pandas imported successfully")
except ImportError:
  print("✗ pandas not found. Install with: pip install pandas")
  exit(1)


SEC_UA = "your.email@example.com"  
set_identity(SEC_UA) 
  
class Enterprize: 
  def __init__ (self, ticker: str) -> None:
    self.ticker = ticker
    # Keep the company instance - it's expensive to recreate
    self.company = yf.Ticker(ticker)
    self.YQcompany = yq.Ticker(ticker, asynchronous=True)
    self.SECcompany = Company(ticker)
    # Get static info once during initialization
    self.name = self.company.info['shortName']
    self.market_cap = self.company.info['marketCap']
    self.industry = self.company.info["industry"]
    self.sector = self.company.info['sector']
    self.bid = self.company.info['bid']
    self.ask = self.company.info['ask']
  
  def __str__(self):
    """String representation of the object"""
    return f"""Company: {self.name} ({self.ticker})
    Market Cap: ${self.market_cap:,}
    Industry: {self.industry}
    Sector: {self.sector}
    Bid: ${self.bid}
    Ask: ${self.ask}"""
  
  def __repr__(self):
    """Developer representation of the object"""
    return f"Enterprize(ticker='{self.ticker}', name='{self.name}', market_cap={self.market_cap})"
    
  @property
  def liveQuote(self):
    """Get current price from most recent data (not websocket stream)"""
    try:
      fast_info = self.company.fast_info
      return fast_info.get('lastPrice', self.ask)
    except:
      return self.ask

  @property
  def getFilings(self):
    try: 
      filings = self.company.sec_filings
      return filings
    except:
      return 'Error: API connection'

  # getHistoricalData used yahooquery (yq) over yfinance (yf)
  @property
  def getHistoricalData(self): 
    pricesDF = self.YQcompany.history()
    return pricesDF
    
  @property
  def getCompanyFacts(self):
    return self.SECcompany.get_facts()
  
  @property
  def getFilings(self, filingType="10Q", periods=5, stmtType="IS"):

    if filingType not in ["10Q", "10K", "8K"]:
      return "Wrong filing type"
    match stmtType:
      case "IS":
        return self.getIncomeStatements(self, filingType, periods)
      case "BS":
        return self.getBalanceSheets()
  
  @property
  def getIncomeStatements(self, filingType="10Q", periods=5):
    return # fill in
  
  @property
  def getBalanceSheets(self, filingType="10Q", periods=5):
    return # fill in
  
  @property 
  def getCashFlowStatement(self, filingType="10Q", periods=5):
    return 
  
  

  
def __main__():
  company = Enterprize('U')
  print(company.getHistoricalData)
  print(company.SECcompany.balance_sheet().to_dataframe())
  
  
  
__main__()