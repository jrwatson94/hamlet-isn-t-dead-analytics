import os
import pandas as pd
import matplotlib.pyplot as plt

# ---------- Paths ----------
BASE = os.path.dirname(os.path.abspath(__file__))
CSV_IN  = os.path.join(BASE, "../merged.csv")
OUT_DIR = os.path.join(BASE, "output")
CSV_OUT = os.path.join(OUT_DIR, "posttype_comparison.csv")
IMG_OUT = os.path.join(OUT_DIR, "posttype_comparison.png")
IMG_NORM_OUT = os.path.join(OUT_DIR, "posttype_comparison_normalized.png")

# ---------- Load Data ----------
df = pd.read_csv(CSV_IN)
df.columns = df.columns.str.strip()

# ---------- Ensure numeric fields ----------
numeric_cols = ["Reach", "Likes", "Comments", "Shares", "Saved", "Follows", "EngagementRate"]
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

# ---------- Remove outlier ----------
OUTLIER_POST_ID = "18073628026714616"
if "Post ID" in df.columns:
    df = df[df["Post ID"].astype(str) != OUTLIER_POST_ID]

# ---------- Compute Engagement ----------
df["TotalEngagements"] = df["Likes"] + df["Comments"] + df["Shares"] + df["Saved"]
df["EngagementRate"] = (df["TotalEngagements"] / df["Reach"].replace(0, pd.NA)) * 100
df["FollowConversionRate"] = (df["Follows"] / df["Reach"].replace(0, pd.NA)) * 100

# ---------- Clean Engagement Data ----------
df = df[df["EngagementRate"].notna()]
df = df[df["EngagementRate"] >= 0]
df = df[df["EngagementRate"] <= 99.99]

# ---------- Group by Post Type ----------
if "Post type" not in df.columns:
    raise KeyError("Column 'Post type' not found — check your CSV headers.")

summary = (
    df.groupby("Post type")
    .agg(
        AvgReach=("Reach", "mean"),
        AvgEngagementRate=("EngagementRate", "mean"),
        AvgFollowConversion=("FollowConversionRate", "mean"),
        Posts=("Reach", "count")
    )
    .sort_values("AvgEngagementRate", ascending=False)
    .reset_index()
)

# ---------- Format Metrics ----------
summary["AvgReach"] = summary["AvgReach"].round(0)
summary["AvgEngagementRate"] = summary["AvgEngagementRate"].round(2)
summary["AvgFollowConversion"] = summary["AvgFollowConversion"].round(2)

# ---------- Export Raw Summary ----------
os.makedirs(OUT_DIR, exist_ok=True)
summary.to_csv(CSV_OUT, index=False)
print(f"✅ Saved summary CSV to: {CSV_OUT}")

# ---------- Plot (Absolute Values) ----------
plt.figure(figsize=(8, 5))
bar_width = 0.35
x = range(len(summary))

plt.bar([i - bar_width/2 for i in x],
        summary["AvgEngagementRate"],
        width=bar_width,
        label="Engagement Rate (%)")
plt.bar([i + bar_width/2 for i in x],
        summary["AvgFollowConversion"],
        width=bar_width,
        label="Follow Conversion (%)")

plt.xticks(x, summary["Post type"], rotation=30, ha="right")
plt.ylabel("Rate (%)")
plt.title("Instagram Performance by Post Type (Absolute)")
plt.legend()
plt.tight_layout()
plt.savefig(IMG_OUT, dpi=300)
print(f"📊 Saved absolute chart image to: {IMG_OUT}")

# ---------- Normalize for Comparison ----------
# Scale each metric 0–100 within its own column
for col in ["AvgReach", "AvgEngagementRate", "AvgFollowConversion"]:
    summary[col + "_Norm"] = (summary[col] / summary[col].max()) * 100

# ---------- Plot Normalized Comparison ----------
plt.figure(figsize=(9, 5))
bar_width = 0.25
x = range(len(summary))

plt.bar([i - bar_width for i in x],
        summary["AvgReach_Norm"],
        width=bar_width,
        label="Reach (normalized)")
plt.bar(x,
        summary["AvgEngagementRate_Norm"],
        width=bar_width,
        label="Engagement Rate (normalized)")
plt.bar([i + bar_width for i in x],
        summary["AvgFollowConversion_Norm"],
        width=bar_width,
        label="Follow Conversion (normalized)")

plt.xticks(x, summary["Post type"], rotation=30, ha="right")
plt.ylabel("Relative Performance (0–100)")
plt.title("Instagram Post Type — Normalized Comparison")
plt.legend()
plt.tight_layout()
plt.savefig(IMG_NORM_OUT, dpi=300)
print(f"📊 Saved normalized comparison chart to: {IMG_NORM_OUT}")

# ---------- Print Preview ----------
print("\n📈 AVERAGE PERFORMANCE BY POST TYPE (RAW):\n")
print(summary[["Post type", "AvgReach", "AvgEngagementRate", "AvgFollowConversion", "Posts"]].to_string(index=False))

print("\n📈 RELATIVE PERFORMANCE (0–100 SCALE):\n")
print(summary[["Post type", "AvgReach_Norm", "AvgEngagementRate_Norm", "AvgFollowConversion_Norm"]].round(1).to_string(index=False))
