import os
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from matplotlib import cm
import numpy as np
import re
from collections import defaultdict
import nltk
from nltk.corpus import stopwords

# ---------- Paths ----------
BASE = os.path.dirname(os.path.abspath(__file__))
CSV_IN  = os.path.join(BASE, "../merged.csv")
OUT_DIR = os.path.join(BASE, "output")
IMG_WORDCLOUD = os.path.join(OUT_DIR, "wordcloud_heatmap.png")
CSV_WORDCLOUD = os.path.join(OUT_DIR, "wordcloud_data.csv")

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

# ---------- Setup ----------
os.makedirs(OUT_DIR, exist_ok=True)

# ---------- Stopwords ----------
try:
    stop_words = set(stopwords.words("english"))
except LookupError:
    nltk.download("stopwords")
    stop_words = set(stopwords.words("english"))

# ---------- Tokenize Words (ignore hashtags and stopwords) ----------
# Matches only plain words (3+ letters), ignores hashtags and mentions
word_pattern = re.compile(r"\b[a-z]{3,}[a-z0-9_]*\b", re.IGNORECASE)

def extract_words(text):
    if not isinstance(text, str):
        return []
    words = word_pattern.findall(text.lower())
    return [w for w in words if w not in stop_words]

df["words"] = df["Description"].fillna("").apply(extract_words)

# ---------- Build Word-Level Stats ----------
word_counts = defaultdict(int)
word_engagements = defaultdict(list)

for _, row in df.iterrows():
    eng = row["EngagementRate"]
    for w in set(row["words"]):  # count each word once per post
        word_counts[w] += 1
        word_engagements[w].append(eng)

# ---------- Keep only words used in >= 2 posts ----------
filtered_words = {w: c for w, c in word_counts.items() if c >= 2}

# ---------- Limit to Top 50 Most Frequent Words ----------
top_words = sorted(filtered_words.items(), key=lambda x: x[1], reverse=True)[:50]
top_word_set = {w for w, _ in top_words}

word_counts = {w: word_counts[w] for w in top_word_set}
word_engagements = {w: word_engagements[w] for w in top_word_set}

# ---------- Compute Mean Engagement per Word ----------
word_mean_engagement = {
    w: float(np.mean(word_engagements[w])) for w in word_counts
}

# ---------- Normalize Engagement to 0–1 Scale ----------
eng_min, eng_max = min(word_mean_engagement.values()), max(word_mean_engagement.values())
normalized_eng = {
    w: (word_mean_engagement[w] - eng_min) / (eng_max - eng_min + 1e-6)
    for w in word_mean_engagement
}

# ---------- Save Word Data to CSV ----------
word_df = pd.DataFrame({
    "Word": list(word_counts.keys()),
    "UsageCount": [word_counts[w] for w in word_counts],
    "MeanEngagementRate": [word_mean_engagement[w] for w in word_counts],
    "NormalizedEngagement": [normalized_eng[w] for w in word_counts]
}).sort_values("UsageCount", ascending=False)

word_df.to_csv(CSV_WORDCLOUD, index=False)
print(f"📄 Saved word data to: {CSV_WORDCLOUD}")

# ---------- Color Function Based on Engagement ----------
cmap = cm.get_cmap("Blues")

def color_func(word, *args, **kwargs):
    val = normalized_eng.get(word, 0)
    r, g, b, _ = cmap(val)
    return f"rgb({int(r*255)}, {int(g*255)}, {int(b*255)})"

# ---------- Generate Word Cloud ----------
wc = WordCloud(
    width=1600,
    height=900,
    background_color="white",
    max_words=50,
    prefer_horizontal=0.9,
    relative_scaling=0.6,
    collocations=False
).generate_from_frequencies(word_counts)

# ---------- Recolor Based on Engagement ----------
wc_recolored = wc.recolor(color_func=color_func)

# ---------- Plot ----------
plt.figure(figsize=(12, 8))
plt.imshow(wc_recolored, interpolation="bilinear")
plt.axis("off")
plt.title("Word Cloud Heatmap — Top 50 Words (Size = Frequency, Color = Mean Engagement)", fontsize=14)
plt.tight_layout()
plt.savefig(IMG_WORDCLOUD, dpi=300)
plt.show()

print(f"☁️  Saved word cloud heatmap to: {IMG_WORDCLOUD}")
