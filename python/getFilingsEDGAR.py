import os, requests
import sys
import json
from pathlib import Path
from edgar import Company
import pandas as pd
from edgar import *  
from edgar.xbrl.xbrl import XBRL
from edgar.xbrl import XBRLS
from edgar.entity import public_companies


set_identity("scccbf@gmail.com") 
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

def getIncomeStatementXBRL(c="AAPL", whichType="XBRL"):
    co = Company(c)
    filings = co.get_filings(form="10-K").head(6)
    xbrls = XBRLS.from_filings(filings)
    stitched = xbrls.statements
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
    
    # Fill any remaining NaN values with a placeholder
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
    print(getIncomeStatement(c="AAPL", periods=10, form="10-K"))
    # print(getIncomeStatementXBRL("AAPL", whichType=" "))

__main__()


# print(companyFacts.entity_info())


# fin = co.get_financials()

# print(fin.income_statement())


# df = fin.income_statement().to_dataframe()
# bs = fin.balance_sheet().to_dataframe()
# # print(df)
# if not df.empty:
#     # Use the 'concept' column for a more reliable match
#     revenue = df[df["concept"] == "us-gaap_Revenues"]
#     if revenue.empty:
#         revenue = df[df["concept"] == "us-gaap_RevenueFromContractWithCustomerExcludingAssessedTax"]
#     row = df[df["concept"] == "us-gaap_NetIncomeLoss" ]
#     row2 = bs[bs["concept"] == "us-gaap_StockholdersEquity"]
#     print(row2)
#     if not row.empty:
#         # latest period is typically the last column
#         revenue = revenue.iloc[0, 2]
#         net_income = row.iloc[0, 2]
#         stockholder_equity = row2.iloc[0, 2]
#         print(f"Revenue: {revenue:,.0f}")
#         print(f"Net Income: {net_income}")
#         print(f"Stockholder Equity: {stockholder_equity}")
#     else:
#         print("Net income not found in the income statement.")
#         # If you want to see the whole dataframe when net income is not found
#         # print(df)
# else:
#     print("Failed to retrieve income statement. The DataFrame is empty.")

# print(dir(income_statement))
# print(vars(Company))
# print(co.industry)
# [ 'balance_sheet', 'business_address', 'cash_flow', 'cik', 'data', 'display_name', 
#  'facts', 'fiscal_year_end', 'get_exchanges', 'get_facts', 'get_filings', 'get_financials', 'get_icon', 'get_quarterly_financials', 'get_structured_statement', 
#  'get_ticker', 'income_statement', 'industry', 'is_company', 'is_individual', 'latest', 'latest_tenk', 'latest_tenq', 'mailing_address', 'name', 'not_found', 
#  'public_float', 'shares_outstanding', 'sic', 'tickers']
# print(balance_sheet._calculate_balance_sheet_ratios())
# if __name__ == '__main__':
#     c = Company("NVDA")
#     ticker = c.get_ticker()
#     filings = c.get_filings(form="10-K")
#     ticker = c.tickers
#     print(filings)
#     print(c.data.mailing_address)
#     print(c)
#     print(ticker[0])
# print(f"Revenue: ${revenue:,.0f}, Net Income: ${net_income:,.0f}")

# financials = company.get_financials()
# filings = get_filings()

# IS = company.income_statement()
# BS = company.balance_sheet()
# # CFS = company.cash_flow_statement()
# if IS and BS is not None:
#     print(IS)
#     print(BS)
#     # print(CFS)
# # print(financials)
# print(f"Shares Outstanding: {232.14*company.shares_outstanding:,.0f}")