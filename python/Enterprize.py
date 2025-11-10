# companyProfile.py

from datetime import date
import re
from utilities import getStatementXBRL, smart_column_sort, stitch_by_concept_iterative

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
set_identity(SEC_UA) # type: ignore


# Implementations of the Enterprize class

class Enterprize: 
  def __init__ (self, ticker: str) -> None:
    self.ticker = ticker
    # Keep the company instance - it's expensive to recreate
    self.company = yf.Ticker(ticker)
    self.YQcompany = yq.Ticker(ticker, asynchronous=True)
    self.SECcompany = Company(ticker)
    # Get static info once during initialization and tolerate sparse datasets
    info = self.company.info or {}
    self.name = info.get('shortName', ticker.upper())
    self.market_cap = info.get('marketCap')
    self.industry = info.get("industry")
    self.sector = info.get('sector')
    self.bid = info.get('bid')
    self.ask = info.get('ask')
  
  def __str__(self):
    """String representation of the object"""
    market_cap = f"${self.market_cap:,}" if isinstance(self.market_cap, (int, float)) else "N/A"
    bid = f"${self.bid}" if isinstance(self.bid, (int, float)) else "N/A"
    ask = f"${self.ask}" if isinstance(self.ask, (int, float)) else "N/A"
    return f"""Company: {self.name} ({self.ticker})
    Market Cap: {market_cap}
    Industry: {self.industry or 'N/A'}
    Sector: {self.sector or 'N/A'}
    Bid: {bid}
    Ask: {ask}"""
  
  def __repr__(self):
    """Developer representation of the object"""
    return f"Enterprize(ticker='{self.ticker}', name='{self.name}', market_cap={self.market_cap})"
    
  @property
  def latestPrice(self):
    """Get current price from most recent data (not websocket stream)"""
    try:
      fast_info = self.company.fast_info
      return fast_info.get('lastPrice', self.ask)
    except:
      return self.ask

  # getHistoricalData used yahooquery (yq) over yfinance (yf)
  @property
  def getHistoricalData(self): 
    pricesDF = self.YQcompany.history()
    return pricesDF
    
  @property
  def getCompanyFacts(self):
    return self.SECcompany.get_facts()

  def getFilings(self: "Enterprize", *, filingType: str = "10-Q", periods: int = 5, stmtType: str = "IS") -> pd.DataFrame | None:

    if filingType not in ["10-Q", "10-K", "8-K"]:
      print("Wrong filing type")
      return None
    
    stmt: pd.DataFrame | None = None
    
    match stmtType:
      case "IS":
        stmt =  self.getIncomeStatements(filingType=filingType, periods=periods)
      case "BS":
        stmt = self.getBalanceSheets(filingType=filingType, periods=periods)
      case "CF":
        stmt = self.getCashFlowStatement(filingType=filingType, periods=periods)
    if stmt is None:
      return None
    return smart_column_sort(stmt)

  def getIncomeStatements(self, *, filingType: str = "10-K", periods: int = 5, year=date.today().year, shouldPrint: bool = False) -> pd.DataFrame | None:
    stmt_list = []
    
    for i in range(year - periods, year + 1):
      is_ = getStatementXBRL(self.ticker, filingType, "IS", year=i)
      if is_:
        is_df = is_.income_statement()
        if is_df is not None:
          stmt_list.append(is_df.to_dataframe())
          if shouldPrint:
            print(f"Added statement for year {i}")
    
    if not stmt_list:
      return None
    return stitch_by_concept_iterative(stmt_list)

  def getBalanceSheets(self, *, filingType: str = "10-K", periods: int = 5, year=date.today().year, shouldPrint: bool = False) -> pd.DataFrame | None:
    stmt_list = []
    
    for i in range(year - periods, year + 1):
      bs = getStatementXBRL(self.ticker, filingType, "BS", year=i)
      if bs:
        bs_df = bs.balance_sheet()
        if bs_df is not None:
          stmt_list.append(bs_df.to_dataframe())
          if shouldPrint:
            print(f"Added statement for year {i}")
    
    if not stmt_list:
      return None
    return stitch_by_concept_iterative(stmt_list)  # type: ignore
  
  def getCashFlowStatement(self, *, filingType: str = "10-K", periods: int = 5, year=date.today().year, shouldPrint: bool = False) -> pd.DataFrame | None:
    stmt_list = []
    
    for i in range(year - periods, year + 1):
      cf = getStatementXBRL(self.ticker, filingType, "CF", year=i)
      if cf:
        cf_df = cf.cashflow_statement()
        if cf_df is not None:
          stmt_list.append(cf_df.to_dataframe())
          if shouldPrint:
            print(f"Added statement for year {i}")
    
    if not stmt_list:
      return None
    return stitch_by_concept_iterative(stmt_list)  # type: ignore

