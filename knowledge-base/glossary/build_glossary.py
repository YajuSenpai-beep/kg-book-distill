# -*- coding: utf-8 -*-
"""Build a bilingual glossary and resolve each term to a knowledge point."""
import csv, json, os, re

BASE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.dirname(BASE)
TERMS = json.load(open(os.path.join(BASE, "terms.json"), encoding="utf-8"))["terms"]
ROWS = json.load(open(os.path.join(KB, "kg-knowledge-points.json"), encoding="utf-8"))


def norm(s):
    return re.sub(r"[\s_\-/]", "", s.lower())


def resolve(t):
    names = [t["term"], t["en"]] + t.get("aliases", [])
    normed = [norm(x) for x in names]
    exact, starts, contains = [], [], []
    for r in ROWS:
        nt = norm(r["title"])
        if nt in normed:
            exact.append(r)
        elif any(nt.startswith(x) for x in normed):
            starts.append(r)
        elif any(x in nt for x in normed) and len(r["title"]) <= 40:
            contains.append(r)
    pool = exact or starts or contains
    return pool[0] if pool else None


def main():
    rows = []
    for t in TERMS:
        r = resolve(t)
        rows.append({**t, "point_id": r["id"] if r else "",
                     "page": r["page"] if r else "",
                     "definition": r["definition"] if r else ""})
    with open(os.path.join(BASE, "glossary.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["term", "en", "aliases", "category", "point_id",
                                          "page", "definition"])
        w.writeheader()
        for r in rows:
            x = dict(r)
            x["aliases"] = "；".join(r.get("aliases", []))
            w.writerow(x)
    lines = ["# 术语表\n", f"- 术语：{len(rows)}；已解析到知识点：{sum(1 for r in rows if r['point_id'])}", "",
             "| 中文 | English | 别名 | 类别 | 知识点 | 页 |", "|---|---|---|---|---|---:|"]
    for r in rows:
        lines.append(f"| {r['term']} | {r['en']} | {'、'.join(r.get('aliases', [])) or '—'} | "
                     f"{r['category']} | {r['point_id'] or '—'} | {r['page'] or '—'} |")
    lines += ["\n## 定义\n"]
    for r in rows:
        if r["definition"]:
            lines.append(f"- **{r['term']}**（{r['en']}）：{r['definition']}")
    open(os.path.join(BASE, "glossary.md"), "w", encoding="utf-8").write("\n".join(lines))
    print("terms", len(rows), "resolved", sum(1 for r in rows if r["point_id"]))


if __name__ == "__main__":
    main()
