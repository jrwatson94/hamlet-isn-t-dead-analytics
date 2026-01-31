# analysis/videos.py
#
# Outputs VIDEO / REELS posts from the last 12 months only,
# ranked by engagement rate.
# engagement rate = total engagements / reach
# Input is a fixed absolute CSV path.
# Output file renamed to boost_candidates.csv
# All original fields are preserved.

import pandas as pd
import os
from datetime import timedelta

# ---------- Fixed Paths ----------
CSV_IN = "/Users/reidwatson/HID/ig-export-merge-ts/merged.csv"

BASE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(BASE, "output")
CSV_OUT = os.path.join(OUT_DIR, "boost_candidates.csv")

os.makedirs(OUT_DIR, exist_ok=True)

# ---------- Load Data ----------
df = pd.read_csv(CSV_IN)

# ---------- Parse Publish Time ----------
df["Publish time"] = pd.to_datetime(df.get("Publish time"), errors="coerce", utc=True)

now = pd.Timestamp.utcnow()
one_year_ago = now - timedelta(days=365)

df = df[df["Publish time"].notna()]
df = df[df["Publish time"] >= one_year_ago]

# ---------- Filter Videos ----------
df["Post type"] = df.get("Post type", "").astype(str).str.upper()
df = df[df["Post type"].isin(["VIDEO", "REELS", "REEL"])]

# ---------- Numeric Conversion ----------
numeric_cols = [
    "Reach",
    "Total Interactions",
    "Likes",
    "Comments",
    "Shares",
    "Saved",
    "Replies",
    "Follows",
]

for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    else:
        df[col] = 0

# ---------- Total Engagements ----------
df["__total_engagements"] = df["Total Interactions"]

fallback_mask = df["__total_engagements"] <= 0
df.loc[fallback_mask, "__total_engagements"] = (
    df.loc[fallback_mask, ["Likes", "Comments", "Shares", "Saved", "Replies", "Follows"]]
      .sum(axis=1)
)

# ---------- Engagement Rate ----------
df["__engagement_rate"] = df["__total_engagements"] / df["Reach"].replace(0, pd.NA)

# ---------- Clean ----------
df = df[df["__engagement_rate"].notna()]
df = df[df["__engagement_rate"] >= 0]
df = df[df["__engagement_rate"] <= 1.0]

# ---------- Sort & Rank ----------
df = df.sort_values(
    by=["__engagement_rate", "__total_engagements", "Reach"],
    ascending=[False, False, False],
)

df["__rank"] = range(1, len(df) + 1)

# ---------- Save ----------
df.to_csv(CSV_OUT, index=False)

# ---------- Summary ----------
print(f"[ok] Wrote boost candidates → {CSV_OUT}")
print(f"Videos (last 12 months): {len(df)}")
print(f"Average engagement rate: {(df['__engagement_rate'].mean() * 100):.2f}%")
print("\nTop 5 Preview:")
print(df[["Publish time", "__engagement_rate"]].head(5))
