from datetime import date
from edgar import Company, set_identity

set_identity("Your Name your.email@example.com")  # SEC-friendly UA. :contentReference[oaicite:0]{index=0}

def xbrl_for_years(ticker: str, years_back: int = 3, forms=("10-K","10-Q")):
    company = Company(ticker)
    filings = company.get_filings(form=list(forms))            # company filings of chosen forms :contentReference[oaicite:1]{index=1}
    start_year = date.today().year - years_back + 1
    filings = filings.filter(date=f"{start_year}-01-01:{date.today():%Y-%m-%d}")  # date range filter :contentReference[oaicite:2]{index=2}

    for filing in filings:
        xb = filing.xbrl()                                     # parse XBRL for the filing (None if not present) :contentReference[oaicite:3]{index=3}
        if xb is None:
            continue
        yield filing, xb

# Example usage:
bs_df = None
for filing, xb in xbrl_for_years("AAPL", years_back=3, forms=("10-K","10-Q")):
    # Access common statements, or convert to DataFrame
    bs_df  = xb.statements.balance_sheet().to_dataframe()
    is_df  = xb.statements.income_statement().to_dataframe()
    cf_df  = xb.statements.cashflow_statement().to_dataframe()  # statements API → DataFrames :contentReference[oaicite:4]{index=4}