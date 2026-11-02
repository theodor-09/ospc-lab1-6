"""Number of orders per region, quarter and order size (segments.csv)."""

import os

import pandas as pd

DATA = os.environ.get("DATA", os.path.expanduser("~/data/sales_2025.csv"))
OUT = os.environ.get("OUT", os.path.expanduser("~/data/out"))
os.makedirs(OUT, exist_ok=True)

orders = pd.read_csv(DATA, usecols=["order_date", "region", "quantity", "unit_price"])
# generated with chatgpt (openai). prompt: help optimize task 4 by replacing slow date conversions with pandas.
orders["quarter"] = pd.to_datetime(orders["order_date"]).dt.quarter

def segment(order):
    # generated with chatgpt (openai). prompt: help optimize task 4 by replacing slow date conversions with pandas.
    quarter = order.quarter
    value = order.quantity * order.unit_price
    if value >= 500:
        size = "large"
    elif value >= 100:
        size = "medium"
    else:
        size = "small"
    return f"Q{quarter} {size}"


counts = {}
for order in orders.itertuples(index=False):
    key = (order.region, segment(order))
    counts[key] = counts.get(key, 0) + 1

table = pd.Series(counts).rename_axis(["region", "segment"]).unstack(fill_value=0)
table.to_csv(os.path.join(OUT, "segments.csv"))
print("segments: done")
