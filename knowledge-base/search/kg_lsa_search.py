# -*- coding: utf-8 -*-
"""LSA vector-space search over the knowledge base (TF-IDF + SVD).

This is a lightweight semantic-ish baseline that needs only scikit-learn.
For neural embeddings, swap the vectorizer for a sentence-transformer model.
"""
import argparse, json, os
import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

BASE = os.path.dirname(os.path.abspath(__file__))
ROWS = json.load(open(os.path.join(BASE, "..", "kg-knowledge-points.json"), encoding="utf-8"))
TEXTS = [
    " ".join([r["title"], r["definition"], r["key_points"], r["formula"],
              r["chapter_title"], r["section_title"], r["type"]])
    for r in ROWS
]
vec = TfidfVectorizer(analyzer="char", ngram_range=(1, 3), min_df=2, max_features=60000)
X = vec.fit_transform(TEXTS)
svd = TruncatedSVD(n_components=128, random_state=42)
Z = svd.fit_transform(X)


def search(query, limit=8, scope=None):
    q = svd.transform(vec.transform([query]))
    sims = cosine_similarity(q, Z)[0]
    idx = np.argsort(-sims)
    out = []
    for i in idx:
        r = ROWS[i]
        if scope and r["scope"] != scope:
            continue
        if sims[i] <= 0:
            break
        out.append((float(sims[i]), r))
        if len(out) >= limit:
            break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--limit", type=int, default=8)
    ap.add_argument("--scope")
    a = ap.parse_args()
    for s, r in search(a.query, a.limit, a.scope):
        print(f"{s:.4f}  {r['id']}  {r['title']}  [{r['page']}]")
        print(f"        {r['definition'][:120]}")
        print(f"        {r['skill_module']} · {r['scope']}")


if __name__ == "__main__":
    main()
