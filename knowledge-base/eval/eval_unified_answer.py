# -*- coding: utf-8 -*-
"""Context-level answer eval with unified search + optional BGE/reranker.

Run with the embedding venv for vector/rerank:
    .venv-embed\\Scripts\\python.exe eval_unified_answer.py
"""
import importlib.util, json, os

BASE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.dirname(BASE)
spec = importlib.util.spec_from_file_location("unified", os.path.join(KB, "search", "unified_search.py"))
u = importlib.util.module_from_spec(spec)
spec.loader.exec_module(u)
ITEMS = [json.loads(x) for x in open(os.path.join(BASE, "qa_questions.jsonl"), encoding="utf-8")
         if x.strip()]


def main():
    k = 15
    hit = support = precision = 0.0
    rows = []
    for x in ITEMS:
        ranked = u.search(x["q"], k)
        ids = [d["id"] for _, d in ranked]
        gold = set(x["relevant"])
        found = gold & set(ids)
        sup = len(found) / max(len(gold), 1)
        prec = len(found) / max(len(ids), 1)
        hit += bool(found)
        support += sup
        precision += prec
        rows.append((x["q"], sorted(gold), ids, sup, prec))
    n = len(ITEMS)
    lines = ["# 统一检索 + 重排的上下文答案评估\n",
             f"- 问题：{n}",
             f"- k：{k}",
             f"- 命中率：{hit/n:.3f}",
             f"- 支持覆盖率：{support/n:.3f}",
             f"- 上下文精确率：{precision/n:.3f}",
             "\n口径：只评估检索上下文是否覆盖回答所需知识点，不评估生成答案措辞。\n",
             "## 未完全覆盖\n"]
    for q, gold, ids, sup, prec in rows:
        if sup < 1.0:
            lines.append(f"- {q} | gold {gold} | top {ids} | support {sup:.2f}")
    open(os.path.join(BASE, "report-unified-answer.md"), "w", encoding="utf-8").write("\n".join(lines))
    print(f"hit {hit/n:.3f} support {support/n:.3f} precision {precision/n:.3f}")


if __name__ == "__main__":
    main()
