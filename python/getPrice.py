import os, sys, time, csv, requests
from typing import Dict, Any, List
API_KEY = os.getenv("TWELVE_DATA_API_KEY")
if not API_KEY:
    sys.exit("Set TWELVE_DATA_API_KEY environment variable.") 
    
BASE = "https://api.twelvedata.com"


def td_get(path: str, params: Dict[str, Any], retries=4, backoff=1.6):
    url = f"{BASE}{path}"
    q = dict(params or {}); q["apikey"] = API_KEY
    for i in range(retries):
        r = requests.get(url, params=q, timeout=20)
        if r.status_code in (429, 500, 502, 503, 504):
            time.sleep(backoff ** (i + 1)); continue
        if r.status_code in (401, 402, 403):
            # plan-gated or unauthorized; return an empty dict for graceful handling
            return {}
        try:
            data = r.json()
        except Exception:
            return {}
        if isinstance(data, dict) and data.get("status") == "error":
            return {}
        return data
    return {}



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

if __name__ == "__main__":
    if not os.getenv("TWELVE_DATA_API_KEY"):
        sys.exit("Set TWELVE_DATA_API_KEY")
    sym = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    px = latest_price(sym, "NASDAQ")
    print(px if px is not None else "No price available")