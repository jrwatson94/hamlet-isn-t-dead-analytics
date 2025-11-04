import os

# ----- Base Directories -----
# /analysis/dashboard/settings.py  → go up two levels to reach project root
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ANALYSIS_DIR = os.path.join(ROOT_DIR, "analysis")
OUTPUT_DIR = os.path.join(ANALYSIS_DIR, "output")

# ----- Data Files -----
CSV_PATH = os.path.join(ROOT_DIR, "merged.csv")
HEATMAP_PATH = os.path.join(OUTPUT_DIR, "weekly_heatmap_and_curve.png")
CONVERSION_PATH = os.path.join(OUTPUT_DIR, "conversion_full.csv")

# ----- Debug printouts -----
print("📄 settings.CSV_PATH =", CSV_PATH)
print("📄 settings.HEATMAP_PATH =", HEATMAP_PATH)
print("📄 settings.CONVERSION_PATH =", CONVERSION_PATH)
