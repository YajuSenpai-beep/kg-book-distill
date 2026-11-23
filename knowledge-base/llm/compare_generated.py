# -*- coding: utf-8 -*-
"""Compare all answers-gen-*.jsonl on the 15 gold QA."""
import glob, json, os

BASE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.dirname(BASE)
GOLD = {json.loads(x)["q"]: json.loads(x) for x in open(os.path.join(KB, "eval", "qa_gold.jsonl"),
                                                        encoding="utf-8") if x.strip()}
CTX = {x["q"]: set(x["ids"]) for x in json.load(open(os.path.join(BASE, "contexts.json"),
                                                     encoding="utf-8"))}


def score(path):
    ans = [json.loads(x) for x in open(path, encoding="utf-8") if x.strip()]
    kw = cp = cr = valid = refused = 0.0
    for a in ans:
        g = GOLD.get(a["q"])
        if not g:
            continue
        text = a.get("answer", "")
        cov = sum(1 for k in g["keywords"] if k.lower() in text.lower()) / max(len(g["keywords"]), 1)
        gold = set(g["relevant"])
        cited = set(a.get("citations", []))
        cp += len(cited & gold) / max(len(cited), 1)
        cr += len(cited & gold) / max(len(gold), 1)
        allowed = set(a.get("context_ids", [])) or CTX.get(a["q"], set())
        valid += all(c in allowed for c in cited)
        refused += bool(a.get("insufficient"))
        kw += cov
    n = len(ans) or 1
    return kw / n, cp / n, cr / n, valid / n, refused / n


def main():
    rows = []
    for p in sorted(glob.glob(os.path.join(BASE, "answers-gen-*.jsonl"))):
        rows.append((os.path.basename(p).replace("answers-gen-", "").replace(".jsonl", ""), score(p)))
    lines = ["# 生成式答案对比（15 条 gold QA）\n",
             "| 来源 | 关键词覆盖 | 引用精确率 | 引用召回率 | 引用有效性 | 拒答率 |",
             "|---|---:|---:|---:|---:|---:|",
             "| 抽取式·覆盖优先 | 0.756 | 0.439 | 0.660 | 1.000 | 0.000 |",
             "| 抽取式·引用优先 | 0.622 | 0.700 | 0.516 | 1.000 | 0.000 |"]
    for name, s in rows:
        lines.append(f"| 生成式·{name} | {s[0]:.3f} | {s[1]:.3f} | {s[2]:.3f} | {s[3]:.3f} | {s[4]:.3f} |")
    lines += ["\n口径：关键词覆盖是正确性代理；引用精确/召回按 gold 点计算；"
              "引用有效性要求引用 ID 在检索上下文中。\n",
              "结论：生成式提高覆盖，但引用精确率仍低于“引用优先”抽取式；"
              "DeepSeek（点优先 + 最多 4 引用 + 句内过滤）在生成式中引用精确率最高（0.589），"
              "Opus 覆盖最高（0.889）但引用最弱（0.367）。"]
    open(os.path.join(BASE, "report-generated-compare.md"), "w", encoding="utf-8").write("\n".join(lines))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
