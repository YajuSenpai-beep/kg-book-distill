# -*- coding: utf-8 -*-
"""Evaluate generated answers: keyword coverage, citation precision/recall,
validity, refusal rate."""
import argparse, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from citation_check import sentences, support

BASE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.dirname(BASE)
GOLD = {json.loads(x)["q"]: json.loads(x) for x in open(os.path.join(KB, "eval", "qa_gold.jsonl"),
                                                        encoding="utf-8") if x.strip()}
ap = argparse.ArgumentParser()
ap.add_argument("--answers", default=os.path.join(BASE, "answers-generated.jsonl"))
ARGS = ap.parse_args()
ANS = [json.loads(x) for x in open(ARGS.answers, encoding="utf-8") if x.strip()]
CTX = {}
CTX_TEXT = {}
if os.path.exists(os.path.join(BASE, "contexts.json")):
    for x in json.load(open(os.path.join(BASE, "contexts.json"), encoding="utf-8")):
        CTX[x["q"]] = set(x["ids"])
        CTX_TEXT[x["q"]] = {c["id"]: c["text"] for c in x["contexts"]}


def main():
    kw = cp = cr = valid = refused = support_sum = 0.0
    rows = []
    for a in ANS:
        g = GOLD.get(a["q"])
        if not g:
            continue
        text = a.get("answer", "")
        cov = sum(1 for k in g["keywords"] if k.lower() in text.lower()) / max(len(g["keywords"]), 1)
        gold = set(g["relevant"])
        cited = set(a.get("citations", []))
        p = len(cited & gold) / max(len(cited), 1)
        r = len(cited & gold) / max(len(gold), 1)
        allowed = set(a.get("context_ids", [])) or CTX.get(a["q"], set())
        v = all(c in allowed for c in cited)
        sup = 0.0
        sents = sentences(text)
        for c in cited:
            inline = [s for s in sents if f"[{c}]" in s]
            ctx = CTX_TEXT.get(a["q"], {}).get(c, "")
            sup += max((support(s.replace(f"[{c}]", ""), ctx) for s in inline), default=0.0)
        sup = sup / max(len(cited), 1)
        kw += cov; cp += p; cr += r; valid += bool(v); support_sum += sup
        refused += bool(a.get("insufficient"))
        rows.append((a["q"], cov, p, r, a.get("citations", []), a.get("insufficient")))
    n = len(rows) or 1
    provider = ANS[0].get("provider", "agent") if ANS else "?"
    model = ANS[0].get("model", ARGS.answers) if ANS else "?"
    lines = ["# 生成式答案评估\n",
             f"- Provider：{provider} / {model}",
             f"- 问题：{len(rows)}",
             f"- 关键词覆盖：{kw/n:.3f}",
             f"- 引用精确率：{cp/n:.3f}",
             f"- 引用召回率：{cr/n:.3f}",
             f"- 引用有效性：{valid/n:.3f}",
             f"- 拒答率（insufficient）：{refused/n:.3f}",
             f"- 引用句支持度（词面代理）：{support_sum/n:.3f}",
             "\n口径：关键词覆盖是答案正确性的代理；引用精确/召回按 gold 点计算；"
             "引用有效性要求引用 ID 出现在检索上下文中。\n",
             "## 低覆盖问题\n"]
    for q, cov, p, r, cites, ins in rows:
        if cov < 1.0:
            lines.append(f"- {q} | 覆盖 {cov:.2f} | 引用 {cites} | insufficient={ins}")
    open(os.path.join(BASE, "report-generated.md"), "w", encoding="utf-8").write("\n".join(lines))
    print(f"coverage {kw/n:.3f} citation_p {cp/n:.3f} citation_r {cr/n:.3f} "
          f"valid {valid/n:.3f} refused {refused/n:.3f}")


if __name__ == "__main__":
    main()
