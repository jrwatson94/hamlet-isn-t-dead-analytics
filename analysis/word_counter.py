import pandas as pd
from collections import Counter
import re

# Load file
df = pd.read_csv("../merged.csv")

# Combine all descriptions
text = " ".join(df["Description"].dropna().astype(str))

# Basic cleanup
text = re.sub(r"http\S+", "", text)          # remove links
text = re.sub(r"[^a-zA-Z ]", " ", text)     # keep letters and hashtags
words = [w.lower() for w in text.split() if len(w) > 3]

# Get top 50 most common words
common = Counter(words).most_common(100)
for word, count in common:
    print(f"{word}: {count}")
