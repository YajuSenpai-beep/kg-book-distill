# -*- coding: utf-8 -*-
"""Evaluate neural vector and BM25+vector hybrid retrieval. Run with .venv-embed python."""
import argparse, importlib.util, json, os
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.join(BASE, "..")


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, os.path.join(KB, "search", file))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


vec = load("kg_vector_search", "kg_vector_search.py")
hyb = load("kg_hybrid_vector", "kg_hybrid_vector.py")
ROWS = {r["id"]: r for r in vec.ROWS}
VECTORS = vec.build_index()


def load_jsonl(path):
    return [json.loads(x) for x in open(path, encoding="utf-8") if x.strip()]


def evaluate(path, engine, k_max=10):
    items = load_jsonl(path)
    m = {"n": len(items), "r1": 0, "r5": 0, "r10": 0, "mrr": 0.0}
    fails = []
    for x in items:
        if engine == "vector":
            ranked = [r["id"] for _, r in vec.search(x["q"], k_max, vectors=VECTORS)]
        else:
            ranked = [r["id"] for _, r in hyb.search(x["q"], k_max, vectors=VECTORS)]
        rel = set(x["relevant"])
        h1, h5, h10 = bool(rel & set(ranked[:1])), bool(rel & set(ranked[:5])), bool(rel & set(ranked[:10]))
        rank = next((i + 1 for i, rid in enumerate(ranked) if rid in rel), None)
        m["r1"] += h1; m["r5"] += h5; m["r10"] += h10; m["mrr"] += 1 / rank if rank else 0
        if not h5:
            fails.append((x["q"], x["relevant"], ranked[:5]))
    n = max(m["n"], 1)
    return {k: (v / n if k != "n" else v) for k, v in m.items()}, fails


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", choices=["vector", "hybrid-vector"], default="hybrid-vector")
    a = ap.parse_args()
    ret, rf = evaluate(os.path.join(BASE, "retrieval_queries.jsonl"), a.engine)
    qa, qf = evaluate(os.path.join(BASE, "qa_questions.jsonl"), a.engine)
    lines = [f"# 检索 / QA 评测（{a.engine}）\n", "| 集合 | N | Recall@1 | Recall@5 | Recall@10 | MRR |",
             "|---|---:|---:|---:|---:|---:|"]
    for name, m in [("检索集", ret), ("QA 集", qa)]:
        lines.append(f"| {name} | {m['n']} | {m['r1']:.3f} | {m['r5']:.3f} | {m['r10']:.3f} | {m['mrr']:.3f} |")
    lines += ["\n## QA 失败样例\n"]
    for q, rel, top in qf[:10]:
        lines.append(f"- {q} | 期望 {rel} | 实际 {top}")
    out = os.path.join(BASE, f"report-{a.engine}.md")
    open(out, "w", encoding="utf-8").write("\n".join(lines))
    print(a.engine, "retrieval", ret)
    print(a.engine, "qa", qa)


if __name__ == "__main__":
    main()
