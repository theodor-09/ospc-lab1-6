"""Revenue by region and month (revenue_by_region_month.csv)."""

import os
import pandas as pd

DATA = os.environ.get("DATA", os.path.expanduser("~/data/sales_2025.csv"))
OUT = os.environ.get("OUT", os.path.expanduser("~/data/out"))
os.makedirs(OUT, exist_ok=True)

totals = None
rows = 0

for chunk in pd.read_csv(DATA, chunksize=100_000):
    rows += len(chunk)

    chunk["order_date"] = pd.to_datetime(chunk["order_date"])
    chunk["revenue"] = chunk["quantity"] * chunk["unit_price"]

    # Keep solely the totals for region/month.
    monthly = chunk.groupby(
        ["region", chunk["order_date"].dt.month]
    )["revenue"].sum()

    if totals is None:
        totals = monthly
    else:
        totals = totals.add(monthly, fill_value=0)

    print(f"report: processed {rows:,} orders")

# Same table as og
table = totals.unstack()
table.round(2).to_csv(
    os.path.join(OUT, "revenue_by_region_month.csv")
)

print("report: done")
