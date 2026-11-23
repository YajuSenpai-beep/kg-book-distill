# -*- coding: utf-8 -*-
"""Compare BM25 / vector / hybrid on 20 paraphrase queries. Run with .venv-embed python."""
import importlib.util, json, os

BASE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.join(BASE, "..")


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, os.path.join(KB, "search", file))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


bm = load("kg_search", "kg_search.py")
vec = load("kg_vector_search", "kg_vector_search.py")
hyb = load("kg_hybrid_vector", "kg_hybrid_vector.py")
ROWS = {r["id"]: r for r in bm.ROWS}
VECTORS = vec.build_index()
ITEMS = [json.loads(x) for x in open(os.path.join(BASE, "semantic_queries.jsonl"), encoding="utf-8") if x.strip()]


def run(engine):
    m = {"n": len(ITEMS), "r1": 0, "r5": 0, "r10": 0, "mrr": 0.0}
    for x in ITEMS:
        if engine == "bm25":
            ranked = [r["id"] for _, r in bm.bm25(x["q"], 10)]
        elif engine == "vector":
            ranked = [r["id"] for _, r in vec.search(x["q"], 10, vectors=VECTORS)]
        else:
            ranked = [r["id"] for _, r in hyb.search(x["q"], 10, vectors=VECTORS)]
        rel = set(x["relevant"])
        m["r1"] += bool(rel & set(ranked[:1]))
        m["r5"] += bool(rel & set(ranked[:5]))
        m["r10"] += bool(rel & set(ranked[:10]))
        rank = next((i + 1 for i, rid in enumerate(ranked) if rid in rel), None)
        m["mrr"] += 1 / rank if rank else 0
    n = m["n"]
    return {k: (v / n if k != "n" else v) for k, v in m.items()}


lines = ["# 语义查询对比（20 条改写问题）\n",
         "| 引擎 | N | Recall@1 | Recall@5 | Recall@10 | MRR |",
         "|---|---:|---:|---:|---:|---:|"]
for e in ["bm25", "vector", "hybrid-vector"]:
    m = run(e)
    lines.append(f"| {e} | {m['n']} | {m['r1']:.3f} | {m['r5']:.3f} | {m['r10']:.3f} | {m['mrr']:.3f} |")
    print(e, m)
open(os.path.join(BASE, "report-semantic.md"), "w", encoding="utf-8").write("\n".join(lines))
