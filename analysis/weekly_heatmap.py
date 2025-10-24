import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np

CSV_PATH = os.path.join(os.path.dirname(__file__), "../merged.csv")
OUTLIER_POST_ID = "18073628026714616"

df = pd.read_csv(CSV_PATH)

# Drop outlier
df = df[df["Post ID"].astype(str) != OUTLIER_POST_ID]

# -------- DATETIME PARSE (assume timestamps are UTC, convert to NY) --------
dt = pd.to_datetime(
    df["Publish time"],
    utc=True,
    errors="coerce",
    infer_datetime_format=True
)
df["Publish time"] = dt.dt.tz_convert("America/New_York")
# ---------------------------------------------------------------------------

# Numeric reach (blanks -> 0)
df["Reach"] = pd.to_numeric(df["Reach"], errors="coerce").fillna(0)
df = df.dropna(subset=["Publish time"])

# Build week-hour indices
df["weekday"] = df["Publish time"].dt.dayofweek  # Mon=0,...,Sun=6
df["hour"]    = df["Publish time"].dt.hour       # 0..23

# ---- HEATMAP DATA (force 7x24 grid) ----
heatmap = (
    df.pivot_table(
        index="weekday",
        columns="hour",
        values="Reach",
        aggfunc="mean"
    )
    .reindex(index=range(7), columns=range(24))
    .fillna(0)
)

# ---- 24h AVERAGE CURVE ----
curve = df.groupby("hour")["Reach"].mean().reindex(range(24), fill_value=0)

# ---- PLOT ----
fig, axes = plt.subplots(2, 1, figsize=(14, 10), gridspec_kw={'height_ratios':[3,1]})

# ---- TOP: HEATMAP ----
im = axes[0].imshow(
    heatmap.values,
    aspect="auto",
    cmap="OrRd",
    origin="upper",
    extent=[0, 24, 7, 0],
    interpolation="nearest"
)

axes[0].set_title("Average Reach by Day & Hour (Outlier Removed)", fontsize=20)
axes[0].set_ylabel("Day of Week", fontsize=20)
axes[0].set_xticks(range(0, 24, 2))
axes[0].set_xticklabels(range(0, 24, 2), fontsize=14)
axes[0].set_yticks([0.5, 1.5, 2.5, 3.5, 4.5, 5.5, 6.5])
axes[0].set_yticklabels(["Mon","Tue","Wed","Thu","Fri","Sat","Sun"], fontsize=14)
axes[0].set_xlim(0, 23)

cbar = fig.colorbar(im, ax=axes[0], orientation="vertical", label="Avg Reach")
cbar.ax.tick_params(labelsize=14)
cbar.set_label("Avg Reach", fontsize=18)

# ---- BOTTOM: 24h CURVE ----
axes[1].plot(range(24), curve.values, marker="o", color="#D35400")
axes[1].set_title("Average Reach by Hour (Collapsed Across Week)", fontsize=20)
axes[1].set_xlabel("Hour of Day (0–23)", fontsize=20)
axes[1].set_ylabel("Avg Reach", fontsize=20)
axes[1].set_xticks(range(0, 24, 2))
axes[1].set_xticklabels(range(0, 24, 2), fontsize=14)
axes[1].set_xlim(0, 23)
axes[1].grid(alpha=0.2)

# ---- GLOBAL TITLE ----

plt.tight_layout()

out_dir = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "weekly_heatmap_and_curve.png")
plt.savefig(out_path, dpi=200)
plt.close()

print(f"[ok] Saved dual visualization → {out_path}")
