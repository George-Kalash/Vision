#!/usr/bin/env python3
import os, sys, requests
from datetime import datetime

TD_KEY = os.getenv("TWELVE_DATA_API_KEY")
if not TD_KEY:
    sys.exit("Set TWELVE_DATA_API_KEY")

SEC_UA = os.getenv("SEC_UA", "").strip()  # only needed for SEC fallback

SYMBOL = (sys.argv[1] if len(sys.argv) > 1 else "AAPL").upper()
EXCHANGE = os.getenv("EXCHANGE", "")  # optional, e.g. NASDAQ or NYSE

def latest_price(symbol: str, exchange: str | None = None):
    """
    Return the latest price for `symbol` from Twelve Data /quote.
    If `price` is missing, fall back to `close`. Returns float or None.
    """
    params = {"symbol": symbol}
    if exchange:
        params["exchange"] = exchange  # optional hint, e.g., "NASDAQ" or "NYSE"

    d = td_get("/quote", params)  # uses your existing td_get helper

    # Handle TD error objects: {"status": "error", ...}
    if not isinstance(d, dict) or d.get("status") == "error":
        return None

    val = d.get("price") or d.get("close")
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def td_get(path, params):
    url = f"https://api.twelvedata.com{path}"
    q = dict(params or {})
    q["apikey"] = TD_KEY
    r = requests.get(url, params=q, timeout=20)
    # Treat 4xx/5xx as "not available", we'll try fallbacks
    if r.status_code != 200:
        return {}
    try:
        return r.json()
    except Exception:
        return {}

def latest_eps_quarterly(symbol):
    d = td_get("/earnings", {"symbol": symbol, "period": "quarter"})
    # TD responses differ by plan; normalize to an array of rows
    rows = d.get("earnings") or d.get("data")
    if not isinstance(rows, list) or not rows:
        return None
    row0 = rows[0]
    # common keys: eps_actual, eps
    val = row0.get("eps_actual", row0.get("eps"))
    try:
        return float(val)
    except (TypeError, ValueError):
        return None

def latest_shares_td(symbol, exchange=""):
    params = {"symbol": symbol}
    if exchange:
        params["exchange"] = exchange
    d = td_get("/statistics", params)
    # Can be flat or nested under "statistics" depending on plan/view
    if isinstance(d, dict):
        if "shares_outstanding" in d:
            return d.get("shares_outstanding")
        if isinstance(d.get("statistics"), dict):
            return d["statistics"].get("shares_outstanding")
    return None

def latest_shares_sec(symbol):
    if not SEC_UA:
        return None  # no UA → don't hit SEC
    s = requests.Session()
    s.headers.update({"User-Agent": SEC_UA, "Accept-Encoding": "gzip, deflate"})
    # 1) map ticker → CIK via SEC's published mapping
    idx = s.get("https://www.sec.gov/files/company_tickers.json", timeout=30)
    idx.raise_for_status()
    mapping = idx.json()
    cik10 = None
    for _k, row in mapping.items():
        if str(row.get("ticker", "")).upper() == symbol:
            cik10 = str(int(row.get("cik_str"))).zfill(10)
            break
    if not cik10:
        return None
    # 2) companyfacts → dei.EntityCommonStockSharesOutstanding.units.shares[]
    cf = s.get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik10}.json", timeout=30)
    if cf.status_code != 200:
        return None
    j = cf.json()
    shares = (
        j.get("facts", {})
         .get("dei", {})
         .get("EntityCommonStockSharesOutstanding", {})
         .get("units", {})
         .get("shares", [])
    )
    if not isinstance(shares, list) or not shares:
        return None
    # pick the latest by 'end' date
    def key(x):
        try: return datetime.strptime(x.get("end","1900-01-01"), "%Y-%m-%d")
        except Exception: return datetime(1900,1,1)
    latest = max(shares, key=key)
    return latest.get("val")

def latest_earnings(symbol, exchange=""):
    # Latest EPS from Twelve Data /earnings
    params = {"symbol": symbol, "outputsize": 1}  # latest only
    if exchange:
        params["exchange"] = exchange  # include only if provided

    d = td_get("/earnings", params)

    # Handle Twelve Data error objects: {"status":"error", ...}
    if not isinstance(d, dict) or d.get("status") == "error":
        return None

    rows = d.get("earnings") or d.get("data")
    if not isinstance(rows, list) or not rows:
        return None

    # Prefer the most recent row that has a real EPS value
    def has_eps(r):
        return r.get("eps_actual") is not None or r.get("eps") is not None

    candidates = [r for r in rows if has_eps(r)] or rows

    # Not all responses are guaranteed sorted — pick max by date
    def row_date(r):
        return r.get("date") or r.get("reported_date") or ""  # TD uses "date"
    row = max(candidates, key=row_date)

    eps_val = row.get("eps_actual") or row.get("eps")
    try:
        eps_val = float(eps_val) if eps_val is not None else None
    except (TypeError, ValueError):
        pass

    date = row.get("date") or row.get("reported_date")
    # Synthesize a quarter label if you expect "period" in your downstream code
    period = None
    if date and len(date) >= 7:
        try:
            m = int(date[5:7])
            period = f"Q{((m - 1) // 3) + 1}"
        except Exception:
            period = None

    return {"eps": eps_val, "date": date, "period": period or row.get("time")}

def main():
    # 1) EPS (quarterly)
    eps = latest_eps_quarterly(SYMBOL)
    if eps is not None:
        print(f"{SYMBOL} latest EPS (quarterly): {eps}")
        

    # 2) Shares outstanding from Twelve Data
    so = latest_shares_td(SYMBOL, EXCHANGE)
    if so is not None:
        print(f"{SYMBOL} shares_outstanding (Twelve Data): {so}")
        

    # 3) Fallback to SEC
    so_sec = latest_shares_sec(SYMBOL)
    if so_sec is not None:
        print(f"{SYMBOL} shares_outstanding (SEC latest reported): {so_sec}")
        
    price = latest_earnings(SYMBOL, EXCHANGE)
    print(f"{SYMBOL} latest earnings: {price}")
    if price is not None: 
        print(f"{SYMBOL} latest price: {price}")
    print("No EPS or shares_outstanding available (check API plan/headers).")

if __name__ == "__main__":
    if not os.getenv("TWELVE_DATA_API_KEY"):
        sys.exit("Set TWELVE_DATA_API_KEY")
    sym = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    px = latest_price(sym, "NASDAQ")
    print(px if px is not None else "No price available")