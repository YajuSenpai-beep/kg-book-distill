# -*- coding: utf-8 -*-
"""Score a blind backtest answer file against expected concept phrases.

Usage:
    python grade_backtest.py answers.json [--md report.md]

answers.json: JSON array, each item has id, decision, actions (list), evidence, confidence.
decision-cases.jsonl: source of expected phrases (kept out of the answering agent's view).

This script only checks concept coverage, not whether the decision branch is correct.
Branch correctness still needs a human/LLM review.
"""
import argparse, json, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))

# Exact-phrase matching undercounts correct paraphrases. These are the only
# accepted equivalents; anything outside the list is treated as a miss.
SYNONYMS = {
    "O(M×N)": ["O(M×N)", "O(MN)", "笛卡尔积", "全量比较"],
    "哈希": ["哈希", "LSH", "局部敏感"],
    "符号": ["符号", "规则推理", "规则/路径", "规则、路径"],
    "免索引邻接": ["免索引邻接", "索引无关", "index-free"],
    "W3C": ["W3C"],
    "推理": ["推理", "OWL", "公理"],
    "多参与方": ["多参与方", "多方", "多机构", "多组织"],
    "Hit@n": ["Hit@n", "Hit@1", "Hit@3", "Hit@10", "Hits@"],
    "实体链接": ["实体链接", "entity linking"],
    "CSP": ["CSP", "SPWCF", "SPCSE"],
    "CLSP": ["CLSP"],
    "BetaE": ["BetaE"],
    "多实例": ["多实例", "bag", "multi-instance"],
    "增益": ["增益", "提升", "改进"],
    "模态消融": ["模态消融", "消融"],
    "覆盖率": ["覆盖率", "覆盖"],
    "一对多": ["一对多", "1-N", "1-to-N"],
    "KRL": ["KRL", "TransE", "TransR", "知识表示学习"],
    "降噪": ["降噪", "去噪"],
    "低频": ["低频", "长尾", "未登录"],
    "分块": ["分块", "blocking", "LSH"],
    "多跳": ["多跳", "2 跳", "2+ 跳", "2 跳以上", "两跳", "multi-hop"],
    "事件Schema": ["事件schema", "事件 schema", "event schema"],
    "维护": ["版本化", "日志", "退役", "更新"],
    "种子": ["seed", "伪种子", "人工标注"],
}


def hit(word, text):
    return any(x.lower() in text for x in SYNONYMS.get(word, [word]))


def load_cases(path=None):
    out = {}
    with open(path or os.path.join(BASE, "decision-cases.jsonl"), encoding="utf-8") as f:
        for line in f:
            if line.strip():
                x = json.loads(line)
                out[x["id"]] = x
    return out


def text_of(ans):
    parts = [str(ans.get("decision", ""))]
    parts += [str(x) for x in ans.get("actions", [])]
    parts.append(str(ans.get("evidence", "")))
    return " ".join(parts).lower()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("answers")
    ap.add_argument("--md", default="")
    ap.add_argument("--cases", default="")
    a = ap.parse_args()

    cases = load_cases(a.cases or None)
    answers = json.load(open(a.answers, encoding="utf-8"))
    rows = []
    for ans in answers:
        cid = ans.get("id")
        case = cases.get(cid)
        if not case:
            rows.append((cid, 0, len(case["expected"]) if case else 0, ["未知用例"], ""))
            continue
        text = text_of(ans)
        hits = [w for w in case["expected"] if hit(w, text)]
        missing = [w for w in case["expected"] if not hit(w, text)]
        rows.append((cid, len(hits), len(case["expected"]), missing, ans.get("decision", "")))

    lines = ["| ID | 命中 | 缺失 | 结论 |", "|---|---:|---|---|"]
    for cid, n, total, missing, decision in rows:
        miss = "、".join(missing) if missing else "—"
        lines.append(f"| {cid} | {n}/{total} | {miss} | {decision} |")
    report = "\n".join(lines)
    print(report)
    if a.md:
        with open(a.md, "w", encoding="utf-8") as f:
            f.write("# 盲测自动评分（仅概念覆盖）\n\n" + report + "\n")
    full = sum(1 for _, n, total, _, _ in rows if n == total)
    print(f"\nfully covered: {full}/{len(rows)}")


if __name__ == "__main__":
    main()
