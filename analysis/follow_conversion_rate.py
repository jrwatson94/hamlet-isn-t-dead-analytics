import pandas as pd
import os

BASE = os.path.dirname(os.path.abspath(__file__))
CSV_IN  = os.path.join(BASE, "../merged.csv")
OUT_DIR = os.path.join(BASE, "output")
CSV_OUT = os.path.join(OUT_DIR, "conversion_full.csv")

os.makedirs(OUT_DIR, exist_ok=True)

df = pd.read_csv(CSV_IN)

# numeric coercion
for col in ["Reach","Follows"]:
    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# filter | must have follows and reach > 0
df = df[(df["Reach"] > 0) & (df["Follows"] > 0)]

# compute conversion
df["Conversion"] = df["Follows"] / df["Reach"]

keep_cols = ["Publish time","Description","Follows","Reach","Likes","Media URL","Permalink","Conversion"]
keep_cols = [c for c in keep_cols if c in df.columns]

out = df[keep_cols].sort_values("Conversion", ascending=False)

out.to_csv(CSV_OUT, index=False)
print("[ok] wrote:", CSV_OUT)