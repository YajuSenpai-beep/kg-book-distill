# -*- coding: utf-8 -*-
"""Unified BM25 + optional BGE + optional cross-encoder rerank.

Indexes: knowledge points, figures, tables, glossary terms, instance methods.
Run with the embedding venv for vector/rerank:
    ..\\.venv-embed\\Scripts\\python.exe unified_search.py "TransR 结果" --limit 5
System Python still works with BM25 fallback.
"""
import argparse, hashlib, json, math, os, re
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.dirname(BASE)


def load(path):
    return json.load(open(path, encoding="utf-8"))


ROWS = load(os.path.join(KB, "kg-knowledge-points.json"))
FIGS = load(os.path.join(KB, "figures", "figure-index.json"))
TABLES = {t["id"]: t for t in load(os.path.join(KB, "tables", "table-data.json"))["tables"]}
TERMS = load(os.path.join(KB, "glossary", "terms.json"))["terms"]
INST = load(os.path.join(KB, "instances", "instance-graph.json"))["nodes"]

DOCS = []
for r in ROWS:
    DOCS.append({"id": r["id"], "kind": "point", "title": r["title"],
                 "text": " ".join([r["title"], r["definition"], r["key_points"], r["formula"],
                                   r["chapter_title"], r["section_title"], r["type"]]),
                 "book": r["book"], "page": r["page"], "type": r["type"]})
for f in FIGS:
    t = TABLES.get(f["id"], {})
    DOCS.append({"id": f["id"], "kind": "table" if f["kind"] == "表" else "figure",
                 "title": f"{f['number']} {f['caption']}",
                 "text": " ".join([f["caption"], f["role"], f["section_title"], f.get("note", ""),
                                   f.get("context", ""), " ".join(f.get("linked_points", [])),
                                   " ".join(t.get("columns", []))]),
                 "book": f["book"], "page": f["page"], "type": f["role"]})
for x in TERMS:
    DOCS.append({"id": "TERM-" + x["term"], "kind": "term", "title": x["term"],
                 "text": " ".join([x["term"], x["en"], " ".join(x.get("aliases", []))]),
                 "book": "", "page": "", "type": x["category"]})
for n in INST:
    if n["type"] in ("Method", "Task", "Dataset", "Metric"):
        DOCS.append({"id": n["id"], "kind": n["type"].lower(), "title": n["label"],
                     "text": " ".join([n["label"], n.get("aliases", "") if isinstance(n.get("aliases"), str)
                                       else " ".join(n.get("aliases", []))]),
                     "book": n.get("book", ""), "page": n.get("page", ""), "type": n["type"]})


def tokens(text):
    text = text.lower()
    out = re.findall(r"[a-z0-9]+", text)
    for run in re.findall(r"[一-鿿]+", text):
        out.extend(run)
        out.extend(run[i:i + 2] for i in range(len(run) - 1))
    return out


DOCS_BY_ID = {d["id"]: d for d in DOCS}
TFS = [Counter(tokens(d["text"])) for d in DOCS]
TITLE_TFS = [Counter(tokens(d["title"])) for d in DOCS]
N = len(DOCS)
AVG = sum(sum(tf.values()) for tf in TFS) / max(N, 1)
DF = Counter()
for tf in TFS:
    for t in tf:
        DF[t] += 1


def bm25(query, limit=50):
    q = tokens(query)
    ql = query.lower()
    latin_q = [t for t in q if re.fullmatch(r"[a-z0-9]+", t)]
    scored = []
    for i, d in enumerate(DOCS):
        tf, ttf = TFS[i], TITLE_TFS[i]
        dl = sum(tf.values())
        s = 0.0
        for t in q:
            idf = math.log(1 + (N - DF[t] + 0.5) / (DF[t] + 0.5))
            if t in tf:
                s += idf * tf[t] * 2.5 / (tf[t] + 1.5 * (0.25 + 0.75 * dl / max(AVG, 1e-9)))
            if t in ttf:
                s += idf * 2.2
        latin_hits = sum(1 for t in latin_q if t in tf or t in ttf)
        if latin_q:
            s = s * 0.25 if latin_hits == 0 else s + 15.0 * latin_hits
        if ql and ql in (d["title"] + " " + d["text"]).lower():
            s += 6.0
        if s > 0:
            scored.append((s, i))
    scored.sort(key=lambda x: -x[0])
    return scored[:limit]


_EMB = None
_RER = None
_LOADED = False


def load_models():
    global _EMB, _RER, _LOADED
    if _LOADED:
        return _EMB, _RER
    _LOADED = True
    try:
        from fastembed import TextEmbedding
        from fastembed.rerank.cross_encoder import TextCrossEncoder
        _EMB = TextEmbedding(model_name="BAAI/bge-small-zh-v1.5",
                             cache_dir=os.path.join(KB, "..", ".embed_cache"))
        _RER = TextCrossEncoder(model_name="BAAI/bge-reranker-base",
                                cache_dir=os.path.join(KB, "..", ".embed_cache"))
    except Exception:
        _EMB, _RER = None, None
    return _EMB, _RER


FORCE_REBUILD = False


def source_hash():
    h = hashlib.sha1()
    for p in [os.path.join(KB, "kg-knowledge-points.json"),
              os.path.join(KB, "figures", "figure-index.json"),
              os.path.join(KB, "tables", "table-data.json"),
              os.path.join(KB, "glossary", "terms.json"),
              os.path.join(KB, "instances", "instance-graph.json")]:
        h.update(os.path.basename(p).encode())
        h.update(open(p, "rb").read())
    return h.hexdigest()


def vector_scores(query, emb):
    cache = os.path.join(BASE, "unified_vectors.npz")
    import numpy as np
    if os.path.exists(cache) and not FORCE_REBUILD:
        d = np.load(cache)
        vecs = d["vectors"]
        if len(vecs) == len(DOCS) and str(d.get("source_hash", "")) == source_hash():
            q = np.array(list(emb.query_embed(["为这个句子生成表示以用于检索相关文章：" + query])),
                         dtype="float32")[0]
            q /= np.linalg.norm(q) + 1e-9
            return vecs @ q
    vecs = np.array(list(emb.embed([d["text"] for d in DOCS], batch_size=32)), dtype="float32")
    vecs /= np.linalg.norm(vecs, axis=1, keepdims=True) + 1e-9
    np.savez(cache, vectors=vecs, source_hash=source_hash(), count=len(DOCS))
    q = np.array(list(emb.query_embed(["为这个句子生成表示以用于检索相关文章：" + query])),
                 dtype="float32")[0]
    q /= np.linalg.norm(q) + 1e-9
    return vecs @ q


def search(query, limit=8, kind=None, rerank=True):
    base = bm25(query, 50)
    if not base:
        return []
    emb, rer = load_models()
    cand = base
    if emb is not None:
        try:
            import numpy as np
            vs = vector_scores(query, emb)
            mx = max((s for s, _ in base), default=1.0)
            merged = {}
            for s, i in base:
                merged[i] = 0.55 * (s / mx) + 0.45 * float(vs[i])
            cand = sorted(((s, i) for i, s in merged.items()), reverse=True)[:30]
        except Exception:
            pass
    if rerank and rer is not None and len(cand) > 1:
        try:
            docs = [DOCS[i]["text"][:600] for _, i in cand[:20]]
            scores = list(rer.rerank(query, docs))
            mx = max(scores) if scores else 1.0
            reranked = [(0.7 * (sc / mx) + 0.3 * (bs / max(cand[0][0], 1e-9)), i)
                        for (bs, i), sc in zip(cand[:20], scores)]
            cand = sorted(reranked, reverse=True) + cand[20:]
        except Exception:
            pass
    out = []
    for s, i in cand:
        d = DOCS[i]
        if kind and d["kind"] != kind:
            continue
        out.append((s, d))
        if len(out) >= limit:
            break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--limit", type=int, default=8)
    ap.add_argument("--kind", choices=["point", "figure", "table", "term", "method",
                                       "task", "dataset", "metric"])
    ap.add_argument("--no-rerank", action="store_true")
    ap.add_argument("--rebuild", action="store_true")
    a = ap.parse_args()
    global FORCE_REBUILD
    FORCE_REBUILD = a.rebuild
    for s, d in search(a.query, a.limit, a.kind, not a.no_rerank):
        print(f"{s:6.3f}  {d['id']:18s} [{d['kind']}] {d['title']}  p.{d['page']}")
        print(f"        {d['text'][:140]}")


if __name__ == "__main__":
    main()
