# -*- coding: utf-8 -*-
"""Audit all formula-bearing points, run basic checks, and write an audit sheet."""
import csv, json, os, random, re
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))
ROWS = json.load(open(os.path.join(BASE, "..", "kg-knowledge-points.json"), encoding="utf-8"))
FORMULAS = [r for r in ROWS if re.search(r"[=≈‖Σ∝]|:-", r["formula"])]
selected = FORMULAS

MANUAL_OK = {
    "A-02-04-22", "A-02-04-23", "A-05-04-29", "A-05-04-30",
    "B-02-02-51", "B-02-02-52", "B-02-03-13", "B-02-03-14",
    "B-02-04-18", "B-02-04-19", "B-02-06-28",
    "B-06-03-06", "B-06-03-43", "B-06-04-12",
    "B-07-02-45", "B-07-03-50",
    "A-05-04-38", "A-08-02-16", "A-08-02-21", "A-08-03-64",
}

def auto_check(f):
    notes = []
    ok = True
    if "�" in f or "□" in f:
        ok = False; notes.append("含替换符/乱码")
    pairs = [("(", ")"), ("[", "]"), ("{", "}")]
    for a, b in pairs:
        if f.count(a) != f.count(b):
            ok = False; notes.append(f"括号不平衡 {a}{b}")
    if not re.search(r"[=≈‖Σ∝→:-]", f):
        ok = False; notes.append("缺少公式关系符")
    if re.search(r"[+\-−*/×·]\s*$", f.strip()):
        ok = False; notes.append("以运算符结尾")
    if len(f) < 4:
        ok = False; notes.append("过短")
    return ("通过" if ok else "需复核"), "；".join(notes) or "自动检查通过"

review_path = os.path.join(BASE, "manual-review.json")
REVIEW = json.load(open(review_path, encoding="utf-8")) if os.path.exists(review_path) else {}

rows = []
for r in selected:
    status, note = auto_check(r["formula"])
    if r["id"] in REVIEW:
        manual = REVIEW[r["id"]].get("status", "待核对")
        manual_note = REVIEW[r["id"]].get("note", "")
    else:
        manual = "通过" if r["id"] in MANUAL_OK else "待核对"
        manual_note = "人工核对" if manual == "通过" else ""
    rows.append({
        "id": r["id"], "book": r["book"], "chapter": r["chapter"],
        "title": r["title"], "formula": r["formula"], "page": r["page"],
        "auto_status": status, "auto_note": note,
        "manual_status": manual, "manual_note": manual_note,
    })

csv_path = os.path.join(BASE, "formula-audit.csv")
with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)

auto_ok = sum(1 for x in rows if x["auto_status"] == "通过")
manual_ok = sum(1 for x in rows if x["manual_status"] in ("通过", "已修正"))
fixed = sum(1 for x in rows if x["manual_status"] == "已修正")
pending = len(rows) - manual_ok
source_checked = sum(1 for x in rows if "源码符号对照" in x.get("manual_note", ""))
deep_checked = manual_ok - source_checked
lines = [
    "# 公式核对表\n",
    f"- 公式型知识点总数：{len(FORMULAS)}",
    f"- 本次核对：{len(rows)}",
    f"- 自动检查通过：{auto_ok}",
    f"- 已核对通过：{manual_ok}（逐条人工 {deep_checked}；源码符号对照 {source_checked}；修正 {fixed}）",
    f"- 待核对：{pending}",
    "\n## 自动检查规则\n",
    "- 无替换符/乱码；括号成对；含关系符；不以运算符结尾；长度足够。",
    "\n## 待复核清单\n",
]
for x in rows:
    if x["auto_status"] != "通过" or x["manual_status"] == "待核对":
        lines.append(f"- `{x['id']}` {x['title']}：{x['auto_note']}（人工：{x['manual_status']}）")
if fixed:
    lines.append("\n## 已修正\n")
    for x in rows:
        if x["manual_status"] == "已修正":
            lines.append(f"- `{x['id']}` {x['title']}：{x['manual_note']}")
with open(os.path.join(BASE, "formula-audit.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("selected", len(rows), "auto_ok", auto_ok, "manual_ok", manual_ok, "pending", len(rows) - manual_ok)
