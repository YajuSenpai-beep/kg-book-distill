# -*- coding: utf-8 -*-
"""Hybrid search: BM25 (lexical) + LSA (vector-space) score fusion."""
import argparse, importlib.util, os

BASE = os.path.dirname(os.path.abspath(__file__))


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, os.path.join(BASE, file))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


bm = load("kg_search", "kg_search.py")
lsa = load("kg_lsa_search", "kg_lsa_search.py")


def search(query, limit=8, scope=None, w_bm25=0.7):
    cand = {}
    b = bm.bm25(query, limit * 4, scope=scope)
    l = lsa.search(query, limit * 4, scope=scope)
    if b:
        mx = max(x[0] for x in b)
        for s, r in b:
            cand.setdefault(r["id"], [r, 0.0, 0.0])[1] = s / mx
    if l:
        mx = max(x[0] for x in l)
        for s, r in l:
            cand.setdefault(r["id"], [r, 0.0, 0.0])[2] = s / mx
    out = []
    for r, sb, sl in cand.values():
        out.append((w_bm25 * sb + (1 - w_bm25) * sl, r))
    out.sort(key=lambda x: -x[0])
    return out[:limit]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--limit", type=int, default=8)
    ap.add_argument("--scope")
    ap.add_argument("--w-bm25", type=float, default=0.7)
    a = ap.parse_args()
    for s, r in search(a.query, a.limit, a.scope, a.w_bm25):
        print(f"{s:.4f}  {r['id']}  {r['title']}  [{r['page']}]")
        print(f"        {r['definition'][:120]}")
        print(f"        {r['skill_module']} · {r['scope']}")


if __name__ == "__main__":
    main()
