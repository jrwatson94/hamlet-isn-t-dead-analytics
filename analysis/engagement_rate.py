import pandas as pd
import os

# ---------- Paths ----------
BASE = os.path.dirname(os.path.abspath(__file__))
CSV_IN  = os.path.join(BASE, "../merged.csv")
OUT_DIR = os.path.join(BASE, "output")
CSV_OUT = os.path.join(OUT_DIR, "engagement_top25.csv")

os.makedirs(OUT_DIR, exist_ok=True)

# ---------- Load Data ----------
df = pd.read_csv(CSV_IN)

# ---------- Numeric Conversion ----------
for col in ["Reach", "Likes", "Comments", "Shares", "Saved"]:
    df[col] = pd.to_numeric(df.get(col, 0), errors="coerce").fillna(0)

# ---------- Compute Engagement ----------
df["TotalEngagements"] = df["Likes"] + df["Comments"] + df["Shares"] + df["Saved"]
df["EngagementRate"] = (df["TotalEngagements"] / df["Reach"].replace(0, pd.NA)) * 100

# ---------- Clean Data ----------
df = df[df["EngagementRate"].notna()]
df = df[df["EngagementRate"] >= 0]
df = df[df["EngagementRate"] <= 99.99]


# ---------- Keep Relevant Columns ----------
keep_cols = [
    "Publish time", "Description", "Reach", "Likes", "Comments",
    "Shares", "Saved", "Media URL", "Permalink", "EngagementRate"
]
keep_cols = [c for c in keep_cols if c in df.columns]

# ---------- Sort & Slice Top 25 ----------
out = df[keep_cols].sort_values("EngagementRate", ascending=False).head(25)

# ---------- Save ----------
out.to_csv(CSV_OUT, index=False)

# ---------- Print Summary ----------
print(f"[ok] Wrote top 25 engagement posts → {CSV_OUT}")
print(f"Average engagement rate (Top 25): {out['EngagementRate'].mean():.2f}%")
print("\nTop 5 Preview:")
print(out.head(5)[['Publish time', 'EngagementRate']])
