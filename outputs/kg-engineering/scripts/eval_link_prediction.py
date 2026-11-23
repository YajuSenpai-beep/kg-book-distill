# -*- coding: utf-8 -*-
"""Compute MR/MRR/Hit@n for link prediction.

Input JSONL (one test triple per line):
    {"gold": "t1", "ranked": ["t2","t1",...], "relation": "bornIn"}
    {"gold": "t1", "ranked": [...], "filtered_ranked": [...], "relation": "bornIn"}

`ranked` is the raw ranking; `filtered_ranked` removes other true triples.
Usage:
    python eval_link_prediction.py ranks.jsonl [--report report.md]
"""
import argparse, json
from collections import defaultdict


def load(path):
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def metrics(items, key):
    ranks = []
    for x in items:
        seq = x.get(key) or x.get("ranked") or []
        try:
            ranks.append(seq.index(x["gold"]) + 1)
        except ValueError:
            ranks.append(len(seq) + 1)
    if not ranks:
        return None
    n = len(ranks)
    return {
        "n": n,
        "MR": sum(ranks) / n,
        "MRR": sum(1 / r for r in ranks) / n,
        "Hit@1": sum(1 for r in ranks if r <= 1) / n,
        "Hit@3": sum(1 for r in ranks if r <= 3) / n,
        "Hit@10": sum(1 for r in ranks if r <= 10) / n,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ranks")
    ap.add_argument("--report")
    a = ap.parse_args()
    items = load(a.ranks)
    raw = metrics(items, "ranked")
    filt = metrics(items, "filtered_ranked") if any("filtered_ranked" in x for x in items) else None

    lines = ["# 链接预测评估\n", f"- 测试三元组：{len(items)}",
             "\n## 指标\n", "| 口径 | N | MR | MRR | Hit@1 | Hit@3 | Hit@10 |",
             "|---|---:|---:|---:|---:|---:|---:|"]
    for name, m in [("raw", raw), ("filtered", filt)]:
        if m:
            lines.append(f"| {name} | {m['n']} | {m['MR']:.2f} | {m['MRR']:.4f} | "
                         f"{m['Hit@1']:.4f} | {m['Hit@3']:.4f} | {m['Hit@10']:.4f} |")
    # 按关系
    by_rel = defaultdict(list)
    for x in items:
        by_rel[x.get("relation", "未知")].append(x)
    lines += ["\n## 按关系（filtered 优先）\n",
              "| 关系 | N | MR | MRR | Hit@10 |", "|---|---:|---:|---:|---:|"]
    for rel, xs in sorted(by_rel.items(), key=lambda x: -len(x[1])):
        m = metrics(xs, "filtered_ranked") or metrics(xs, "ranked")
        lines.append(f"| {rel} | {m['n']} | {m['MR']:.2f} | {m['MRR']:.4f} | {m['Hit@10']:.4f} |")
    text = "\n".join(lines)
    if a.report:
        with open(a.report, "w", encoding="utf-8") as f:
            f.write(text)
    print(text)


if __name__ == "__main__":
    main()
