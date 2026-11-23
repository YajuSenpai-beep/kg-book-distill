# -*- coding: utf-8 -*-
"""CLIP image/text search over figure/table pages.

Run with the embedding venv:
    .venv-embed\\Scripts\\python.exe image_search.py --text "TransR architecture"
    .venv-embed\\Scripts\\python.exe image_search.py --image path/to/query.jpg
"""
import argparse, importlib.util, json, os
import numpy as np
from fastembed import ImageEmbedding, TextEmbedding

BASE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.dirname(BASE)
FIG_DIR = os.path.join(KB, "figures")
CACHE = os.path.join(FIG_DIR, "multimodal_index.npz")
FIGS = json.load(open(os.path.join(FIG_DIR, "figure-index.json"), encoding="utf-8"))
spec = importlib.util.spec_from_file_location("ex", os.path.join(KB, "search", "exhibit_search.py"))
EX = importlib.util.module_from_spec(spec)
spec.loader.exec_module(EX)
BY_PAGE = {}
for f in FIGS:
    BY_PAGE.setdefault((f["book"], f["page"]), []).append(f)


def load():
    d = np.load(CACHE)
    pages = [json.loads(x) for x in d["page_meta"]]
    return d, pages


def norm(v):
    return v / (np.linalg.norm(v) + 1e-9)


def text_search(q, limit=8, mode="caption"):
    if mode == "caption":
        hits = EX.bm25(q, 50)
        seen, out = set(), []
        for score, f in hits:
            key = (f["book"], f["page"])
            if key in seen:
                continue
            seen.add(key)
            meta = {"book": f["book"], "page": f["page"],
                    "file": f"figures/pages/{f['book']}-{f['page']:03d}.jpg"}
            out.append((float(score), meta, BY_PAGE.get(key, [])))
            if len(out) >= limit:
                break
        if out:
            return out
    d, pages = load()
    m = TextEmbedding(model_name="Qdrant/clip-ViT-B-32-text",
                      cache_dir=os.path.join(KB, "..", ".embed_cache"))
    qv = norm(np.array(list(m.query_embed([q])), dtype="float32")[0])
    sims = d["page_vecs"] @ qv
    idx = np.argsort(-sims)[:limit]
    out = []
    for i in idx:
        p = pages[i]
        figs = BY_PAGE.get((p["book"], p["page"]), [])
        out.append((float(sims[i]), p, figs))
    return out


def image_search(path, limit=8):
    d, pages = load()
    m = ImageEmbedding(model_name="Qdrant/clip-ViT-B-32-vision",
                       cache_dir=os.path.join(KB, "..", ".embed_cache"))
    qv = norm(np.array(list(m.embed([path])), dtype="float32")[0])
    sims = d["page_vecs"] @ qv
    idx = np.argsort(-sims)[:limit]
    out = []
    for i in idx:
        p = pages[i]
        out.append((float(sims[i]), p, BY_PAGE.get((p["book"], p["page"]), [])))
    return out


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--text")
    g.add_argument("--image")
    ap.add_argument("--limit", type=int, default=8)
    ap.add_argument("--mode", choices=["caption", "clip"], default="caption")
    a = ap.parse_args()
    rows = text_search(a.text, a.limit, a.mode) if a.text else image_search(a.image, a.limit)
    for s, p, figs in rows:
        labels = "；".join(f"{f['number']} {f['caption'][:24]}" for f in figs[:3])
        print(f"{s:.3f}  {p['book']}-{p['page']}  {p['file']}")
        print(f"        {labels}")


if __name__ == "__main__":
    main()
