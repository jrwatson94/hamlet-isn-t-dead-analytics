import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = os.getenv("IG_CSV", str((BASE_DIR / ".." / "merged.csv").resolve()))
HEATMAP_PATH = os.getenv(
    "IG_HEATMAP",
    "/Users/reidwatson/HID/ig-export-merge-ts/analysis/output/weekly_heatmap_and_curve.png",
)
