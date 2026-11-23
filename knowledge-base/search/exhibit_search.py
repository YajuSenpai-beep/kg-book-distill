# -*- coding: utf-8 -*-
"""BM25 search over figures and tables. No external dependencies."""
import argparse, json, math, os, re
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.join(BASE, "..")
FIGS = json.load(open(os.path.join(KB, "figures", "figure-index.json"), encoding="utf-8"))
TABLES = {t["id"]: t for t in json.load(open(os.path.join(KB, "tables", "table-data.json"),
                                             encoding="utf-8"))["tables"]}


def tokens(text):
    text = text.lower()
    out = re.findall(r"[a-z0-9]+", text)
    for run in re.findall(r"[一-鿿]+", text):
        out.extend(run)
        out.extend(run[i:i + 2] for i in range(len(run) - 1))
    return out


DOCS = []
for f in FIGS:
    t = TABLES.get(f["id"], {})
    text = " ".join([f["caption"], f["role"], f["section_title"], f.get("note", ""),
                     f.get("context", ""), " ".join(f.get("linked_points", [])),
                     " ".join(str(x) for row in t.get("rows", [])[:3] for x in row)])
    title = " ".join([f["caption"], f["number"], f["section_title"]])
    DOCS.append((f, Counter(tokens(text)), Counter(tokens(title))))

N = len(DOCS)
AVG = sum(sum(tf.values()) for _, tf, _ in DOCS) / max(N, 1)
DF = Counter()
for _, tf, _ in DOCS:
    for t in tf:
        DF[t] += 1


def bm25(query, limit=8, kind=None, book=None):
    q = tokens(query)
    ql = query.lower()
    scored = []
    for f, tf, title_tf in DOCS:
        if kind and f["kind"] != kind:
            continue
        if book and f["book"] != book:
            continue
        dl = sum(tf.values())
        s = 0.0
        for t in q:
            idf = math.log(1 + (N - DF[t] + 0.5) / (DF[t] + 0.5))
            if t in tf:
                s += idf * tf[t] * 2.5 / (tf[t] + 1.5 * (0.25 + 0.75 * dl / max(AVG, 1e-9)))
            if t in title_tf:
                s += idf * 2.0
        hay = (f["caption"] + " " + f["number"] + " " + f.get("note", "")).lower()
        if ql and ql in hay:
            s += 8.0
        if s > 0:
            scored.append((s, f))
    scored.sort(key=lambda x: -x[0])
    return scored[:limit]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--limit", type=int, default=8)
    ap.add_argument("--kind", choices=["图", "表"])
    ap.add_argument("--book", choices=["A", "B"])
    a = ap.parse_args()
    for s, f in bm25(a.query, a.limit, a.kind, a.book):
        print(f"{s:6.2f}  {f['id']}  {f['number']} {f['caption']}  [p.{f['page']}]")
        print(f"        {f['role']} · {f['book']} 第{f['chapter']}章 · {f['section']}")
        if f.get("note"):
            print(f"        {f['note'][:140]}")


if __name__ == "__main__":
    main()
