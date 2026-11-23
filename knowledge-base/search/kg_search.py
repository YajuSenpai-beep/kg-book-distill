# -*- coding: utf-8 -*-
"""Local BM25 search over the knowledge base. No external dependencies."""
import argparse, json, math, os, re
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))
ROWS = json.load(open(os.path.join(BASE, "..", "kg-knowledge-points.json"), encoding="utf-8"))


def tokens(text):
    text = text.lower()
    out = re.findall(r"[a-z0-9]+", text)
    for run in re.findall(r"[一-鿿]+", text):
        out.extend(run)
        out.extend(run[i:i + 2] for i in range(len(run) - 1))
    return out


DOCS = []
for r in ROWS:
    text = " ".join([r["title"], r["definition"], r["key_points"], r["formula"],
                     r["chapter_title"], r["section_title"], r["type"]])
    title = " ".join([r["title"], r["chapter_title"], r["section_title"]])
    DOCS.append((r, Counter(tokens(text)), Counter(tokens(title))))

N = len(DOCS)
AVG = sum(sum(tf.values()) for _, tf, _ in DOCS) / max(N, 1)
DF = Counter()
for _, tf, _ in DOCS:
    for t in tf:
        DF[t] += 1


def bm25(query, limit=8, book=None, module=None, scope=None):
    q = tokens(query)
    q_lower = query.lower()
    latin_q = [t for t in q if re.fullmatch(r"[a-z0-9]+", t)]
    scored = []
    for r, tf, title_tf in DOCS:
        if book and r["book"] != book:
            continue
        if module and not r["skill_module"].startswith(module):
            continue
        if scope and r["scope"] != scope:
            continue
        dl = sum(tf.values())
        s = 0.0
        for t in q:
            idf = math.log(1 + (N - DF[t] + 0.5) / (DF[t] + 0.5))
            if t in tf:
                f = tf[t]
                s += idf * f * 2.5 / (f + 1.5 * (1 - 0.75 + 0.75 * dl / max(AVG, 1e-9)))
            if t in title_tf:
                s += idf * 2.0
        # Latin terms (model names) are high-signal: require/boost them.
        latin_hits = sum(1 for t in latin_q if t in tf or t in title_tf)
        if latin_q:
            if latin_hits == 0:
                s *= 0.25
            else:
                s += 20.0 * latin_hits
        hay = (r["title"] + " " + r["definition"]).lower()
        if q_lower and q_lower in hay:
            s += 8.0
        if s > 0:
            scored.append((s, r))
    scored.sort(key=lambda x: -x[0])
    return scored[:limit]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--limit", type=int, default=8)
    ap.add_argument("--book", choices=["A", "B"])
    ap.add_argument("--module", help="如 M5 或 M10")
    ap.add_argument("--scope", help="KG核心 / KG专项 / KG邻接 / 背景")
    a = ap.parse_args()
    for s, r in bm25(a.query, a.limit, a.book, a.module, a.scope):
        print(f"{s:6.2f}  {r['id']}  {r['title']}  [{r['page']}]")
        print(f"        {r['definition'][:120]}")
        print(f"        {r['skill_module']} · {r['scope']}")


if __name__ == "__main__":
    main()
