# -*- coding: utf-8 -*-
"""Neural vector search with fastembed + BAAI/bge-small-zh-v1.5.

Run with the embedding venv:
    ..\\.venv-embed\\Scripts\\python.exe kg_vector_search.py "查询"

First run builds `vector_index.npz`; later runs reuse it. Use --rebuild to refresh.
"""
import argparse, hashlib, json, os, sys
import numpy as np
from fastembed import TextEmbedding

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.join(BASE, "..")
ROWS = json.load(open(os.path.join(KB, "kg-knowledge-points.json"), encoding="utf-8"))
DOCS = [
    " ".join([r["title"], r["definition"], r["key_points"], r["formula"],
              r["chapter_title"], r["section_title"], r["type"]])
    for r in ROWS
]
CACHE = os.path.join(BASE, "vector_index.npz")
MODEL = "BAAI/bge-small-zh-v1.5"
PREFIX = "为这个句子生成表示以用于检索相关文章："


def get_model():
    return TextEmbedding(model_name=MODEL, cache_dir=os.path.join(KB, "..", ".embed_cache"))


def source_hash():
    h = hashlib.sha1()
    for p in [os.path.join(KB, "kg-knowledge-points.json")]:
        h.update(open(p, "rb").read())
    return h.hexdigest()


def build_index(force=False):
    if os.path.exists(CACHE) and not force:
        d = np.load(CACHE)
        if len(d["vectors"]) == len(ROWS) and str(d.get("source_hash", "")) == source_hash():
            return d["vectors"]
    model = get_model()
    vecs = np.array(list(model.embed(DOCS, batch_size=32)), dtype="float32")
    vecs /= np.linalg.norm(vecs, axis=1, keepdims=True) + 1e-9
    np.savez(CACHE, vectors=vecs, source_hash=source_hash(), count=len(ROWS))
    return vecs


def search(query, limit=8, scope=None, vectors=None):
    model = get_model()
    q = np.array(list(model.query_embed([PREFIX + query])), dtype="float32")[0]
    q /= np.linalg.norm(q) + 1e-9
    sims = vectors @ q
    idx = np.argsort(-sims)
    out = []
    for i in idx:
        r = ROWS[i]
        if scope and r["scope"] != scope:
            continue
        out.append((float(sims[i]), r))
        if len(out) >= limit:
            break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--limit", type=int, default=8)
    ap.add_argument("--scope")
    ap.add_argument("--rebuild", action="store_true")
    a = ap.parse_args()
    vecs = build_index(a.rebuild)
    for s, r in search(a.query, a.limit, a.scope, vecs):
        print(f"{s:.4f}  {r['id']}  {r['title']}  [{r['page']}]")
        print(f"        {r['definition'][:120]}")
        print(f"        {r['skill_module']} · {r['scope']}")


if __name__ == "__main__":
    main()
