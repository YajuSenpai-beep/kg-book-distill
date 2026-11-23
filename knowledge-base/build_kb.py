# -*- coding: utf-8 -*-
"""Build the knowledge-point base from per-chapter JSON files.

Input:  data/*.json  (one chapter per file)
Output: kg-knowledge-points.csv / .json / knowledge-map.md /
        coverage-matrix.md / validation-report.md
"""
import csv, glob, json, os, re, sys
from collections import Counter, defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
TYPES = {"概念", "方法", "模型", "算法", "系统", "公式", "案例", "对比", "原则"}
COVERS = {"核心", "专项", "背景"}


def load_canonical():
    path = os.path.join(DATA, "canonical-map.json")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def scope_of(book, chapter, section):
    if book == "A":
        if chapter == 1:
            return "KG核心" if section in ("1.4", "1.5") else "背景"
        if 2 <= chapter <= 7:
            return "KG核心"
        if chapter == 8:
            return "KG邻接"
        return "KG专项"
    if chapter == 1:
        return "背景"
    if chapter in (2, 3, 4):
        return "KG核心"
    if chapter in (5, 6, 7):
        return "KG专项"
    return "背景"


def load_chapters():
    chapters = []
    for path in sorted(glob.glob(os.path.join(DATA, "*.json"))):
        if os.path.basename(path) == "canonical-map.json":
            continue
        with open(path, encoding="utf-8") as f:
            try:
                obj = json.load(f)
            except Exception as e:
                sys.exit(f"JSON 解析失败: {path}: {e}")
        chapters.append((path, obj))
    chapters.sort(key=lambda x: (x[1]["book"], int(x[1]["chapter"])))
    return chapters


def flatten(chapters):
    rows = []
    seen = set()
    errors, warnings = [], []
    canon = load_canonical()
    for path, ch in chapters:
        book = ch["book"]
        cno = int(ch["chapter"])
        ctitle = ch["chapter_title"]
        for sec in ch["sections"]:
            secno = sec["sec"]
            stitle = sec["title"]
            for p in sec["points"]:
                pid = p.get("id", "")
                if not re.fullmatch(r"[AB]-\d{2}-\d{2}-\d{2}", pid):
                    errors.append(f"{path}: 非法 ID {pid!r}")
                if pid in seen:
                    errors.append(f"重复 ID: {pid}")
                seen.add(pid)
                for key in ("t", "ty", "d", "k", "p", "m", "c"):
                    if key not in p:
                        errors.append(f"{pid}: 缺少字段 {key}")
                if p.get("ty") not in TYPES:
                    errors.append(f"{pid}: 未知类型 {p.get('ty')!r}")
                if p.get("c") not in COVERS:
                    errors.append(f"{pid}: 未知覆盖层级 {p.get('c')!r}")
                if not re.match(r"^M(?:[0-9]|1[01])(?:\s|/|$)", p.get("m", "")):
                    errors.append(f"{pid}: Skill 模块必须以 M0–M11 开头，当前 {p.get('m')!r}")
                if not isinstance(p.get("k"), list):
                    errors.append(f"{pid}: k 必须是数组")
                row = {
                    "id": pid,
                    "canonical_id": canon.get(pid, pid),
                    "book": book,
                    "chapter": cno,
                    "chapter_title": ctitle,
                    "section": secno,
                    "section_title": stitle,
                    "title": p.get("t", ""),
                    "type": p.get("ty", ""),
                    "definition": p.get("d", ""),
                    "key_points": "；".join(p.get("k", [])),
                    "formula": p.get("f", ""),
                    "prerequisites": "；".join(p.get("pre", [])),
                    "related": "；".join(p.get("rel", [])),
                    "page": p.get("p", ""),
                    "skill_module": p.get("m", ""),
                    "coverage": p.get("c", ""),
                    "scope": scope_of(book, cno, secno),
                }
                rows.append(row)
    # reference integrity (warn only, cross-book refs may be intentional)
    ids = {r["id"] for r in rows}
    byid = {r["id"]: r for r in rows}
    for r in rows:
        for ref in [x for x in r["prerequisites"].split("；") if x] + [x for x in r["related"].split("；") if x]:
            if ref not in ids:
                warnings.append(f"{r['id']}: 引用了不存在的知识点 {ref}")
        cid = r["canonical_id"]
        if cid not in ids:
            errors.append(f"{r['id']}: canonical_id 不存在 {cid}")
        elif cid != r["id"] and byid[cid]["canonical_id"] != cid:
            errors.append(f"{r['id']}: canonical_id 指向了非规范条目 {cid}")
    return rows, errors, warnings


def write_csv(rows):
    path = os.path.join(BASE, "kg-knowledge-points.csv")
    headers = [
        ("id", "知识点ID"), ("canonical_id", "规范ID"), ("book", "书"), ("chapter", "章"),
        ("chapter_title", "章标题"), ("section", "节"), ("section_title", "节标题"),
        ("title", "知识点"), ("type", "类型"), ("definition", "定义"),
        ("key_points", "关键要点"), ("formula", "公式/示例"),
        ("prerequisites", "前置知识"), ("related", "关联知识"), ("page", "来源页"),
        ("skill_module", "Skill模块"), ("coverage", "覆盖层级"), ("scope", "范围"),
    ]
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow([h for _, h in headers])
        for r in rows:
            w.writerow([r[k] for k, _ in headers])
    return path


def write_json(rows):
    path = os.path.join(BASE, "kg-knowledge-points.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)
    return path


def md_escape(s):
    return str(s).replace("|", "\\|").replace("\n", " ")


def write_map(rows):
    path = os.path.join(BASE, "knowledge-map.md")
    grouped = defaultdict(list)
    for r in rows:
        grouped[(r["book"], r["chapter"], r["chapter_title"], r["section"], r["section_title"])].append(r)
    lines = [
        "# 知识图谱两书知识点地图\n",
        f"> 共 {len(rows)} 个知识点；按“书→章→节→知识点”组织。"
        "定义与要点为转述，来源页指 PDF 页码。\n",
    ]
    for (book, cno, ctitle, secno, stitle), items in sorted(grouped.items()):
        lines.append(f"\n## {'书 A' if book == 'A' else '书 B'} 第 {cno} 章 {ctitle} / {secno} {stitle}\n")
        lines.append("| ID | 知识点 | 类型 | 范围 | 定义 | 关键要点 | 来源 | Skill |")
        lines.append("|---|---|---|---|---|---|---|---|")
        for r in items:
            lines.append(
                f"| {r['id']} | {md_escape(r['title'])} | {r['type']} | {r['scope']} | {md_escape(r['definition'])} | "
                f"{md_escape(r['key_points'])} | {r['page']} | {md_escape(r['skill_module'])} |"
            )
        lines.append("")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


def write_coverage(rows):
    path = os.path.join(BASE, "coverage-matrix.md")
    by_module = defaultdict(list)
    for r in rows:
        by_module[r["skill_module"]].append(r)
    lines = ["# 知识点 → Skill 模块覆盖矩阵\n", f"> 共 {len(rows)} 个知识点。\n", "## 模块统计\n",
             "| Skill 模块 | 知识点数 |", "|---|---:|"]
    for m, items in sorted(by_module.items(), key=lambda x: (-len(x[1]), x[0])):
        lines.append(f"| {m} | {len(items)} |")
    lines.append("\n## 覆盖层级统计\n")
    lines.append("| 覆盖层级 | 数量 | 占比 |")
    lines.append("|---|---:|---:|")
    for c in ["核心", "专项", "背景"]:
        n = sum(1 for r in rows if r["coverage"] == c)
        lines.append(f"| {c} | {n} | {n / len(rows):.1%} |")
    lines.append("\n## 范围统计\n")
    lines.append("| 范围 | 数量 | 占比 |")
    lines.append("|---|---:|---:|")
    scopes = Counter(r["scope"] for r in rows)
    for s, n in scopes.most_common():
        lines.append(f"| {s} | {n} | {n / len(rows):.1%} |")
    lines.append("\n## 按模块列出知识点\n")
    for m, items in sorted(by_module.items()):
        lines.append(f"\n### {m}（{len(items)}）\n")
        for r in items:
            lines.append(f"- `{r['id']}` {r['title']}（{r['page']}）")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


def write_report(rows, errors, warnings):
    path = os.path.join(BASE, "validation-report.md")
    type_counts = Counter(r["type"] for r in rows)
    book_counts = Counter(r["book"] for r in rows)
    lines = [
        "# 知识库校验报告\n",
        "## 总量\n",
        f"- 知识点总数：**{len(rows)}**",
        f"- 书 A：{book_counts.get('A', 0)}；书 B：{book_counts.get('B', 0)}",
        f"- 章数：{len({(r['book'], r['chapter']) for r in rows})}；节数：{len({(r['book'], r['chapter'], r['section']) for r in rows})}",
        f"- 严重错误：{len(errors)}；引用警告：{len(warnings)}",
        "\n## 类型分布\n",
        "| 类型 | 数量 |", "|---|---:|",
    ]
    for t, n in type_counts.most_common():
        lines.append(f"| {t} | {n} |")
    lines.append("\n## 覆盖层级\n")
    for c in ["核心", "专项", "背景"]:
        n = sum(1 for r in rows if r["coverage"] == c)
        lines.append(f"- {c}：{n}（{n / len(rows):.1%}）")
    lines.append("\n## 范围\n")
    scopes = Counter(r["scope"] for r in rows)
    for s, n in scopes.most_common():
        lines.append(f"- {s}：{n}（{n / len(rows):.1%}）")
    lines.append(f"\n## 规范条目\n")
    lines.append(f"- 非规范条目（指向 canonical_id）：{sum(1 for r in rows if r['canonical_id'] != r['id'])}")
    lines.append("\n## 错误\n")
    lines.extend([f"- {e}" for e in errors] or ["- 无"])
    lines.append("\n## 引用警告\n")
    lines.extend([f"- {w}" for w in warnings] or ["- 无"])
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return path


def main():
    chapters = load_chapters()
    if not chapters:
        sys.exit("data/ 下没有 JSON 文件")
    rows, errors, warnings = flatten(chapters)
    rows.sort(key=lambda r: (
        r["book"], r["chapter"],
        tuple(int(x) for x in r["section"].split(".")),
        r["id"],
    ))
    if errors:
        print("\n".join(errors), file=sys.stderr)
        sys.exit(f"发现 {len(errors)} 个严重错误，未生成产物")
    write_csv(rows)
    write_json(rows)
    write_map(rows)
    write_coverage(rows)
    write_report(rows, errors, warnings)
    print(f"知识点 {len(rows)}；书 A {sum(1 for r in rows if r['book']=='A')}；"
          f"书 B {sum(1 for r in rows if r['book']=='B')}；警告 {len(warnings)}")


if __name__ == "__main__":
    main()
