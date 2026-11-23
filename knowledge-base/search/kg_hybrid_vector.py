# -*- coding: utf-8 -*-
"""Hybrid: BM25 (lexical) + BGE neural vector (semantic).

Use the embedding venv:
    .venv-embed\\Scripts\\python.exe kg_hybrid_vector.py "查询"
"""
import argparse, importlib.util, os, sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.abspath(__file__))


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, os.path.join(BASE, file))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


bm = load("kg_search", "kg_search.py")
vec = load("kg_vector_search", "kg_vector_search.py")


def search(query, limit=8, scope=None, w_bm25=0.6, vectors=None):
    cand = {}
    b = bm.bm25(query, limit * 4, scope=scope)
    v = vec.search(query, limit * 4, scope=scope, vectors=vectors)
    if b:
        mx = max(x[0] for x in b)
        for s, r in b:
            cand.setdefault(r["id"], [r, 0.0, 0.0])[1] = s / mx
    if v:
        mx = max(x[0] for x in v)
        for s, r in v:
            cand.setdefault(r["id"], [r, 0.0, 0.0])[2] = s / mx
    out = [(w_bm25 * sb + (1 - w_bm25) * sv, r) for r, sb, sv in cand.values()]
    out.sort(key=lambda x: -x[0])
    return out[:limit]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--limit", type=int, default=8)
    ap.add_argument("--scope")
    ap.add_argument("--w-bm25", type=float, default=0.6)
    a = ap.parse_args()
    vectors = vec.build_index()
    for s, r in search(a.query, a.limit, a.scope, a.w_bm25, vectors):
        print(f"{s:.4f}  {r['id']}  {r['title']}  [{r['page']}]")
        print(f"        {r['definition'][:120]}")
        print(f"        {r['skill_module']} · {r['scope']}")


if __name__ == "__main__":
    main()
