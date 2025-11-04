import pandas as pd
import re
import os
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import make_interp_spline

# ---------- Paths ----------
BASE = os.path.dirname(os.path.abspath(__file__))
CSV_IN  = os.path.join(BASE, "../merged.csv")
OUT_DIR = os.path.join(BASE, "output")
os.makedirs(OUT_DIR, exist_ok=True)

TAGS_OUT = os.path.join(OUT_DIR, "top_hashtags.csv")
SUMMARY_OUT = os.path.join(OUT_DIR, "hashtag_summary.csv")

# ---------- Load ----------
df = pd.read_csv(CSV_IN)

# ---------- Ensure numeric ----------
for col in ["Reach", "Likes", "Comments", "Shares", "Saved"]:
    df[col] = pd.to_numeric(df.get(col, 0), errors="coerce").fillna(0)

# ---------- Compute Engagement ----------
df["TotalEngagements"] = (
    df["Likes"] + df["Comments"] + df["Shares"] + df["Saved"]
)
df["EngagementRate"] = (
    df["TotalEngagements"] / df["Reach"].replace(0, pd.NA)
) * 100

# ---------- Clean Data ----------
# Drop invalid or nonsensical engagement values
df = df[df["EngagementRate"].notna()]
df = df[df["EngagementRate"] >= 0]
df = df[df["EngagementRate"] <= 99.99]

# ---------- Extract hashtags ----------
def extract_hashtags(text):
    if not isinstance(text, str):
        return []
    return re.findall(r"#\w+", text.lower())

df["Hashtags"] = df["Description"].apply(extract_hashtags)
df["NumHashtags"] = df["Hashtags"].apply(len)
df["HasHashtags"] = df["NumHashtags"] > 0

# ---------- Hashtag vs Non-Hashtag Summary ----------
summary = (
    df.groupby("HasHashtags")
      .agg({
          "EngagementRate": "mean",
          "Reach": "mean",
          "Likes": "mean",
          "NumHashtags": "mean",
      })
      .rename(index={True: "Has hashtags", False: "No hashtags"})
)

summary.to_csv(SUMMARY_OUT)
print(f"[ok] Wrote summary comparison → {SUMMARY_OUT}\n")
print(summary)

# ---------- Per-Hashtag Breakdown ----------
rows = []
for _, r in df.iterrows():
    for h in r["Hashtags"]:
        rows.append((h, r["EngagementRate"], r["Reach"], r["Likes"]))

tags_df = pd.DataFrame(rows, columns=["Hashtag", "EngagementRate", "Reach", "Likes"])

if not tags_df.empty:
    top_tags = (
        tags_df.groupby("Hashtag")
               .agg({
                   "EngagementRate": "mean",
                   "Reach": "mean",
                   "Likes": "mean",
                   "Hashtag": "count",
               })
               .rename(columns={"Hashtag": "PostCount"})
               .sort_values("EngagementRate", ascending=False)
    )

    top_tags.to_csv(TAGS_OUT)
    print(f"[ok] Wrote per-hashtag stats → {TAGS_OUT}")

    # ---------- Quick visualization ----------
    top10 = top_tags.head(10)
    plt.figure(figsize=(10, 5))
    plt.barh(top10.index[::-1], top10["EngagementRate"][::-1], color="#0047AB")
    plt.xlabel("Average Engagement Rate (%)")
    plt.title("Top 10 Hashtags by Engagement Rate")
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "top_hashtags_chart.png"))
    print("[ok] Saved bar chart → output/top_hashtags_chart.png")
else:
    print("No hashtags found in dataset.")

# ---------- Scatter with Average Line ----------
plt.figure(figsize=(7, 5))

# Pale blue scatter points
plt.scatter(
    df["NumHashtags"],
    df["EngagementRate"],
    alpha=0.5,
    color="#9EC9FF",
    edgecolors="none",
    label="Posts",
)

# Mean engagement per hashtag count
mean_curve = (
    df.groupby("NumHashtags")["EngagementRate"]
      .mean()
      .reset_index()
      .sort_values("NumHashtags")
)

# Ignore hashtag counts with too few posts (<5)
counts = df["NumHashtags"].value_counts()
valid_counts = counts[counts >= 5].index
mean_curve = mean_curve[mean_curve["NumHashtags"].isin(valid_counts)]

# Plot the average line (smoothed but not fancy)
x = mean_curve["NumHashtags"]
y = mean_curve["EngagementRate"]

if len(x) > 3:
    # Smooth just for visual continuity
    x_smooth = np.linspace(x.min(), x.max(), 200)
    y_smooth = make_interp_spline(x, y, k=1)(x_smooth)
    plt.plot(x_smooth, y_smooth, color="red", linewidth=2, label="Average Engagement")
else:
    plt.plot(x, y, color="red", linewidth=2, label="Average Engagement")

# Annotate the main peak (optional but clear)
if len(x) > 0:
    peak_idx = np.argmax(y)
    peak_x = x.iloc[peak_idx]
    peak_y = y.iloc[peak_idx]
    plt.scatter(peak_x, peak_y, color="red", s=40, zorder=5)
    plt.text(
        peak_x,
        peak_y + 1,
        f"Peak ≈ {peak_x:.0f} hashtags\n({peak_y:.1f}%)",
        color="red",
        fontsize=8,
        ha="center",
    )

plt.xlabel("Number of Hashtags")
plt.ylabel("Average Engagement Rate (%)")
plt.title("Engagement vs. Number of Hashtags")
plt.legend()
plt.grid(alpha=0.2)
plt.tight_layout()

plt.savefig(os.path.join(OUT_DIR, "hashtag_count_scatter.png"))
print("[ok] Saved clean average scatter → output/hashtag_count_scatter.png")
