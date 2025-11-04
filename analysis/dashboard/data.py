import os
import pandas as pd
import pytz
from settings import CSV_PATH

# Ensure CSV_PATH is absolute
CSV_PATH = os.path.abspath(CSV_PATH)

# Derive the base directory (root of project)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Define conversion file path (../output/conversion_full.csv relative to dashboard/)
CONV_PATH = os.path.join(BASE_DIR, "analysis", "output", "conversion_full.csv")

print("📂 Loading main CSV from:", CSV_PATH)
print("📂 Loading conversion CSV from:", CONV_PATH)

if not os.path.exists(CSV_PATH):
    raise FileNotFoundError(f"❌ CSV file not found at {CSV_PATH}")

if not os.path.exists(CONV_PATH):
    raise FileNotFoundError(f"❌ Conversion file not found at {CONV_PATH}")

# Load data
df = pd.read_csv(CSV_PATH)
conv = pd.read_csv(CONV_PATH)

# Convert and format Publish time column if present
if "Publish time" in df.columns:
    est = pytz.timezone("America/New_York")
    df["Publish time"] = pd.to_datetime(df["Publish time"], errors="coerce", utc=True)
    df["Publish time"] = (
        df["Publish time"]
        .dt.tz_convert(est)
        .dt.strftime("%m/%d/%Y")
    )
