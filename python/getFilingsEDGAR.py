import os, requests
from datetime import date
import sys
import re
import json
from pathlib import Path
from edgar import Company
import pandas as pd
from edgar import *  
from edgar.xbrl.xbrl import XBRL
from edgar.xbrl import XBRLS
from edgar.entity import public_companies


set_identity("youremail@somemail.com") 
print("EdgarTools installed successfully!")


# ADGENDA:
# 0. organize files by type <- DONE
# 1. create method to retrieve specific financial data get_latest_financial_data(ticker="AAPL", statement_type="10-K") -> pd.DataFrame ie net income, stockholder equity ... <- Done
# 1.2. Extract relevant data from the income statement, balance sheet, cash flow statements.




ticker = sys.argv[1] if len(sys.argv) > 1 else "AAPL"

company = Company('AAPL')
filing = company.latest("10-K")

# Parse XBRL data
xbrl = XBRL.from_filing(filing)
co = Company(ticker)


def _quarter_bounds(year: int, quarter: int) -> tuple[str, str]:
    if quarter not in (1, 2, 3, 4):
        raise ValueError("quarter must be 1..4")
    starts = {1: (1, 1), 2: (4, 1), 3: (7, 1), 4: (10, 1)}
    ends   = {1: (3, 31), 2: (6, 30), 3: (9, 30), 4: (12, 31)}
    s = date(year, *starts[quarter]).strftime("%Y-%m-%d")
    e = date(year, *ends[quarter]).strftime("%Y-%m-%d")
    return s, e

def getIncomeStatementXBRL(ticker: str = "AAPL", form: str = "10-K", *, year: int | None = None, quarter: int | None = None,):
    co = Company(ticker)
    filings = co.get_filings(form=form, is_xbrl=True) 
    # filing = co.latest(form)
    
    if year is not None and quarter is None:
        date_filter = f"{year}-01-01:{year}-12-31"
        filings = filings.filter(date=date_filter)
        
    elif year is not None and quarter is not None:
        start, end = _quarter_bounds(year, quarter)
        filings = filings.filter(date=f"{start}:{end}")
    
    filing = filings.latest()          
    if not filing:
        return None
    
    xb = filing.xbrl()
    if not xb:
        return None
    return xb.statements.income_statement().to_dataframe()
    # income_trend = stitched.income_statement(max_periods=8)

def getCompanyFacts(c="AAPL"):
    return co.get_facts()

def getIndustry(c="AAPL"):
    co = Company(c)
    if not co.is_company: 
        print(f"Company with ticker {ticker} not found.")
        return pd.DataFrame()
    return co.industry

def getIncomeStatement(c="AAPL", periods=1, form="10-K"):   
    co = Company(c)
    if not co.is_company: 
        print(f"Company with ticker {ticker} not found.")
        return pd.DataFrame()
    filings = co.get_filings(form=form).head(periods) 
    xbrls = XBRLS.from_filings(filings)
    try:
        return xbrls.statements.income_statement().to_dataframe()
    except Exception as e:
        print(f"Error retrieving income statement for {c}: {e}")
        return pd.DataFrame()

def getBalanceSheet(c="AAPL", periods=1, form="10-K"):
    co = Company(c)
    if not co.is_company: 
        print(f"Company with ticker {ticker} not found.")
        return pd.DataFrame()
    filings = co.get_filings(form=form).head(periods) 
    xbrls = XBRLS.from_filings(filings)
    try:
        return xbrls.statements.balance_sheet().to_dataframe()
    except Exception as e:
        print(f"Error retrieving balance sheet for {c}: {e}")
        return pd.DataFrame()

def getCashFlowStatement(c="AAPL", periods=1, form="10-K"): 
    co = Company(c)
    if not co.is_company: 
        print(f"Company with ticker {ticker} not found.")
        return pd.DataFrame()
    filings = co.get_filings(form=form).head(periods) 
    xbrls = XBRLS.from_filings(filings)

    try:
        return xbrls.statements.cashflow_statement().to_dataframe()
    except Exception as e:
        print(f"Error retrieving cash flow statement for {c}: {e}")
        return pd.DataFrame()

def getLatestFinancialData(c="AAPL", periods=1, form="10-K") -> object:
    income_statement = getIncomeStatement(c, periods, form)
    balance_sheet = getBalanceSheet(c, periods, form)
    cash_flow_statement = getCashFlowStatement(c, periods, form)

    # Combine all data into a single DataFrame
    financial_data = {
        "Income Statement": income_statement,
        "Balance Sheet": balance_sheet,
        "Cash Flow Statement": cash_flow_statement
    }
    return financial_data

def toCSV(data: pd.DataFrame, filename: str):
    # Create a copy to avoid modifying the original DataFrame while iterating
    cleaned_data = data.copy()

    # Iterate over each cell in the DataFrame
    for index, row in cleaned_data.iterrows():
        for col in cleaned_data.columns:
            cell = cleaned_data.at[index, col]
            if isinstance(cell, (int, float)):
                # Check if the absolute value is large enough to be converted
                if abs(cell) > 1_000_000:
                    # Update the value in the DataFrame
                    cleaned_data.at[index, col] = cell / 1_000_000
    
    cleaned_data.fillna("-")
    
    # Save the modified DataFrame to a CSV file
    cleaned_data.to_csv(filename, index=False)

def __main__():
    print("initializing main")
    # dropconcept = getLatestFinancialData(ticker, periods=11, form="10-K")["Balance Sheet"].drop("concept", axis=1)
    # toCSV(dropconcept, f"{ticker}_financials.csv")
    # available_periods = xbrl.reporting_periods
    # print(available_periods)
    # print(dropconcept)
    # print(getIncomeStatement(c="AAPL", periods=10, form="10-K"))
    word = "Revenue"
    col = "label"

    for i in range(0, 10):
        year = 2025 - i
        df = getIncomeStatementXBRL(year=year)

        if df is None or df.empty:
            print(f"{year}: no data")
            continue

        if col not in df.columns:
            print(f"{year}: column '{col}' not found; available: {list(df.columns)}")
            continue

        mask_has_word = df[col].astype(str).str.contains(
            rf"(?i)\b{re.escape(word)}\b", na=False
        )
        # migh use "mask_not_only" in the future if "mask_has_word" does not yeild results
        mask_not_only = ~df[col].astype(str).str.fullmatch( 
            rf"(?i)\s*{re.escape(word)}\s*", na=False
        )

        mask = mask_has_word

        row = df.loc[mask]
        print(f"{year}:\n{row}\n")

__main__()

