# -*- coding: utf-8 -*-
"""Evaluate extracted triples against gold, with micro/macro P/R/F1.

Input JSONL (one doc per line):
    {"doc_id": "d1", "triples": [["h","r","t"], ...]}

Usage:
    python eval_extraction.py gold.jsonl pred.jsonl [--report report.md]
"""
import argparse, json, sys
from collections import defaultdict


def load(path):
    docs = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            x = json.loads(line)
            docs[x["doc_id"]] = {tuple(t) for t in x.get("triples", [])}
    return docs


def prf(tp, fp, fn):
    p = tp / (tp + fp) if tp + fp else 0.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return p, r, f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("gold")
    ap.add_argument("pred")
    ap.add_argument("--report")
    a = ap.parse_args()

    gold, pred = load(a.gold), load(a.pred)
    missing = sorted(set(gold) - set(pred))
    extra = sorted(set(pred) - set(gold))
    docs = sorted(set(gold) & set(pred))

    per_rel = defaultdict(lambda: [0, 0, 0])  # tp, fp, fn
    total_tp = total_fp = total_fn = 0
    for d in docs:
        g, p = gold[d], pred[d]
        tp = g & p
        fp = p - g
        fn = g - p
        total_tp += len(tp); total_fp += len(fp); total_fn += len(fn)
        for _, r, _ in tp: per_rel[r][0] += 1
        for _, r, _ in fp: per_rel[r][1] += 1
        for _, r, _ in fn: per_rel[r][2] += 1

    P, R, F = prf(total_tp, total_fp, total_fn)
    lines = ["# 抽取评估报告\n",
             f"- gold docs: {len(gold)}；pred docs: {len(pred)}；匹配 docs: {len(docs)}",
             f"- gold triples: {sum(len(v) for v in gold.values())}；pred triples: {sum(len(v) for v in pred.values())}",
             f"- 缺失文档: {missing or '无'}", f"- 多余文档: {extra or '无'}",
             "\n## 总体（micro）\n",
             "| TP | FP | FN | Precision | Recall | F1 |", "|---:|---:|---:|---:|---:|---:|",
             f"| {total_tp} | {total_fp} | {total_fn} | {P:.4f} | {R:.4f} | {F:.4f} |",
             "\n## 按关系\n",
             "| 关系 | TP | FP | FN | P | R | F1 |", "|---|---:|---:|---:|---:|---:|---:|"]
    f1s = []
    for rel, (tp, fp, fn) in sorted(per_rel.items(), key=lambda x: -sum(x[1])):
        p, r, f = prf(tp, fp, fn)
        f1s.append(f)
        lines.append(f"| {rel} | {tp} | {fp} | {fn} | {p:.4f} | {r:.4f} | {f:.4f} |")
    macro = sum(f1s) / len(f1s) if f1s else 0.0
    lines += ["", f"**Macro-F1（按关系平均）：{macro:.4f}**", ""]
    text = "\n".join(lines)
    if a.report:
        with open(a.report, "w", encoding="utf-8") as f:
            f.write(text)
    print(text)
    sys.exit(0)


if __name__ == "__main__":
    main()
