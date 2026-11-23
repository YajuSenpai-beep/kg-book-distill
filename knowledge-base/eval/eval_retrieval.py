# -*- coding: utf-8 -*-
"""Evaluate BM25 retrieval on the 100-query set and 30-question QA set."""
import argparse, importlib.util, json, os
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.join(BASE, "..")


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, os.path.join(KB, "search", file))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


kg = load("kg_search", "kg_search.py")
hybrid = load("kg_hybrid_search", "kg_hybrid_search.py")
lsa = load("kg_lsa_search", "kg_lsa_search.py")
ROWS = {r["id"]: r for r in kg.ROWS}


def load(path):
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def evaluate(path, k_max=10, engine="bm25"):
    items = load(path)
    missing = []
    for x in items:
        for rid in x["relevant"]:
            if rid not in ROWS:
                missing.append((x["q"], rid))
    metrics = {"n": len(items), "r1": 0, "r5": 0, "r10": 0, "mrr": 0.0}
    by_scope = defaultdict(lambda: {"n": 0, "r1": 0, "r5": 0, "r10": 0, "mrr": 0.0})
    failures = []
    for x in items:
        if engine == "hybrid":
            ranked = [r["id"] for _, r in hybrid.search(x["q"], limit=k_max)]
        elif engine == "lsa":
            ranked = [r["id"] for _, r in lsa.search(x["q"], limit=k_max)]
        else:
            ranked = [r["id"] for _, r in kg.bm25(x["q"], limit=k_max)]
        rel = set(x["relevant"])
        hit1 = bool(rel & set(ranked[:1]))
        hit5 = bool(rel & set(ranked[:5]))
        hit10 = bool(rel & set(ranked[:10]))
        rank = next((i + 1 for i, rid in enumerate(ranked) if rid in rel), None)
        rr = 1.0 / rank if rank else 0.0
        metrics["r1"] += hit1; metrics["r5"] += hit5; metrics["r10"] += hit10; metrics["mrr"] += rr
        s = x.get("scope", "未知")
        by_scope[s]["n"] += 1
        by_scope[s]["r1"] += hit1; by_scope[s]["r5"] += hit5; by_scope[s]["r10"] += hit10; by_scope[s]["mrr"] += rr
        if not hit5:
            failures.append((x["q"], x["relevant"], ranked[:5]))
    n = max(metrics["n"], 1)
    summary = {k: (v / n if k != "n" else v) for k, v in metrics.items()}
    for s, m in by_scope.items():
        nn = max(m["n"], 1)
        for k in ("r1", "r5", "r10", "mrr"):
            m[k] = m[k] / nn
    return summary, dict(by_scope), failures, missing


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--engine", choices=["bm25", "hybrid", "lsa"], default="bm25")
    a = ap.parse_args()
    ret_sum, ret_scope, ret_fail, ret_missing = evaluate(
        os.path.join(BASE, "retrieval_queries.jsonl"), engine=a.engine)
    qa_sum, qa_scope, qa_fail, qa_missing = evaluate(
        os.path.join(BASE, "qa_questions.jsonl"), engine=a.engine)

    lines = [f"# 检索 / QA 基线评测（{a.engine}）\n", "## 指标口径\n",
             "- Recall@k：前 k 条中是否包含任一相关知识点。",
             "- MRR：第一条相关知识的排名倒数。",
             "- 检索集：100 条由知识点关键短语构成的 smoke 查询。",
             "- QA 集：30 条人工编写的问题，用“前 k 是否命中相关知识点”做检索级评估。\n",
             "## 总体\n", "| 集合 | N | Recall@1 | Recall@5 | Recall@10 | MRR |",
             "|---|---:|---:|---:|---:|---:|"]
    for name, s in [("检索集", ret_sum), ("QA 集", qa_sum)]:
        lines.append(f"| {name} | {s['n']} | {s['r1']:.3f} | {s['r5']:.3f} | {s['r10']:.3f} | {s['mrr']:.3f} |")
    lines += ["\n## 按范围（检索集）\n", "| 范围 | N | Recall@1 | Recall@5 | Recall@10 | MRR |",
              "|---|---:|---:|---:|---:|---:|"]
    for scope, m in sorted(ret_scope.items()):
        lines.append(f"| {scope} | {m['n']} | {m['r1']:.3f} | {m['r5']:.3f} | {m['r10']:.3f} | {m['mrr']:.3f} |")
    lines += ["\n## 失败样例（QA 集，前 5 未命中）\n"]
    if qa_fail:
        for q, rel, top in qa_fail[:10]:
            lines.append(f"- {q} | 期望 {rel} | 实际 {top}")
    else:
        lines.append("- 无")
    lines += ["\n## 引用完整性\n"]
    lines.append(f"- 检索集缺失 ID：{ret_missing or '无'}")
    lines.append(f"- QA 集缺失 ID：{qa_missing or '无'}")
    out = "report.md" if a.engine == "bm25" else f"report-{a.engine}.md"
    with open(os.path.join(BASE, out), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(a.engine, "retrieval", {k: round(v, 3) if isinstance(v, float) else v for k, v in ret_sum.items()})
    print("qa", {k: round(v, 3) if isinstance(v, float) else v for k, v in qa_sum.items()})
    print("missing", len(ret_missing), len(qa_missing), "failures(qa)", len(qa_fail))


if __name__ == "__main__":
    main()
