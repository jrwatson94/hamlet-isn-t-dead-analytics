import pandas as pd
import pytz
from settings import CSV_PATH

df = pd.read_csv(CSV_PATH)
conv = pd.read_csv("../output/conversion_full.csv")

if "Publish time" in df.columns:
    est = pytz.timezone("America/New_York")
    df["Publish time"] = pd.to_datetime(df["Publish time"], errors="coerce", utc=True)
    df["Publish time"] = df["Publish time"].dt.tz_convert(est).dt.strftime("%m/%d/%Y")
