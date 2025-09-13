import os, requests
import time
from datetime import date
import edgar
from edgar import get_filings
print("EdgarTools installed successfully!")
company = edgar.Company("AAPL")
financials = company.get_financials()
filings = get_filings()
# for i in range(0,10):
#     print(filings[i])  
IC = company.income_statement()
if IC is not None:
    print( IC)
# print(financials)
print(f"Shares Outstanding: {company.shares_outstanding:,.0f}")

SEC_UA = os.getenv("SEC_UA", "Your Name your@email.com (VisionApp/0.1)")
CIK10 = "0000320193"  # Apple

SEC_UA = os.getenv("SEC_UA", "Your Name your@email (VisionApp/0.1)")
HEADERS = {"User-Agent": SEC_UA, "Accept-Encoding": "gzip, deflate"}

TICKER_MAP_URL = "https://www.sec.gov/files/company_tickers.json"
COMPANY_FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010}.json"



# US-GAAP tags to try (in priority order)
TAGS = {
    "revenue": [
        "RevenueFromContractWithCustomerExcludingAssessedTax",
        "Revenues",
        "SalesRevenueNet"
    ],
    "sales": [
        "SalesRevenueNet",
        "Revenues",
        "RevenueFromContractWithCustomerExcludingAssessedTax"
    ],
    "gross_income": [
        "GrossProfit"
    ],
    "net_income": [
        "NetIncomeLoss"
    ],
}


def getReports(companyCIK, reports, num):
    s = requests.Session()
    s.headers.update({"User-Agent": SEC_UA, "Accept-Encoding": "gzip, deflate"})

    subs = s.get(f"https://data.sec.gov/submissions/CIK{companyCIK}.json", timeout=30).json()
    recent = subs["filings"]["recent"]

    out = []
    for form, acc, prim in zip(recent["form"], recent["accessionNumber"], recent["primaryDocument"]):
        if form in (reports):
            cik_nolead = str(int(companyCIK))  # drop leading zeros for the path
            acc_nodash = acc.replace("-", "")
            url = f"https://www.sec.gov/Archives/edgar/data/{cik_nolead}/{acc_nodash}/{prim}"
            out.append((form, acc, url))

    for row in out[:num]:
        print(row)

def get_json(url, params=None, sleep=0.2):
    """GET JSON with fair-access friendly pause."""
    r = requests.get(url, headers=HEADERS, params=params, timeout=30)
    r.raise_for_status()
    if sleep: time.sleep(sleep)
    return r.json()

def ticker_to_cik(ticker: str) -> str:
    """
    Resolve ticker -> 10-digit zero-padded CIK using SEC's mapping.
    """
    mapping = get_json(TICKER_MAP_URL)
    # mapping is { "0": {"ticker":"A","cik_str":320193,"title":"..."} , ... }
    t = ticker.upper()
    for _, row in mapping.items():
        if row.get("ticker", "").upper() == t:
            return f"{int(row['cik_str']):010d}"
    raise ValueError(f"Ticker not found in SEC map: {ticker}")

def latest_usd_duration_value(fact_obj: dict):
    """
    From a Company Facts 'fact' object, pick the most recent USD duration value.
    """
    if not fact_obj:
        return None
    units = fact_obj.get("units", {})
    # prefer USD (duration values like FY or Q)
    for unit_key in ("USD", "USD/shares"):
        facts = units.get(unit_key, [])
        # filter to duration contexts (have end & start)
        dur = [f for f in facts if "end" in f and "start" in f]
        if not dur:
            continue
        # choose latest by end date, then most recently filed
        dur.sort(key=lambda x: (x.get("end", ""), x.get("filed", "")), reverse=True)
        val = dur[0].get("val")
        if isinstance(val, (int, float)):
            return val
        try:
            return float(val)
        except Exception:
            continue
    return None

def extract_metrics_from_companyfacts(companyfacts: dict) -> dict:
    """
    Try a set of US-GAAP tags for each metric and return the first that yields a value.
    """
    usgaap = companyfacts.get("facts", {}).get("us-gaap", {})
    out = {}
    for key, candidates in TAGS.items():
        value = None
        for tag in candidates:
            value = latest_usd_duration_value(usgaap.get(tag))
            if value is not None:
                break
        out[key] = value
    return out

def print_income_statement(ticker_or_cik: str):
    # accept ticker (e.g., AAPL) or already-zero-padded CIK
    if ticker_or_cik.isdigit():
        cik = f"{int(ticker_or_cik):010d}"
    else:
        cik = ticker_to_cik(ticker_or_cik)

    facts = get_json(COMPANY_FACTS_URL.format(cik=int(cik)))
    metrics = extract_metrics_from_companyfacts(facts)

    print(f"[EDGAR] Income Statement snapshot for {ticker_or_cik.upper()} (CIK {cik}) — {date.today()}:")
    print(f"  Revenue:      {metrics['revenue']}")
    print(f"  Sales:        {metrics['sales']}")
    print(f"  Gross Income: {metrics['gross_income']}")
    print(f"  Net Income:   {metrics['net_income']}")

if __name__ == "__main__":
    # example: python script.py AAPL   or   python script.py 0000320193
    import sys
    if len(sys.argv) < 2:
        print("Usage: python script.py <TICKER|CIK>")
        sys.exit(1)
    print_income_statement(sys.argv[1])
    getReports(ticker_to_cik(sys.argv[1]), ["10-K"], 2)