# -*- coding: utf-8 -*-
"""Answer-level evaluation for the extractive answer engine.

Metrics: keyword coverage (answer correctness proxy), citation precision/recall,
citation validity. Not an LLM answer-quality eval.
"""
import importlib.util, json, os

BASE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.dirname(BASE)
spec = importlib.util.spec_from_file_location("ans", os.path.join(BASE, "answer_engine.py"))
ans = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ans)
ITEMS = [json.loads(x) for x in open(os.path.join(BASE, "qa_gold.jsonl"), encoding="utf-8") if x.strip()]


def run(threshold):
    kw = cp = cr = valid = 0.0
    rows = []
    for x in ITEMS:
        text, cites = ans.answer(x["q"], threshold=threshold)
        hit = sum(1 for k in x["keywords"] if k.lower() in text.lower())
        cov = hit / max(len(x["keywords"]), 1)
        gold = set(x["relevant"])
        cited = set(cites)
        p = len(cited & gold) / max(len(cited), 1)
        r = len(cited & gold) / max(len(gold), 1)
        v = all(c in ans.ROWS or c.startswith("TAB-") for c in cites)
        kw += cov; cp += p; cr += r; valid += bool(v)
        rows.append((x["q"], cov, p, r, cites))
    n = len(ITEMS)
    return kw / n, cp / n, cr / n, valid / n, rows


def main():
    a = run(0.0)
    b = run(0.6)
    lines = ["# 答案级评估（抽取式）\n",
             "| 模式 | 关键词覆盖 | 引用精确率 | 引用召回率 | 引用有效性 |",
             "|---|---:|---:|---:|---:|",
             f"| 覆盖优先（threshold=0） | {a[0]:.3f} | {a[1]:.3f} | {a[2]:.3f} | {a[3]:.3f} |",
             f"| 引用优先（threshold=0.6） | {b[0]:.3f} | {b[1]:.3f} | {b[2]:.3f} | {b[3]:.3f} |",
             "\n口径：抽取式答案，不是生成式；不评流畅性/幻觉，只评覆盖与引用。\n",
             "## 引用优先模式下的低覆盖问题\n"]
    for q, cov, p, r, cites in b[4]:
        if cov < 1.0:
            lines.append(f"- {q} | 覆盖 {cov:.2f} | 引用 {cites}")
    open(os.path.join(BASE, "report-answer-quality.md"), "w", encoding="utf-8").write("\n".join(lines))
    print(f"coverage {a[0]:.3f}/{b[0]:.3f} citation_p {a[1]:.3f}/{b[1]:.3f} "
          f"citation_r {a[2]:.3f}/{b[2]:.3f}")


if __name__ == "__main__":
    main()
