# -*- coding: utf-8 -*-
"""Context-level answer evaluation: does top-k retrieval contain the gold
knowledge points needed to answer? This is not an LLM answer-quality eval.

Outputs: eval/report-answer-context.md
"""
import importlib.util, json, os

BASE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.dirname(BASE)


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, os.path.join(KB, "search", file))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


kg = load("kg_search", "kg_search.py")
ITEMS = [json.loads(x) for x in open(os.path.join(BASE, "qa_questions.jsonl"),
                                    encoding="utf-8") if x.strip()]


def main():
    k = 5
    hit = 0
    support_sum = 0.0
    precision_sum = 0.0
    rows = []
    for x in ITEMS:
        ranked = [r["id"] for _, r in kg.bm25(x["q"], k)]
        gold = set(x["relevant"])
        found = gold & set(ranked)
        sup = len(found) / max(len(gold), 1)
        prec = len(found) / max(len(ranked), 1)
        hit += bool(found)
        support_sum += sup
        precision_sum += prec
        rows.append((x["q"], sorted(gold), ranked, sup, prec))
    n = len(ITEMS)
    lines = ["# 上下文级答案评估\n",
             f"- 问题：{n}",
             f"- k：{k}",
             f"- 命中率（top-{k} 含任一 gold）：{hit/n:.3f}",
             f"- 支持覆盖率（gold 点被召回的比例）：{support_sum/n:.3f}",
             f"- 上下文精确率（召回中 gold 的占比）：{precision_sum/n:.3f}",
             "\n口径：只评估检索上下文是否覆盖回答所需知识点，不评估生成答案的措辞与忠实性。\n",
             "## 未覆盖问题\n"]
    for q, gold, ranked, sup, prec in rows:
        if sup < 1.0:
            lines.append(f"- {q} | gold {gold} | top {ranked} | support {sup:.2f}")
    open(os.path.join(BASE, "report-answer-context.md"), "w", encoding="utf-8").write("\n".join(lines))
    print(f"hit {hit/n:.3f} support {support_sum/n:.3f} precision {precision_sum/n:.3f}")


if __name__ == "__main__":
    main()
