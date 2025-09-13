import json, pathlib, pandas as pd

# --- load ----------------------------------------------------
data = json.loads(pathlib.Path("output.json").read_text())
facts = data["facts"]["us-gaap"]

# --- tag map -------------------------------------------------
income_tags = {
    "Revenue": ["RevenueFromContractWithCustomerNet", "SalesRevenueNet", "RevenueFromContractWithCustomerExcludingAssessedTax"],
    "CostOfSales": ["CostOfGoodsAndServicesSold"],
    "GrossProfit": ["GrossProfit"],
    "OperatingIncome": ["OperatingIncomeLoss"],
    "NetIncome": ["NetIncomeLoss"],
}

def getRevenue(form="10-K"):
    revenue = []
    for tag in income_tags["Revenue"]:
        if tag not in facts:
            continue
        for unit, obs in facts[tag]["units"].items():
            for item in obs:
                if item.get("form") != form:   # keep 10-K only
                    continue
                if item.get("fp") != "FY":       # ignore amended Q data
                    continue
                revenue.append({
                    "fy":     item["fy"],
                    "end":    item["end"],
                    "value":  item["val"],
                    "unit":   unit,
                    "accn":   item["accn"],
                })
    return pd.DataFrame(revenue)

def getCostOfSales(form="10-K"):
    cost_of_sales = []
    for tag in income_tags["CostOfSales"]:
        if tag not in facts:
            continue
        for unit, obs in facts[tag]["units"].items():
            for item in obs:
                if item.get("form") != form:   # keep 10-K only
                    continue
                if item.get("fp") != "FY":       # ignore amended Q data
                    continue
                cost_of_sales.append({
                    "fy":     item["fy"],
                    "end":    item["end"],
                    "value":  item["val"],
                    "unit":   unit,
                    "accn":   item["accn"],
                })
    return pd.DataFrame(cost_of_sales)

def printGAAPTitles(data):
    us_gaap_titles = sorted(data["facts"]["us-gaap"].keys())

    print(f"{len(us_gaap_titles)} distinct us-gaap tags found.")
    print(us_gaap_titles)


rows = getRevenue()#.assign(metric="Revenue").to_dict("records")
# df = pd.DataFrame(rows).sort_values(["fy", "metric"])
print(rows.sort_values("end").to_string(index=False))
printGAAPTitles(data)
