from edgar import *  
from edgar.xbrl.xbrl import XBRL
from datetime import date
import os

from dotenv import load_dotenv
load_dotenv()

set_identity(os.getenv("EDGAR_IDENTITY", "Your Name your.email@example.com"))
__all__ = ['getStatementXBRL', 'listRecentFilings']
def _quarter_bounds(year: int, quarter: int) -> tuple[str, str]:
    if quarter not in (1, 2, 3, 4):
        raise ValueError("quarter must be 1..4")
    starts = {1: (1, 1), 2: (4, 1), 3: (7, 1), 4: (10, 1)}
    ends   = {1: (3, 31), 2: (6, 30), 3: (9, 30), 4: (12, 31)}
    s = date(year, *starts[quarter]).strftime("%Y-%m-%d")
    e = date(year, *ends[quarter]).strftime("%Y-%m-%d")
    return s, e

def listRecentFilings(ticker: str = "AAPL", form: str = "10-Q", count: int = 5):
    co = Company(ticker)
    filings = co.get_filings(form=form, is_xbrl=True).head(count)
    print(f"Recent {form} filings for {ticker}:")
    for filing in filings:
        print(f"  - {filing.filing_date}: {filing.form} - {filing.accession_number}")
    return filings

def getStatementXBRL(ticker: str = "AAPL", form: str = "10-K", statement: str = "IS", *,
        year: int | None = None, quarter: int | None = None): 
    # reeturns the statements obj
    #statement = IS - income stmt, CF - cashflow stmt, BS - balance sheet
    
    co = Company(ticker)
    filings = co.get_filings(form=form, is_xbrl=True) 
    
    # If no year/quarter specified, get the latest filing
    if year is None and quarter is None:
        filing = filings.latest()
    elif year is not None and quarter is None:
        date_filter = f"{year}-01-01:{year}-12-31"
        filings = filings.filter(date=date_filter)
        filing = filings.latest()
    elif year is not None and quarter is not None:
        start, end = _quarter_bounds(year, quarter)
        filings = filings.filter(date=f"{start}:{end}")
        filing = filings.latest()
    else:
        filing = filings.latest()
    
    if not filing:
        return None
    
    xb = filing.xbrl() 
    if not xb:
        return None
    return xb.statements

