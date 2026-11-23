# -*- coding: utf-8 -*-
"""Multi-query retrieval: original + glossary aliases + keyword-only, then rerank once."""
import importlib.util, json, os, re

BASE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.dirname(BASE)
spec = importlib.util.spec_from_file_location("u", os.path.join(BASE, "unified_search.py"))
u = importlib.util.module_from_spec(spec)
spec.loader.exec_module(u)
TERMS = json.load(open(os.path.join(KB, "glossary", "terms.json"), encoding="utf-8"))["terms"]
STOP = ["怎么", "如何", "什么", "哪些", "为什么", "应该", "可以", "有哪", "是什么", "分别", "主要"]


def variants(q):
    out = [q]
    ql = q.lower()
    for t in TERMS:
        names = [t["term"], t["en"]] + t.get("aliases", [])
        hit = [n for n in names if n and n.lower() in ql]
        if hit:
            for n in names:
                if n and n not in hit:
                    out.append(ql.replace(hit[0].lower(), n.lower(), 1))
    kw = q
    for s in STOP:
        kw = kw.replace(s, " ")
    kw = re.sub(r"[？?，,。！!、]", " ", kw).strip()
    if kw and kw != q:
        out.append(kw)
    seen, uniq = set(), []
    for v in out:
        v = v.strip()
        if v and v not in seen:
            seen.add(v)
            uniq.append(v)
    return uniq[:6]


def search(q, limit=10, kind=None):
    merged = {}
    for v in variants(q):
        for rank, (s, d) in enumerate(u.search(v, 12, kind, rerank=False)):
            merged[d["id"]] = merged.get(d["id"], 0.0) + 1.0 / (60 + rank)
    cand = sorted(((s, u.DOCS_BY_ID[did]) for did, s in merged.items()), key=lambda x: -x[0])[:24]
    # one cross-encoder rerank pass if available
    emb, rer = u.load_models()
    if rer is not None and len(cand) > 1:
        try:
            docs = [d["text"][:600] for _, d in cand]
            scores = list(rer.rerank(q, docs))
            mx = max(scores) if scores else 1.0
            cand = sorted(((0.7 * sc / mx + 0.3 * bs / max(cand[0][0], 1e-9), d)
                           for (bs, d), sc in zip(cand, scores)), key=lambda x: -x[0])
        except Exception:
            pass
    return cand[:limit]


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--limit", type=int, default=8)
    a = ap.parse_args()
    print("variants:", variants(a.query))
    for s, d in search(a.query, a.limit):
        print(f"{s:.3f} {d['id']} [{d['kind']}] {d['title']}")
