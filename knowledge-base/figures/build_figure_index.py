# -*- coding: utf-8 -*-
"""Build a figure/table index with page, section, context and linked points.

Inputs:
  ../extracted/book-*.md
  kg-knowledge-points.json
Outputs:
  figures/figure-index.json
  figures/figure-index.csv
  figures/figure-index.md
  obsidian/40-图表索引.md
"""
import csv, json, os, re
from collections import Counter, defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.dirname(BASE)
ROOT = os.path.dirname(KB)
SRC = {
    "A": os.path.join(ROOT, "extracted", "book-a-知识图谱导论.md"),
    "B": os.path.join(ROOT, "extracted", "book-b-知识图谱与深度学习.md"),
}
ROWS = json.load(open(os.path.join(KB, "kg-knowledge-points.json"), encoding="utf-8"))
MAP_PATH = os.path.join(BASE, "illustrates-map.json")
ILLUSTRATES = json.load(open(MAP_PATH, encoding="utf-8")) if os.path.exists(MAP_PATH) else {}
TABLE_PATH = os.path.join(KB, "tables", "table-data.json")
TABLE_NOTES = ({t["id"]: t.get("note", "") for t in json.load(open(TABLE_PATH, encoding="utf-8"))["tables"]}
               if os.path.exists(TABLE_PATH) else {})

CAP_RE = re.compile(r"^(图|表)\s*([0-9]+)\s*[.\-–—]\s*([0-9]+)\s*(.*)$")
NUM_RE = re.compile(r"^([1-9])\.(\d{1,2})(?:\.(\d{1,2}))?$")
BAD_TITLE = ("所示", "中", "给出", "展示", "可以", "为", "是", "和", "与", "及", "的",
             "从这", "如表", "其中", "我们", "由此", "因此")

# Hand-written notes for the most important experiment/architecture exhibits.
CURATED = {
    "B:表2-1": "TransR/CTransR 在 WN18/FB15K 上的链接预测结果；按 raw/filtered、MR/Hits@10、unif/bern 对比。",
    "B:表2-2": "FB15K 按 1-1/1-N/N-1/N-N 切片的结果；TransR/CTransR 在多对一关系上提升最大。",
    "B:表2-4": "WN11/FB13/FB15K 三元组分类结果；FB13 更稠密，NTN 仍占优。",
    "B:表2-5": "FB15K 实体预测；PTransE 的 ADD 组合与 2/3 步路径对比。",
    "B:表2-6": "PTransE 按关系基数切片的结果；四类关系上均有提升。",
    "B:表2-9": "KR-EAR 在 FB24K 的实体预测；分头/尾实体与合计报告 MR/Hits@10。",
    "B:表2-10": "KR-EAR 关系预测；CRA 属性相关性约束的增益。",
    "B:表2-11": "KR-EAR 属性预测；AC 属性相关性的增益。",
    "B:表2-13": "DKRL 在 FB15K 的实体预测；CNN+TransE 的结构+描述联合表示最好。",
    "B:表2-14": "DKRL 在 FB15K 的关系预测；一命中率对比。",
    "B:表2-16": "DKRL 实体类型分类 MAP；BOW/TransE/DKRL(CBOW)/DKRL(CNN) 对比。",
    "B:表2-17": "DKRL 在 FB20K 的零样本实体预测；d-e/e-d/d-d 四组。",
    "B:表2-18": "DKRL 在 FB20K 的零样本关系预测；d-d 类因自环而虚高。",
    "B:表2-20": "TKRL 在 FB15K 的实体预测；RHE/WHE、+STC 类型约束对比。",
    "B:表2-21": "TKRL 在 FB15K 的关系预测；类型特化映射矩阵的效果。",
    "B:表2-23": "TKRL 在 FB15K+ 长尾关系上的结果；按关系频次分组。",
    "B:表3-2": "CNN/PCNN 在 One/Two/All 实例设置下的 P@N；选择性注意力的增益。",
    "B:表3-5": "HATT 与普通注意力在不同召回率、微平均/宏平均上的对比。",
    "B:表3-6": "HATT 在长尾关系（训练实例 <100/<200）上的 Hits@K。",
    "B:表3-7": "MNRE 中英双语数据统计；176 种关系、百万级实例。",
    "B:表3-14": "FB15K/FB60K 与 NYT-FB15K/NYT-FB60K 的规模统计。",
    "B:表3-16": "联合学习中 ONE/ATT/KATT 三种跨句合并机制的 P@N。",
    "B:表4-6": "DFB-1/2/3 实体对齐数据集统计；子图规模与重叠率。",
    "B:表4-7": "IPTransE 软对齐在 DFB-1/2/3 上的实体对齐结果。",
    "B:表4-8": "对齐辅助的图谱补全；实体预测与关系预测的 MR/Hits@10/Hits@1。",
    "B:表4-9": "EDRM 在 Testing-SAME/DIFF/RAW 三场景的排序指标。",
    "B:表5-1": "义原词表示在 Wordsim240 上的词相似度相关系数。",
    "B:表5-2": "义原模型在 SemEval2007 中文词义消歧上的准确率。",
    "B:表5-7": "SAT/SSA/SAC 等模型的词类比准确率与平均排序。",
    "B:表6-1": "SPWE/SPSE/SPASE 及集成模型的义原预测 MAP。",
    "B:表6-3": "不同词性下的义原预测 MAP；名词最高。",
    "B:表6-4": "不同词频下的义原预测 MAP；低频词更高。",
    "B:表6-5": "外部/内部/集成模型的义原预测 MAP；CSP 最好。",
    "B:表6-6": "CSP 在不同词频段上的 MAP；内部模型对低频更稳。",
    "B:表7-2": "HDSA/HD 在 LIWC 三层标签上的 Micro-F1 与 W-M-F1。",
    "B:表7-5": "SDLM 与 MoS/AWD-LSTM 在《人民日报》上的困惑度。",
    "B:表7-6": "SDLM 在单义词/多义词上的困惑度增益。",
    "B:表7-7": "SDLM 随义原数量增加的困惑度增益。",
    "B:表7-8": "LCSTS 标题生成的 ROUGE-1/2/L。",
    "A:表9-4": "PKGM 增强 BERT 的商品分类结果；Hit@1/3/10 与准确率。",
    "A:表9-5": "PKGM 增强 BERT 的同款商品对齐准确率。",
    "A:表9-6": "PKGM 增强 NCF 的商品推荐结果；leave-one-out。",
    "A:表7-1": "常见知识图谱问答数据集对比。",
    "B:表7-1": "LIWC 词典统计：6828 词、51 标签、3 层（10/34/7）。",
    "A:表5-1": "规则推理的示例规则集。",
    "A:表5-2": "OWL 各类构造的语法示例。",
    "A:表5-3": "OWL 公理/构造的语法对照。",
    "A:表5-4": "知识图谱嵌入的代表性模型列表。",
    "A:表5-5": "EL 本体语言的构造示例。",
    "A:表9-1": "事理知识图谱与传统知识图谱的维度对比。",
    "A:表9-2": "因果/条件/反转/顺承四类事理逻辑关系。",
    "A:表9-3": "PKGM 预训练阶段与服务阶段的函数对照。",
    "A:表9-7": "知识价值曲线各阶段的特点。",
    "B:表2-3": "CTransR 对“地区包含”关系的子关系聚类样例。",
    "B:表2-7": "PTransE 关系预测的 MR 与 Hits@1。",
    "B:表2-8": "属性、关系及映射属性的例子，说明属性是一对多/多对一来源。",
    "B:表2-12": "KR-EAR 学到的属性相关对。",
    "B:表2-15": "Freebase 高频实体类型及频次。",
    "B:表2-19": "DKRL 零样本实体类型分类 MAP。",
    "B:表2-22": "测试时类型限制（TCE）对实体预测的提升。",
    "B:表2-24": "TKRL 三元组分类结果。",
    "B:表2-25": "IKRL 在 WN9-IMG 上的实体预测结果。",
    "B:表2-26": "IKRL 在 WN9-IMG 上的三元组分类结果。",
    "B:表2-27": "IKRL 在 WN9-IMG 上的实体分类结果。",
    "B:表3-1": "PCNN/CNN 远程监督抽取的超参数。",
    "B:表3-3": "NYT 上选择性注意力的高分/低分句示例。",
    "B:表3-4": "HATT 超参数。",
    "B:表3-8": "MNRE 超参数。",
    "B:表3-9": "中英句子对的跨语言注意力权重。",
    "B:表3-10": "中英文训练样例不平衡关系的预测准确率。",
    "B:表3-11": "联合抽取超参数。",
    "B:表3-12": "多语言关系抽取各模型 AUC。",
    "B:表3-13": "单语言场景各模型 AUC。",
    "B:表3-15": "KATT 联合学习超参数。",
    "B:表3-17": "JointE/JointD+SATT 分关系类型的头尾实体 Hits@10。",
    "B:表4-1": "FIGER/WIKI-AUTO/WIKI 等实体类型数据集对比。",
    "B:表4-2": "KNET 最优超参数。",
    "B:表4-3": "WIKI-AUTO 上实体分类表现（严格/宏平均/微平均）。",
    "B:表4-4": "不同粗粒度类型上的效果比较。",
    "B:表4-5": "正确集与错误集上的模型表现。",
    "B:表4-10": "EDRM 在 K-NRM/Conv-KNRM 上增加语义的消融。",
    "B:表4-11": "EDRM 排序的查询-文档样例。",
    "B:表4-12": "EDRM 的错误样例分析。",
    "B:表5-3": "义项与义原向量的最近邻词。",
    "B:表5-4": "义原向量的最近邻义原。",
    "B:表5-5": "低频词在 CBOW 与义原模型下的最近邻对比。",
    "B:表5-6": "SAT/SSA/SAC 在 Wordsim240/297 上的相关系数。",
    "B:表5-8": "不同上下文下义原注意力权重示例。",
    "B:表5-9": "义原对词义的注意力权重。",
    "B:表6-2": "SPWE+SPSE 对 5 个词的 Top-5 义原预测。",
    "B:表6-7": "内部/外部/集成模型对复合词与音译词的预测。",
    "B:表6-8": "跨语言义原预测随种子词典规模的变化。",
    "B:表6-9": "目标语言词的前 5 义原与最近中文词。",
    "B:表6-10": "跨语言预测在不同词频段的结果。",
    "B:表6-11": "跨语言实验的双语数据构建统计。",
    "B:表6-12": "跨语言词相似度与义原预测指标。",
    "B:表7-3": "HDSA 每层加权平均精度与召回。",
    "B:表7-4": "义原帮助 HDSA 纠正/出错的例子。",
    "B:表7-9": "SDLM 在《人民日报》测试句上的词与义原预测。",
    "B:表7-10": "SDLM 在 LCSTS 上生成的标题样例。",
}


def page_of_line(lines):
    pages, cur = [], 0
    for line in lines:
        m = re.match(r"<!--\s*p\.(\d+)\s*-->", line.strip())
        if m:
            cur = int(m.group(1))
        pages.append(cur)
    return pages


def parse_headings(book, lines, pages):
    out = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        page = pages[i]
        hm = re.match(r"^(#{2,5})\s*(\d+(?:\.\d+){1,2})\s*(.*)$", line)
        if hm and NUM_RE.match(hm.group(2)):
            title = re.sub(r"\s+\d+\s*$", "", hm.group(3)).strip()
            out.append({"num": hm.group(2), "title": title, "page": page,
                        "level": hm.group(2).count(".") + 1})
            i += 1
            continue
        if book == "B" and page >= 14:
            sm = re.match(r"^(\d+(?:\.\d+){1,2})\s+(\S.*)$", line)
            bm = re.match(r"^(\d+(?:\.\d+){1,2})$", line)
            num, title = None, ""
            if sm and NUM_RE.match(sm.group(1)):
                num, title = sm.group(1), sm.group(2).strip()
            elif bm and NUM_RE.match(bm.group(1)):
                num = bm.group(1)
                for j in range(i + 1, min(i + 4, len(lines))):
                    nxt = lines[j].strip()
                    if nxt and not re.match(r"^\d+(?:\.\d+)*$", nxt):
                        title = nxt
                        break
            if num:
                ch = int(num.split(".")[0])
                maxsec = {1: 5, 2: 9, 3: 8, 4: 5, 5: 5, 6: 6, 7: 4, 8: 3}.get(ch, 0)
                sec = int(num.split(".")[1])
                if (ch <= 8 and 1 <= sec <= maxsec and CJK_OK(title)
                        and len(title) <= 40 and not title.startswith(BAD_TITLE)):
                    out.append({"num": num, "title": title, "page": page,
                                "level": num.count(".") + 1})
        i += 1
    seen, uniq = set(), []
    for h in out:
        if h["num"] in seen:
            continue
        seen.add(h["num"])
        uniq.append(h)
    return uniq


def CJK_OK(s):
    return re.search(r"[一-鿿]{2,}", s or "") is not None


def parse_captions(lines, pages):
    caps, seen = [], set()
    for i, raw in enumerate(lines):
        line = raw.strip()
        m = CAP_RE.match(line)
        if not m:
            continue
        kind, a, b, title = m.group(1), m.group(2), m.group(3), m.group(4).strip()
        num = f"{kind}{a}-{b}"
        if num in seen:
            continue
        if not title or len(title) < 2:
            for j in range(i + 1, min(i + 4, len(lines))):
                nxt = lines[j].strip()
                if nxt and not re.match(r"^(图|表)\s*\d", nxt):
                    title = nxt
                    break
        if not title or title.startswith(BAD_TITLE) or len(title) > 80:
            continue
        # context: two lines before, three after (skip page markers / headings)
        ctx = []
        for j in range(max(0, i - 3), min(len(lines), i + 4)):
            t = lines[j].strip()
            if not t or t.startswith("<!--") or re.match(r"^#{2,5}\s", t):
                continue
            if j == i:
                continue
            ctx.append(t)
        seen.add(num)
        caps.append({"num": num, "kind": kind, "title": title, "page": pages[i],
                     "context": " ".join(ctx)[:300]})
    return caps


def section_for(headings, ch, page):
    cands = [h for h in headings if int(h["num"].split(".")[0]) == ch and h["page"] <= page]
    if not cands:
        return None
    # prefer the most specific heading on the page or the last preceding one
    return max(cands, key=lambda h: (h["page"], h["level"]))


def linked_points(book, ch, sec_num, page):
    out = []
    for r in ROWS:
        if r["book"] != book or r["chapter"] != ch:
            continue
        if sec_num and (r["section"] == sec_num
                        or r["section"].startswith(sec_num + ".")
                        or sec_num.startswith(r["section"] + ".")):
            out.append(r["id"])
            continue
        m = re.search(r"p\.\s*(\d+)(?:\s*[-–—]\s*(\d+))?", r["page"])
        if m:
            a = int(m.group(1)); b = int(m.group(2) or a)
            if a <= page <= b:
                out.append(r["id"])
    return out[:5]


def role_of(kind, title):
    if kind == "表":
        if any(k in title for k in ("结果", "评测", "实验", "对比", "统计", "指标")):
            return "实验结果表"
        if any(k in title for k in ("数据", "规模", "统计")):
            return "数据统计表"
        return "数据表"
    if any(k in title for k in ("架构", "框架", "流程", "模型", "结构")):
        return "架构/流程图"
    if any(k in title for k in ("示例", "例子", "样例")):
        return "示例图"
    return "示意图"


def main():
    if not all(os.path.exists(p) for p in SRC.values()):
        print("skip: source text not available; keep existing figure-index.json")
        return
    records = []
    for book in ("A", "B"):
        lines = open(SRC[book], encoding="utf-8").read().splitlines()
        pages = page_of_line(lines)
        heads = parse_headings(book, lines, pages)
        caps = parse_captions(lines, pages)
        for c in caps:
            ch = int(re.sub(r"\D", "", c["num"].split("-")[0]) or 0)
            sec = section_for(heads, ch, c["page"])
            sec_num = sec["num"] if sec else ""
            rec = {
                "id": f"{'TAB' if c['kind'] == '表' else 'FIG'}-{book}-{c['num'][1:].replace('-', '-')}",
                "book": book, "chapter": ch, "kind": c["kind"], "number": c["num"],
                "caption": c["title"], "page": c["page"],
                "section": sec_num, "section_title": sec["title"] if sec else "",
                "role": role_of(c["kind"], c["title"]),
                "context": c["context"],
                "linked_points": linked_points(book, ch, sec_num, c["page"]),
                "illustrates": ILLUSTRATES.get(f"{'TAB' if c['kind'] == '表' else 'FIG'}-{book}-{c['num'][1:]}", []),
                "note": TABLE_NOTES.get(
                    f"{'TAB' if c['kind'] == '表' else 'FIG'}-{book}-{c['num'][1:]}",
                    CURATED.get(f"{book}:{c['num']}", "")),
                "note_status": "curated" if f"{book}:{c["num"]}" in CURATED else "auto",
            }
            records.append(rec)
    def num_key(r):
        m = re.match(r"([图表])(\d+)-(\d+)", r["number"])
        return (r["book"], r["chapter"], int(m.group(2)) if m else 0,
                int(m.group(3)) if m else 0)

    records.sort(key=num_key)
    os.makedirs(BASE, exist_ok=True)
    json.dump(records, open(os.path.join(BASE, "figure-index.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    with open(os.path.join(BASE, "figure-index.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "book", "chapter", "kind", "number", "caption",
                                          "page", "section", "section_title", "role",
                                          "note_status", "linked_points", "illustrates", "note", "context"])
        w.writeheader()
        for r in records:
            row = dict(r)
            row["linked_points"] = "；".join(r["linked_points"])
            row["illustrates"] = "；".join(r["illustrates"])
            w.writerow(row)

    by_book = Counter(r["book"] for r in records)
    by_kind = Counter(r["kind"] for r in records)
    curated = sum(1 for r in records if r["note_status"] == "curated")
    lines = ["# 图表索引\n",
             f"- 总数：{len(records)}（图 {by_kind.get('图', 0)} / 表 {by_kind.get('表', 0)}）",
             f"- 书 A：{by_book.get('A', 0)}；书 B：{by_book.get('B', 0)}",
             f"- 人工要点：{curated} 条；其余由标题/上下文自动生成",
             "\n口径：每条记录含图注、页码、所属小节、角色、上下文和关联知识点；`note` 为空时看 `context`。\n"]
    for book in ("A", "B"):
        lines += [f"## 书 {book}\n", "| 编号 | 图注 | 页 | 小节 | 角色 | 精确关联 | 关联知识点 |", "|---|---|---:|---|---|---|---|"]
        for r in records:
            if r["book"] != book:
                continue
            pts = "、".join(r["linked_points"][:3]) or "—"
            ill = "、".join(r.get("illustrates", [])) or "—"
            lines.append(f"| {r['number']} | {r['caption']} | {r['page']} | {r['section']} | {r['role']} | {ill} | {pts} |")
        lines.append("")
    open(os.path.join(BASE, "figure-index.md"), "w", encoding="utf-8").write("\n".join(lines))

    # Obsidian single index
    obs = os.path.join(KB, "obsidian", "40-图表索引.md")
    out = ["# 图表索引\n", f"共 {len(records)} 条（图 {by_kind.get('图',0)} / 表 {by_kind.get('表',0)}）。\n"]
    for book in ("A", "B"):
        out += [f"## 书 {book}\n", "| 编号 | 图注 | 页 | 小节 | 关联知识点 |", "|---|---|---:|---|---|"]
        for r in records:
            if r["book"] != book:
                continue
            pts = "、".join(r["linked_points"][:3]) or "—"
            ill = "、".join(r.get("illustrates", [])) or "—"
            out.append(f"| {r['number']} | {r['caption']} | {r['page']} | {r['section']} | {ill} | {pts} |")
        out.append("")
    open(obs, "w", encoding="utf-8").write("\n".join(out))
    print(json.dumps({"total": len(records), "by_book": by_book, "by_kind": by_kind,
                      "curated": curated}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
