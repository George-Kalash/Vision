# companyProfile.py

from datetime import date
import re
from utilities import getStatementXBRL

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

def stitchStatements(stmts: list) -> pd.DataFrame | None:
  if not stmts:
    return None
  stmts_df = pd.concat(stmts, ignore_index=True)
  return stmts_df

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

  def getFilings(self: "Enterprize", *, filingType: str = "10-Q", periods: int = 5, stmtType: str = "IS") -> list | str | None:

    if filingType not in ["10-Q", "10-K", "8-K"]:
      print("Wrong filing type")
      return None
    stmt = None
    match stmtType:
      case "IS":
        stmt = self.getIncomeStatements(filingType=filingType, periods=periods)
      case "BS":
        stmt = self.getBalanceSheets(filingType=filingType, periods=periods)
      case "CF":
        stmt = self.getCashFlowStatement(filingType=filingType, periods=periods)
    return stitchStatements(stmt) # type: ignore
  
  def getIncomeStatements(self, *, filingType: str = "10-K", periods: int = 5, shouldPrint: bool = False) -> list | None:
    is_list = []
    for i in range(date.today().year - periods, date.today().year + 1):
      is_ = getStatementXBRL(self.ticker, filingType, "IS", year=i)
      is_ = is_.income_statement() if is_ else None
      if is_:
        is_list.append(is_.to_dataframe())
        if shouldPrint:
          print(is_)
    if is_list:
      return is_list  
    return None
  
  def getBalanceSheets(self, *, filingType: str = "10-K", periods: int = 5, shouldPrint: bool = False) -> list | None:
    bs_list = []
    for i in range(date.today().year - periods, date.today().year + 1):
      bs = getStatementXBRL(self.ticker, filingType, "BS", year=i)
      bs = bs.balance_sheet() if bs else None
      if bs:
        bs_list.append(bs.to_dataframe())
        if shouldPrint:
          print(bs)
    if bs_list:
      return bs_list  
    return None

  def getCashFlowStatement(self, *, filingType: str = "10-K", periods: int = 5, shouldPrint: bool = False) -> list | None:
    cf_list = []
    for i in range(date.today().year - periods, date.today().year + 1):
      cf = getStatementXBRL(self.ticker, filingType, "CF", year=i)
      cf = cf.cashflow_statement() if cf else None
      if cf:
        cf_list.append(cf.to_dataframe())
        if shouldPrint:
          print(cf)
    if cf_list:
      return cf_list
    return None



def __main__():
  company = Enterprize('MSFT')
  stmt = company.getFilings(filingType="10-K", stmtType="IS")

  print(stmt)
  
  
__main__()