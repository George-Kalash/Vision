import json
import pandas as pd
from edgar import Company, set_identity
from edgar.xbrl.xbrl import XBRL
from edgar.xbrl import XBRLS

# Set your identity for the SEC EDGAR API
set_identity("scccbf@gmail.com")

def check_company_data(company_ticker: str, company_name: str, line: int = 1):
    """
    Checks if the first line of the income statement can be pulled for a company.
    """
    try:
        # Find the company by name
        company = Company(company_ticker)
        if not company:
            # print(f"Could not find company: {company_name}")
            return

        # Get the latest 10-Q filing
        filing = company.latest("10-K")
        xbrl = XBRL.from_filing(filing)
        statements = xbrl.statements
        if not filing:
            print(f"No 10-Q filing found for {company_ticker}")
            return

        # Get the income statement DataFrame
        income_statement = statements.income_statement().to_dataframe().loc[0]

        # Check if the DataFrame is valid and has data
        if not income_statement.empty and len(income_statement) > 0:
            # print(f"✅ Successfully pulled first line for: {company_name}")
            print(income_statement, " ", company_ticker) # Uncomment to see the first line
            return
        else:
            # print(f"{line}: ❌ Failed to pull data or DataFrame is empty for: {company_ticker}, {company_name}")
            return False

    except Exception as e:
        # print(f"{line}: ❌ An error occurred for {company_ticker}, {company_name}: {e}")
        return False

if __name__ == "__main__":
    # Load the JSON file with company names
    with open("../random/ticker_to_cik.json", "r") as f:
        data = json.load(f)

    # Loop through each company in the JSON file
    i = 1
    for index, company_info in data.items():
      
        company_ticker = company_info.get("ticker")
        company_name = company_info.get("title")
        if company_ticker:
          if check_company_data(company_ticker, company_name, i) == False:
              i += 1