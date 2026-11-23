# -*- coding: utf-8 -*-
"""Compare unified search vs multi-query retrieval on 30 QA."""
import importlib.util, json, os

BASE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.dirname(BASE)
spec = importlib.util.spec_from_file_location("mq", os.path.join(KB, "search", "multi_query.py"))
mq = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mq)
u = mq.u
ITEMS = [json.loads(x) for x in open(os.path.join(BASE, "qa_questions.jsonl"), encoding="utf-8")
         if x.strip()]


def score(fn, k):
    hit = sup = prec = 0.0
    for x in ITEMS:
        ids = [d["id"] for _, d in fn(x["q"], k)]
        gold = set(x["relevant"])
        found = gold & set(ids)
        hit += bool(found); sup += len(found) / max(len(gold), 1)
        prec += len(found) / max(len(ids), 1)
    n = len(ITEMS)
    return hit / n, sup / n, prec / n


def main():
    lines = ["# 统一检索 vs 多查询分解\n",
             "| 引擎 | k | 命中率 | 支持覆盖 | 上下文精确率 |",
             "|---|---:|---:|---:|---:|"]
    for name, fn in [("unified", lambda q, k: u.search(q, k)),
                     ("multi-query", lambda q, k: mq.search(q, k))]:
        for k in (10, 15):
            h, s, p = score(fn, k)
            lines.append(f"| {name} | {k} | {h:.3f} | {s:.3f} | {p:.3f} |")
    open(os.path.join(BASE, "report-multi-query.md"), "w", encoding="utf-8").write("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
