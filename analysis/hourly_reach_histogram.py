import pandas as pd
import matplotlib.pyplot as plt
import os

CSV_PATH = os.path.join(os.path.dirname(__file__), "../merged.csv")
OUTLIER_POST_ID = "18073628026714616"

# ---------- LOAD DATA ----------
df = pd.read_csv(CSV_PATH)

# Drop the known outlier post
df = df[df["Post ID"].astype(str) != OUTLIER_POST_ID]

# -------- DATETIME PARSE (mixed formats, assume NY-local) --------
dt = pd.to_datetime(
    df["Publish time"],
    errors="coerce",
    infer_datetime_format=True,
    dayfirst=False
)
df["Publish time"] = dt.dt.tz_localize("America/New_York")
# ---------------------------------------------------------------

# Treat blanks as zero reach
df["Reach"] = pd.to_numeric(df["Reach"], errors="coerce").fillna(0)

# Drop rows missing publish time
df = df.dropna(subset=["Publish time"])

# ---------- BUILD WEEK-HOUR INDEX ----------
df["weekday"] = df["Publish time"].dt.dayofweek  # 0=Mon,...,6=Sun
df["hour"] = df["Publish time"].dt.hour
df["weekhour"] = df["weekday"] * 24 + df["hour"]  # 0–167

hourly = df.groupby("weekhour")["Reach"].mean().reindex(range(168), fill_value=0)

x = range(168)
y = hourly.values

# Color weekdays vs weekends
colors = ["#4A90E2" if wh < 120 else "#E67E22" for wh in x]

# ---------- PLOT ----------
plt.figure(figsize=(16,5))
plt.bar(x, y, color=colors)

plt.title("Average Reach by Hour of Week (Outlier Removed)")
plt.xlabel("Hour of Week (0=Mon 00:00 ... 167=Sun 23:00)")
plt.ylabel("Avg Reach")

plt.axvline(120, color="black", linestyle="--", alpha=0.5) # Sat start
plt.axvline(144, color="black", linestyle="--", alpha=0.5) # Sun start

out_dir = os.path.join(os.path.dirname(__file__), "output")
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "hourly_reach.png")

plt.tight_layout()
plt.savefig(out_path, dpi=200)
print(f"[ok] Saved chart → {out_path}")
plt.close()
