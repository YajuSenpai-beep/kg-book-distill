# -*- coding: utf-8 -*-
"""Four-level coverage audit: chapter -> section -> subsection -> figures/tables/formulas.

Inputs:
  ../extracted/book-a-知识图谱导论.md
  ../extracted/book-b-知识图谱与深度学习.md
  kg-knowledge-points.json

Outputs:
  audit/coverage-audit.md
  audit/coverage-gaps.csv
"""
import csv, json, os, re, sys
from collections import Counter, defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.dirname(BASE)
ROOT = os.path.dirname(KB)
SRC = {
    "A": os.path.join(ROOT, "extracted", "book-a-知识图谱导论.md"),
    "B": os.path.join(ROOT, "extracted", "book-b-知识图谱与深度学习.md"),
}

NUM_RE = re.compile(r"^([1-9])\.(\d{1,2})(?:\.(\d{1,2}))?$")
CJK_RE = re.compile(r"[一-鿿]{2,}")
CAP_RE = re.compile(r"^(图|表)\s*([0-9]+)\s*[-–—.]\s*([0-9]+)\s*(.*)$")
FORMULA_RE = re.compile(r"^\(?\s*(\d+)\.(\d+)\s*\)?$")


def parse_page(text):
    m = re.search(r"p\.\s*(\d+)(?:\s*[-–—]\s*(\d+))?", text or "")
    if not m:
        return None, None
    a = int(m.group(1))
    b = int(m.group(2)) if m.group(2) else a
    return a, b


def parse_source(book):
    """Return headings [{num,title,page,level}], captions, formula candidates."""
    headings, caps, formulas = [], [], []
    page = 0
    lines = open(SRC[book], encoding="utf-8").read().splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        m = re.match(r"<!--\s*p\.(\d+)\s*-->", line)
        if m:
            page = int(m.group(1))
            i += 1
            continue
        # formula candidates (heuristic): short lines with math operators
        if (len(line) < 120 and ("=" in line or "∑" in line or "∥" in line or "√" in line)
                and not line.startswith(("图", "表"))):
            formulas.append((page, line))
        # captions (filter prose lines that merely start with 图/表 X-Y)
        cm = CAP_RE.match(line)
        if cm:
            title = cm.group(4).strip()
            bad = ("所示", "中", "给出", "展示", "可以", "为", "是", "和", "与", "及", "的")
            if title and len(title) <= 60 and not title.startswith(bad):
                caps.append({"kind": cm.group(1), "num": f"{cm.group(1)}{cm.group(2)}-{cm.group(3)}",
                             "title": title, "page": page})
        # headings
        hm = re.match(r"^(#{2,5})\s*(\d+(?:\.\d+){1,2})\s*(.*)$", line)
        if hm:
            num, title = hm.group(2), hm.group(3).strip()
            # A headings may include trailing page numbers
            title = re.sub(r"\s+\d+\s*$", "", title).strip()
            if NUM_RE.match(num):
                headings.append({"num": num, "title": title, "page": page,
                                 "level": num.count(".") + 1})
            i += 1
            continue
        if book == "B" and page >= 14:
            # OCR: number+title may share a line, or number alone with title next line
            sm = re.match(r"^(\d+(?:\.\d+){1,2})\s+(\S.*)$", line)
            if sm and NUM_RE.match(sm.group(1)):
                num, title = sm.group(1), sm.group(2).strip()
                ch = int(num.split(".")[0])
                maxsec = {1: 5, 2: 9, 3: 8, 4: 5, 5: 5, 6: 6, 7: 4, 8: 3}.get(ch, 0)
                sec = int(num.split(".")[1])
                bad = ("从这", "如表", "图", "表", "其中", "我们", "可以", "由此", "因此", "所示")
                if (ch <= 8 and 1 <= sec <= maxsec and not re.match(r"^\d+\.0\d", num)
                        and CJK_RE.search(title) and len(title) <= 40
                        and not title.startswith(bad)):
                    headings.append({"num": num, "title": title, "page": page,
                                     "level": num.count(".") + 1})
                    i += 1
                    continue
            bm = re.match(r"^(\d+(?:\.\d+){1,2})$", line)
            if bm and NUM_RE.match(bm.group(1)):
                num = bm.group(1)
                ch = int(num.split(".")[0])
                maxsec = {1: 5, 2: 9, 3: 8, 4: 5, 5: 5, 6: 6, 7: 4, 8: 3}.get(ch, 0)
                sec = int(num.split(".")[1])
                title = ""
                for j in range(i + 1, min(i + 4, len(lines))):
                    nxt = lines[j].strip()
                    if nxt and not re.match(r"^\d+(?:\.\d+)*$", nxt):
                        title = nxt
                        break
                # OCR noise control: chapter/section ranges, no leading-zero cells
                bad = ("从这", "如表", "图", "表", "其中", "我们", "可以", "由此", "因此", "所示")
                if (ch <= 8 and 1 <= sec <= maxsec and not re.match(r"^\d+\.0\d", num)
                        and CJK_RE.search(title) and len(title) <= 40
                        and not title.startswith(bad)):
                    headings.append({"num": num, "title": title, "page": page,
                                     "level": num.count(".") + 1})
        i += 1
    # dedupe by num, keep first body occurrence
    seen, out = set(), []
    for h in headings:
        if h["num"] in seen:
            continue
        seen.add(h["num"])
        out.append(h)
    # dedupe captions by number
    seen_c, caps_out = set(), []
    for c in caps:
        if c["num"] in seen_c:
            continue
        seen_c.add(c["num"])
        caps_out.append(c)
    return out, caps_out, formulas


def chapters_of(headings):
    by_ch = defaultdict(list)
    for h in headings:
        ch = int(h["num"].split(".")[0])
        by_ch[ch].append(h)
    return by_ch


def caption_mentioned(points, cap):
    """Strong coverage: a point explicitly cites the figure/table number."""
    digits = re.findall(r"\d+", cap["num"])
    if len(digits) < 2:
        return []
    kind, a, b = cap["num"][0], digits[0], digits[1]
    pat = re.compile(rf"{kind}\s*{a}\s*[.\-–—]\s*{b}")
    out = []
    for p in points:
        text = " ".join([p["title"], p["definition"], p.get("key_points", ""),
                         p.get("formula", "")])
        if pat.search(text):
            out.append(p["id"])
    return out


def covering_points(points, ch, start, end):
    out = []
    for p in points:
        if p["chapter"] != ch:
            continue
        a, b = parse_page(p["page"])
        if a is None:
            continue
        if a <= end and b >= start:
            out.append(p["id"])
    return out


def main():
    if not all(os.path.exists(p) for p in SRC.values()):
        print("skip: source text not available; keep existing coverage audit")
        return
    rows = json.load(open(os.path.join(KB, "kg-knowledge-points.json"), encoding="utf-8"))
    by_book = defaultdict(list)
    for r in rows:
        by_book[r["book"]].append(r)

    summary = {}
    gaps = []
    sec_rows = []
    for book in ("A", "B"):
        heads, caps, formulas = parse_source(book)
        # prefer the richer figure/table index when available
        fig_path = os.path.join(KB, "figures", "figure-index.json")
        if os.path.exists(fig_path):
            all_figs = json.load(open(fig_path, encoding="utf-8"))
            caps = [{"kind": f["kind"], "num": f["number"], "title": f["caption"],
                     "page": f["page"]} for f in all_figs if f["book"] == book]
        by_ch = chapters_of(heads)
        l2 = [h for h in heads if h["level"] == 2]
        l3 = [h for h in heads if h["level"] == 3]
        l2_cov = l3_cov = 0
        for h in heads:
            ch = int(h["num"].split(".")[0])
            siblings = sorted(by_ch[ch], key=lambda x: (x["page"], x["num"]))
            idx = siblings.index(h)
            # a section extends to the next heading at the same or higher level
            # (global, so the last section of a chapter stops at the next chapter)
            later = [x["page"] for x in heads
                     if x["page"] > h["page"] and x["level"] <= h["level"]]
            nxt = min(later) if later else h["page"] + 10
            end = max(nxt + 1, h["page"] + 1)  # inclusive, tolerate same-page headings
            ids = covering_points(by_book[book], ch, h["page"], end)
            # union of point page intervals clipped to this section
            intervals = []
            for pid in ids:
                p = next(x for x in by_book[book] if x["id"] == pid)
                a, b = parse_page(p["page"])
                intervals.append((max(a, h["page"]), min(b, end)))
            covered = set()
            for a, b in intervals:
                covered.update(range(a, b + 1))
            span = max(end - h["page"] + 1, 1)
            ratio = len(covered) / span
            sec_rows.append({"book": book, "level": h["level"], "num": h["num"],
                             "title": h["title"], "page_start": h["page"], "page_end": end,
                             "points": len(ids), "covered_pages": len(covered),
                             "span": span, "ratio": round(ratio, 3)})
            if ids:
                if h["level"] == 2:
                    l2_cov += 1
                elif h["level"] == 3:
                    l3_cov += 1
            else:
                gaps.append({"book": book, "level": h["level"], "num": h["num"],
                             "title": h["title"], "page": h["page"], "kind": "section"})
            if ratio < 0.5:
                gaps.append({"book": book, "level": h["level"], "num": h["num"],
                             "title": h["title"], "page": h["page"],
                             "kind": f"section-thin({ratio:.0%})"})
        # captions: weak = same page has a point; strong = point cites the number
        cap_cov = cap_strong = 0
        for c in caps:
            digits = re.findall(r"\d+", c["num"])
            ch = int(digits[0]) if digits else 0
            ids = covering_points(by_book[book], ch, c["page"], c["page"])
            if ids:
                cap_cov += 1
            if caption_mentioned(by_book[book], c):
                cap_strong += 1
            else:
                gaps.append({"book": book, "level": "caption", "num": c["num"],
                             "title": c["title"], "page": c["page"], "kind": c["kind"]})
        kb_formulas = sum(1 for r in by_book[book] if r["formula"].strip())
        summary[book] = {
            "l2": len(l2), "l2_cov": l2_cov,
            "l3": len(l3), "l3_cov": l3_cov,
            "caps": len(caps), "cap_cov": cap_cov, "cap_strong": cap_strong,
            "src_formulas": len(formulas), "kb_formulas": kb_formulas,
            "l2_thin": sum(1 for s in sec_rows if s["book"] == book and s["level"] == 2 and s["ratio"] < 0.5),
            "l3_thin": sum(1 for s in sec_rows if s["book"] == book and s["level"] == 3 and s["ratio"] < 0.5),
        }

    os.makedirs(BASE, exist_ok=True)
    with open(os.path.join(BASE, "coverage-gaps.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["book", "level", "num", "title", "page", "kind"])
        w.writeheader()
        w.writerows(gaps)
    with open(os.path.join(BASE, "coverage-sections.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["book", "level", "num", "title", "page_start",
                                          "page_end", "points", "covered_pages", "span", "ratio"])
        w.writeheader()
        w.writerows(sec_rows)

    lines = ["# 四级覆盖审计\n",
             "口径：二级/三级小节按“是否有知识点页码覆盖”判定；图表按“同页是否有知识点”判定，属于弱覆盖，不等于图表内容已结构化。\n",
             "| 书 | 二级节 | 覆盖 | 二级稀薄(<50%) | 三级小节 | 覆盖 | 三级稀薄(<50%) | 图表 | 同页有知识点（弱） | 被知识点引用（强） | 公式候选（启发式） | 库内公式 |",
             "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for book in ("A", "B"):
        s = summary[book]
        lines.append(f"| {book} | {s['l2']} | {s['l2_cov']} | {s['l2_thin']} | {s['l3']} | {s['l3_cov']} | "
                     f"{s['l3_thin']} | {s['caps']} | {s['cap_cov']} | {s['cap_strong']} | "
                     f"{s['src_formulas']} | {s['kb_formulas']} |")
    lines += ["\n## 缺口\n", f"共 {len(gaps)} 条，明细见 `coverage-gaps.csv`。\n"]
    for book in ("A", "B"):
        sub = [g for g in gaps if g["book"] == book]
        lines.append(f"### 书 {book}（{len(sub)} 条）\n")
        for g in sub[:40]:
            lines.append(f"- [{g['kind']} {g['num']}] p.{g['page']} {g['title']}")
        if len(sub) > 40:
            lines.append(f"- ……其余 {len(sub) - 40} 条见 CSV")
        lines.append("")
    open(os.path.join(BASE, "coverage-audit.md"), "w", encoding="utf-8").write("\n".join(lines))
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print("gaps", len(gaps))


if __name__ == "__main__":
    main()
