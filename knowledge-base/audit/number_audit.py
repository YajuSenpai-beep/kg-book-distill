# -*- coding: utf-8 -*-
"""Cross-check numeric claims in experiment points against the cited source pages.

Inputs:
  data/*-exp*.json          experiment/detail points
  extracted/book-*.md       page-marked source text
Outputs:
  audit/number-audit.csv
  audit/number-audit.md
"""
import csv, glob, json, os, re

BASE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.dirname(BASE)
ROOT = os.path.dirname(KB)
SRC = {
    "A": os.path.join(ROOT, "extracted", "book-a-知识图谱导论.md"),
    "B": os.path.join(ROOT, "extracted", "book-b-知识图谱与深度学习.md"),
}


def load_pages(book):
    pages = {}
    cur = 0
    buf = []
    for line in open(SRC[book], encoding="utf-8"):
        m = re.match(r"<!--\s*p\.(\d+)\s*-->", line.strip())
        if m:
            if cur:
                pages[cur] = "\n".join(buf)
            cur = int(m.group(1))
            buf = []
        else:
            buf.append(line)
    if cur:
        pages[cur] = "\n".join(buf)
    return pages


def page_range(text):
    m = re.search(r"p\.\s*(\d+)(?:\s*[-–—]\s*(\d+))?", text or "")
    if not m:
        return None, None
    return int(m.group(1)), int(m.group(2) or m.group(1))


def compact(s):
    return re.sub(r"[\s,，]", "", s)


def numbers(s):
    out = []
    for m in re.findall(r"\d+(?:[.,]\d+)*%?", s):
        out.append(m)
    return out


def main():
    if not all(os.path.exists(p) for p in SRC.values()):
        print("skip: source text not available; keep existing number audit")
        return
    exp_ids = set()
    for path in glob.glob(os.path.join(KB, "data", "*-exp*.json")):
        d = json.load(open(path, encoding="utf-8"))
        for sec in d["sections"]:
            for p in sec["points"]:
                exp_ids.add(p["id"])
    rows = json.load(open(os.path.join(KB, "kg-knowledge-points.json"), encoding="utf-8"))
    pages = {b: load_pages(b) for b in ("A", "B")}
    review_path = os.path.join(BASE, "number-review.json")
    review = json.load(open(review_path, encoding="utf-8")) if os.path.exists(review_path) else {}

    out = []
    for r in rows:
        if r["id"] not in exp_ids:
            continue
        a, b = page_range(r["page"])
        if a is None:
            out.append({"id": r["id"], "title": r["title"], "page": r["page"],
                        "token": "", "status": "无页码", "note": ""})
            continue
        src = compact("".join(pages[r["book"]].get(p, "") for p in range(a, b + 1)))
        toks = numbers(r["definition"] + " " + r["key_points"])
        missing = []
        for t in toks:
            # ignore small integers that occur everywhere; keep decimals/percent/thousands
            core = t.rstrip("%").replace(",", "")
            if len(core) <= 2 and "." not in core:
                continue
            if core not in src:
                missing.append(t)
        if missing and r["id"] in review:
            status = "人工确认"
            note = review[r["id"]]
        elif missing:
            status = "需复核"
            note = "数字未在引用页找到"
        else:
            status = "通过"
            note = "引用页可检索到全部关键数字"
        out.append({"id": r["id"], "title": r["title"], "page": r["page"],
                    "token": "；".join(missing), "status": status, "note": note})

    csv_path = os.path.join(BASE, "number-audit.csv")
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "title", "page", "token", "status", "note"])
        w.writeheader()
        w.writerows(out)

    ok = sum(1 for x in out if x["status"] == "通过")
    confirmed = sum(1 for x in out if x["status"] == "人工确认")
    bad = [x for x in out if x["status"] == "需复核"]
    lines = ["# 实验数值回溯核对\n",
             f"- 实验/评估点：{len(out)}",
             f"- 引用页可检索到关键数字：{ok}",
             f"- 人工确认（派生/指标名/取整）：{confirmed}",
             f"- 仍需复核：{len(bad)}",
             "\n口径：抽取定义/要点中的数字 token（忽略 1–2 位整数），在引用页 OCR 文本中做去空格/去逗号匹配。OCR 错字会造成假阴性，需人工判断。\n",
             "## 需复核\n"]
    for x in bad:
        lines.append(f"- `{x['id']}` {x['title']}（{x['page']}）：未匹配 {x['token']}")
    open(os.path.join(BASE, "number-audit.md"), "w", encoding="utf-8").write("\n".join(lines))
    print("points", len(out), "ok", ok, "review", len(bad))


if __name__ == "__main__":
    main()
