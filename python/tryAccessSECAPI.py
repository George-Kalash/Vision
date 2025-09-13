# tryAccessSECAPI.py
import os, sys, requests

ua = os.getenv("SEC_UA")
if not ua:
    sys.exit('Set SEC_UA first, e.g. export SEC_UA="George Kalashlinskyi scccbf@gmail.com (VisionApp/1.0)"')

url = "https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json"
r = requests.get(url, headers={"User-Agent": ua, "Accept-Encoding": "gzip, deflate"}, timeout=30)
r.raise_for_status()
print(r.text)  # raw JSON