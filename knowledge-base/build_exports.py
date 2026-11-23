# -*- coding: utf-8 -*-
"""Export the knowledge base to Obsidian notes, Anki CSV, and a local BM25 searcher."""
import csv, json, os, re, shutil
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
ROWS = json.load(open(os.path.join(BASE, "kg-knowledge-points.json"), encoding="utf-8"))
OBS = os.path.join(BASE, "obsidian")
ANKI = os.path.join(BASE, "anki")
SEARCH = os.path.join(BASE, "search")


def note_name(r):
    title = re.sub(r'[\\/:*?"<>|]', "－", r["title"]).strip().rstrip(".")
    title = title[:48]
    return f"{r['id']} {title}"


NAME = {r["id"]: note_name(r) for r in ROWS}
FIG_PATH = os.path.join(BASE, "figures", "figure-index.json")
FIGS = json.load(open(FIG_PATH, encoding="utf-8")) if os.path.exists(FIG_PATH) else []
EX_MAP = defaultdict(list)
for f in FIGS:
    parts = f["section"].split(".")
    EX_MAP[(f["book"], f["chapter"], ".".join(parts[:2]))].append(f)


def fmt_links(ids_text):
    ids = [x for x in ids_text.split("；") if x]
    if not ids:
        return "无"
    return "\n".join(f"- [[{NAME.get(i, i)}]]" for i in ids)


def write_note(r):
    tags = ["KG", f"书{r['book']}", f"第{r['chapter']}章", r["coverage"], r["type"], r["scope"]]
    lines = [
        "---",
        f'id: "{r["id"]}"',
        f'canonical_id: "{r["canonical_id"]}"',
        f'book: "{r["book"]}"',
        f"chapter: {r['chapter']}",
        f'section: "{r["section"]}"',
        f'type: "{r["type"]}"',
        f'coverage: "{r["coverage"]}"',
        f'scope: "{r["scope"]}"',
        f'page: "{r["page"]}"',
        f'skill_module: "{r["skill_module"]}"',
        "tags:",
    ] + [f"  - {t}" for t in tags] + [
        "---",
        "",
        f"# {r['title']}",
        "",
        f"> {r['id']} · 书{r['book']} 第{r['chapter']}章 {r['chapter_title']} · {r['section']} {r['section_title']}",
        "",
    ]
    if r["canonical_id"] != r["id"]:
        lines += [f"> 规范条目：[[{NAME.get(r['canonical_id'], r['canonical_id'])}]]", ""]
    ann = os.path.join(OBS, "30-批注", f"批注-{r['id']}.md")
    if os.path.exists(ann):
        lines += [f"> 批注：[[批注-{r['id']}]]", ""]
    ex = EX_MAP.get((r["book"], r["chapter"], r["section"]), [])[:6]
    if ex:
        labels = "、".join(f"{f['number']} {f['caption'][:18]}" for f in ex)
        lines += [f"> 本节图表：{labels}（[[40-图表索引]]）", ""]
    lines += [
        "## 定义",
        "",
        r["definition"],
        "",
        "## 关键要点",
        "",
    ]
    for k in [x for x in r["key_points"].split("；") if x]:
        lines.append(f"- {k}")
    if r["formula"]:
        lines += ["", "## 公式/示例", "", "```text", r["formula"], "```"]
    lines += [
        "",
        "## 前置知识",
        "",
        fmt_links(r["prerequisites"]),
        "",
        "## 关联知识",
        "",
        fmt_links(r["related"]),
        "",
        "## 来源",
        "",
        f"- PDF {r['page']}",
        f"- Skill 模块：{r['skill_module']}",
        "",
    ]
    path = os.path.join(OBS, "10-知识点", note_name(r) + ".md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


def build_obsidian():
    for sub in ["10-知识点", "00-索引", "00-索引/章节"]:
        os.makedirs(os.path.join(OBS, sub), exist_ok=True)
    for r in ROWS:
        write_note(r)

    by_chapter = defaultdict(list)
    for r in ROWS:
        by_chapter[(r["book"], r["chapter"], r["chapter_title"])].append(r)

    # chapter indexes
    chapter_links = {"A": [], "B": []}
    for (book, ch, ctitle), items in sorted(by_chapter.items()):
        secs = defaultdict(list)
        for r in items:
            secs[(r["section"], r["section_title"])].append(r)
        lines = [
            "---",
            f'book: "{book}"',
            f"chapter: {ch}",
            "---",
            "",
            f"# 书{book} 第{ch}章 {ctitle}",
            "",
            f"共 {len(items)} 个知识点。",
            "",
        ]
        for (sec, stitle), pts in sorted(secs.items()):
            lines += [f"## {sec} {stitle}", "", "| 知识点 | 类型 | 页码 |", "|---|---|---|"]
            for r in pts:
                lines.append(f"| [[{note_name(r)}]] | {r['type']} | {r['page']} |")
            lines.append("")
        cname = f"书{book} 第{ch:02d}章 {ctitle}"
        with open(os.path.join(OBS, "00-索引", "章节", cname + ".md"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        chapter_links[book].append((ch, ctitle, len(items), cname))

    for book, label in [("A", "书 A《知识图谱导论》"), ("B", "书 B《知识图谱与深度学习》")]:
        lines = [
            "---",
            f'book: "{book}"',
            "---",
            "",
            f"# {label} 索引",
            "",
            "| 章 | 标题 | 知识点数 |", "|---|---|---:|",
        ]
        for ch, ctitle, n, cname in chapter_links[book]:
            lines.append(f"| {ch} | [[{cname}]] | {n} |")
        lines += ["", f"返回 [[总索引]]", ""]
        with open(os.path.join(OBS, "00-索引", f"书{book}索引.md"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    scope_groups = defaultdict(list)
    for r in ROWS:
        scope_groups[r["scope"]].append(r)
    scope_links = []
    for scope, items in sorted(scope_groups.items(), key=lambda x: (-len(x[1]), x[0])):
        name = f"范围-{scope}"
        lines = [
            "---", "tags:", "  - KG", "  - 索引", "---", "",
            f"# 范围：{scope}",
            "",
            f"共 {len(items)} 个知识点。",
            "",
            "| ID | 知识点 | 书/章 | 类型 |", "|---|---|---|---|",
        ]
        for r in items:
            lines.append(f"| {r['id']} | [[{note_name(r)}]] | 书{r['book']} 第{r['chapter']}章 | {r['type']} |")
        lines += ["", "返回 [[总索引]]", ""]
        with open(os.path.join(OBS, "00-索引", name + ".md"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        scope_links.append((scope, len(items), name))

    total = [
        "---", "tags:", "  - KG", "  - 索引", "---", "",
        "# 知识图谱两书知识点库",
        "",
        f"- 知识点：**{len(ROWS)}**",
        f"- 书 A：{sum(1 for r in ROWS if r['book']=='A')}",
        f"- 书 B：{sum(1 for r in ROWS if r['book']=='B')}",
        f"- 章：{len({(r['book'], r['chapter']) for r in ROWS})}；节：{len({(r['book'], r['chapter'], r['section']) for r in ROWS})}",
        "",
        "## 入口",
        "",
        "- [[书A索引]]",
        "- [[书B索引]]",
        "",
        "## 按范围",
        "",
    ]
    for scope, n, name in scope_links:
        total.append(f"- [[{name}]]（{n}）")
    total += [
        "",
        "## 用法",
        "",
        "1. 在 Obsidian 中打开 `knowledge-base/obsidian` 作为 Vault。",
        "2. 从总索引进入章节，或直接搜索知识点标题/ID。",
        "3. 每个知识点有前置/关联双链，可沿链接复习。",
        "4. 标签：`#KG #书A #第5章 #核心 #模型 #KG核心`。",
        "5. 非规范条目会在正文顶部指向 `canonical_id`。",
        "",
    ]
    with open(os.path.join(OBS, "00-索引", "总索引.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(total))


def build_anki():
    os.makedirs(ANKI, exist_ok=True)
    path = os.path.join(ANKI, "kg-cards.csv")
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Front", "Back", "Tags"])
        for r in ROWS:
            front = f"请说明：{r['title']}（书{r['book']} · {r['chapter_title']} {r['section']}）"
            back = [r["definition"]]
            kp = [x for x in r["key_points"].split("；") if x]
            if kp:
                back.append("<br><br>" + "<br>".join(f"· {x}" for x in kp))
            if r["formula"]:
                back.append("<br><br><code>" + r["formula"].replace("<", "&lt;") + "</code>")
            back.append(f"<br><br><i>来源：PDF {r['page']} · {r['skill_module']}</i>")
            tags = f"KG 书{r['book']} 第{r['chapter']}章 {r['coverage']} {r['type']} {r['scope']}"
            w.writerow([front, "".join(back), tags])

    # 应用/判断卡：适合对比、案例，以及含适用/选择/风险/注意的条目
    keys = ("适用", "选择", "风险", "注意", "条件", "区别", "优缺点")
    app = [r for r in ROWS if r["type"] in ("对比", "案例") or any(k in r["definition"] for k in keys)]
    app = app[:120]
    path2 = os.path.join(ANKI, "kg-application-cards.csv")
    with open(path2, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Front", "Back", "Tags"])
        for r in app:
            front = f"应用判断：{r['title']} 的适用条件、风险或选择依据是什么？"
            back = [r["definition"]]
            kp = [x for x in r["key_points"].split("；") if x]
            if kp:
                back.append("<br><br>" + "<br>".join(f"· {x}" for x in kp))
            back.append(f"<br><br><i>来源：PDF {r['page']} · {r['skill_module']}</i>")
            tags = f"KG 应用卡 书{r['book']} 第{r['chapter']}章 {r['scope']}"
            w.writerow([front, "".join(back), tags])


def build_canvas():
    chapters = sorted({(r["book"], r["chapter"], r["chapter_title"]) for r in ROWS})
    nodes = [{
        "id": "root", "type": "file", "file": "00-索引/总索引.md",
        "x": -220, "y": -260, "width": 440, "height": 220,
    }]
    edges = []
    book_ids = {}
    for book, x in [("A", -620), ("B", 180)]:
        nid = f"book{book}"
        book_ids[book] = nid
        nodes.append({"id": nid, "type": "file", "file": f"00-索引/书{book}索引.md",
                      "x": x, "y": -20, "width": 420, "height": 180})
        edges.append({"id": f"e-root-{nid}", "fromNode": "root", "toNode": nid,
                      "fromSide": "bottom", "toSide": "top"})
    for book, ch, title in chapters:
        nid = f"ch{book}{ch:02d}"
        name = f"书{book} 第{ch:02d}章 {title}"
        idx = ch
        nodes.append({"id": nid, "type": "file", "file": f"00-索引/章节/{name}.md",
                      "x": -620 if book == "A" else 180,
                      "y": 220 + (idx - 1) * 150, "width": 420, "height": 120})
        edges.append({"id": f"e-{book_ids[book]}-{nid}", "fromNode": book_ids[book],
                      "toNode": nid, "fromSide": "bottom", "toSide": "top"})
    with open(os.path.join(OBS, "知识图谱总览.canvas"), "w", encoding="utf-8") as f:
        json.dump({"nodes": nodes, "edges": edges}, f, ensure_ascii=False, indent=2)


SEARCH_PY = r'''# -*- coding: utf-8 -*-
"""Local BM25 search over the knowledge base. No external dependencies."""
import argparse, json, math, os, re
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))
ROWS = json.load(open(os.path.join(BASE, "..", "kg-knowledge-points.json"), encoding="utf-8"))


def tokens(text):
    text = text.lower()
    out = re.findall(r"[a-z0-9]+", text)
    for run in re.findall(r"[一-鿿]+", text):
        out.extend(run)
        out.extend(run[i:i + 2] for i in range(len(run) - 1))
    return out


DOCS = []
for r in ROWS:
    text = " ".join([r["title"], r["definition"], r["key_points"], r["formula"],
                     r["chapter_title"], r["section_title"], r["type"]])
    title = " ".join([r["title"], r["chapter_title"], r["section_title"]])
    DOCS.append((r, Counter(tokens(text)), Counter(tokens(title))))

N = len(DOCS)
AVG = sum(sum(tf.values()) for _, tf, _ in DOCS) / max(N, 1)
DF = Counter()
for _, tf, _ in DOCS:
    for t in tf:
        DF[t] += 1


def bm25(query, limit=8, book=None, module=None, scope=None):
    q = tokens(query)
    q_lower = query.lower()
    latin_q = [t for t in q if re.fullmatch(r"[a-z0-9]+", t)]
    scored = []
    for r, tf, title_tf in DOCS:
        if book and r["book"] != book:
            continue
        if module and not r["skill_module"].startswith(module):
            continue
        if scope and r["scope"] != scope:
            continue
        dl = sum(tf.values())
        s = 0.0
        for t in q:
            idf = math.log(1 + (N - DF[t] + 0.5) / (DF[t] + 0.5))
            if t in tf:
                f = tf[t]
                s += idf * f * 2.5 / (f + 1.5 * (1 - 0.75 + 0.75 * dl / max(AVG, 1e-9)))
            if t in title_tf:
                s += idf * 2.0
        # Latin terms (model names) are high-signal: require/boost them.
        latin_hits = sum(1 for t in latin_q if t in tf or t in title_tf)
        if latin_q:
            if latin_hits == 0:
                s *= 0.25
            else:
                s += 20.0 * latin_hits
        hay = (r["title"] + " " + r["definition"]).lower()
        if q_lower and q_lower in hay:
            s += 8.0
        if s > 0:
            scored.append((s, r))
    scored.sort(key=lambda x: -x[0])
    return scored[:limit]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--limit", type=int, default=8)
    ap.add_argument("--book", choices=["A", "B"])
    ap.add_argument("--module", help="如 M5 或 M10")
    ap.add_argument("--scope", help="KG核心 / KG专项 / KG邻接 / 背景")
    a = ap.parse_args()
    for s, r in bm25(a.query, a.limit, a.book, a.module, a.scope):
        print(f"{s:6.2f}  {r['id']}  {r['title']}  [{r['page']}]")
        print(f"        {r['definition'][:120]}")
        print(f"        {r['skill_module']} · {r['scope']}")


if __name__ == "__main__":
    main()
'''


def build_search():
    os.makedirs(SEARCH, exist_ok=True)
    with open(os.path.join(SEARCH, "kg_search.py"), "w", encoding="utf-8") as f:
        f.write(SEARCH_PY)


def main():
    build_obsidian()
    build_canvas()
    build_anki()
    build_search()
    print(f"notes {len(ROWS)}; obsidian {os.path.join(OBS, '10-知识点')}; "
          f"anki {os.path.join(ANKI, 'kg-cards.csv')}; canvas 知识图谱总览.canvas")


if __name__ == "__main__":
    main()
