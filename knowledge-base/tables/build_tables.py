# -*- coding: utf-8 -*-
"""Validate curated table data and render Markdown/CSV.

Inputs:
  tables/table-data.json
  figures/figure-index.json
  ../extracted/book-*.md
Outputs:
  tables/tables.md
  tables/table-index.csv
  tables/table-validation.md
"""
import csv, json, os, re, sys

BASE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.dirname(BASE)
ROOT = os.path.dirname(KB)
SRC = {
    "A": os.path.join(ROOT, "extracted", "book-a-知识图谱导论.md"),
    "B": os.path.join(ROOT, "extracted", "book-b-知识图谱与深度学习.md"),
}
DATA = json.load(open(os.path.join(BASE, "table-data.json"), encoding="utf-8"))["tables"]
FIGS = {f["id"]: f for f in json.load(open(os.path.join(KB, "figures", "figure-index.json"),
                                           encoding="utf-8"))}
REVIEW_PATH = os.path.join(BASE, "source-review.json")
REVIEW = json.load(open(REVIEW_PATH, encoding="utf-8")) if os.path.exists(REVIEW_PATH) else {}


def load_pages(book):
    pages, cur, buf = {}, 0, []
    for line in open(SRC[book], encoding="utf-8"):
        m = re.match(r"<!--\s*p\.(\d+)\s*-->", line.strip())
        if m:
            if cur:
                pages[cur] = "\n".join(buf)
            cur, buf = int(m.group(1)), []
        else:
            buf.append(line)
    if cur:
        pages[cur] = "\n".join(buf)
    return pages


def compact(s):
    return re.sub(r"[\s,，]", "", s)


def main():
    if not all(os.path.exists(p) for p in SRC.values()):
        print("skip: source text not available; keep existing table validation")
        return
    pages = {b: load_pages(b) for b in ("A", "B")}
    errors, source_misses = [], []
    for t in DATA:
        tid = t["id"]
        if tid not in FIGS:
            errors.append(f"{tid}: 不在 figure-index")
            continue
        f = FIGS[tid]
        if f["kind"] != "表":
            errors.append(f"{tid}: 不是表")
        if t["page"] != f["page"]:
            errors.append(f"{tid}: 页码 {t['page']} != 图表索引 {f['page']}")
        if len(set(t["columns"])) != len(t["columns"]):
            errors.append(f"{tid}: 列名重复")
        for r in t["rows"]:
            if len(r) != len(t["columns"]):
                errors.append(f"{tid}: 行列数不一致 {len(r)} != {len(t['columns'])}")
                continue
            for i in t["numeric_columns"]:
                try:
                    float(r[i])
                except (TypeError, ValueError):
                    errors.append(f"{tid}: 非数值单元格 {r[i]!r}")
        src = compact("".join(pages[t["book"]].get(p, "") for p in range(t["page"], t["page"] + 2)))
        for r in t["rows"]:
            for i in t["numeric_columns"]:
                tok = str(r[i]).replace(",", "")
                if tok not in src and f"{tid}:{tok}" not in REVIEW:
                    source_misses.append((tid, tok, r[0]))

    status_ok = not errors and not source_misses
    # markdown
    lines = ["# 结构化表格\n",
             f"- 已结构化：{len(DATA)} 张核心实验表",
             f"- 校验错误：{len(errors)}；源码数字未匹配：{len(source_misses)}",
             "\n口径：数值来自原书表格；B 为 OCR，已用去空格/去逗号匹配回源页。\n"]
    for t in DATA:
        lines += [f"## {t['id']} {t['caption']}\n", f"页码：p.{t['page']}；{t.get('note','')}\n"]
        lines.append("| " + " | ".join(t["columns"]) + " |")
        lines.append("|" + "|".join(["---"] * len(t["columns"])) + "|")
        for r in t["rows"]:
            lines.append("| " + " | ".join(str(x) for x in r) + " |")
        lines.append("")
    open(os.path.join(BASE, "tables.md"), "w", encoding="utf-8").write("\n".join(lines))

    with open(os.path.join(BASE, "table-index.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "caption", "page", "rows", "columns", "status"])
        for t in DATA:
            w.writerow([t["id"], t["caption"], t["page"], len(t["rows"]),
                        len(t["columns"]), "ok" if not errors and not source_misses else "check"])

    v = ["# 表格数据校验\n", f"- 表格：{len(DATA)}", f"- 结构错误：{len(errors)}",
         f"- 源码数字未匹配：{len(source_misses)}", f"- 结论：{'PASS' if status_ok else 'CHECK'}", "\n## 结构错误\n"]
    v += [f"- {e}" for e in errors] or ["- 无"]
    v += ["\n## 源码未匹配（OCR 可能造成假阴性）\n"]
    v += [f"- {tid} {model}: {tok}" for tid, tok, model in source_misses] or ["- 无"]
    open(os.path.join(BASE, "table-validation.md"), "w", encoding="utf-8").write("\n".join(v))

    print(f"tables {len(DATA)} errors {len(errors)} source_misses {len(source_misses)}")
    for e in errors[:10]:
        print("ERR", e)
    for x in source_misses[:10]:
        print("MISS", x)
    sys.exit(0 if status_ok else 1)


if __name__ == "__main__":
    main()
