# -*- coding: utf-8 -*-
"""Build a typed knowledge graph from the point index.

Nodes: Book, Chapter, Section, KnowledgePoint, Dataset, Metric
Edges: part_of, in_section, prerequisite_of, related_to, variant_of,
       mentions_dataset, mentions_metric, canonical_of

Outputs:
  graph/kg-graph.json
  graph/kg-graph.graphml
  graph/kg-graph.ttl
  graph/graph-report.md
"""
import json, os, re, sys
from collections import Counter, defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.dirname(BASE)
ROWS = json.load(open(os.path.join(KB, "kg-knowledge-points.json"), encoding="utf-8"))

REL_TYPES = {"part_of", "in_section", "prerequisite_of", "related_to",
             "variant_of", "improves", "illustrates", "evaluated_on", "reports_metric",
             "mentions_dataset", "mentions_metric", "canonical_of"}

DATASETS = [
    ("DS-FB15K", "FB15K", ["FB15K"]),
    ("DS-FB24K", "FB24K", ["FB24K"]),
    ("DS-FB20K", "FB20K", ["FB20K"]),
    ("DS-FB15KPLUS", "FB15K+", ["FB15K+"]),
    ("DS-FB60K", "FB60K", ["FB60K"]),
    ("DS-FB13", "FB13", ["FB13"]),
    ("DS-WN18", "WN18", ["WN18"]),
    ("DS-WN11", "WN11", ["WN11"]),
    ("DS-NYT", "NYT", ["NYT"]),
    ("DS-DFB1", "DFB-1", ["DFB-1"]),
    ("DS-DFB3", "DFB-3", ["DFB-3"]),
    ("DS-DFB4", "DFB-4", ["DFB-4"]),
    ("DS-SEMEVAL07", "SemEval-2007", ["SemEval2007", "SemEval-2007"]),
    ("DS-WORDSIM240", "Wordsim240", ["Wordsim240", "Wordsim 240"]),
    ("DS-HOWNET", "HowNet", ["HowNet", "知网"]),
    ("DS-LIWC", "LIWC", ["LIWC"]),
    ("DS-LCSTS", "LCSTS", ["LCSTS"]),
    ("DS-SQUAD", "SQuAD", ["SQuAD"]),
    ("DS-WEBQUESTIONS", "WebQuestions", ["WebQuestions"]),
    ("DS-SIMPLEQUESTIONS", "SimpleQuestions", ["SimpleQuestions"]),
    ("DS-METAQA", "MetaQA", ["MetaQA"]),
    ("DS-QALD", "QALD", ["QALD"]),
    ("DS-YAGO", "YAGO", ["YAGO"]),
    ("DS-DBPEDIA", "DBpedia", ["DBpedia"]),
    ("DS-FREEBASE", "Freebase", ["Freebase"]),
    ("DS-WIKIDATA", "Wikidata", ["Wikidata"]),
]

METRICS = [
    ("MT-MR", "MR", ["MR", "平均排名"]),
    ("MT-MRR", "MRR", ["MRR"]),
    ("MT-HIT1", "Hit@1", ["Hit@1", "Hits@1", "一命中率"]),
    ("MT-HIT10", "Hit@10", ["Hit@10", "Hits@10", "十命中率"]),
    ("MT-PN", "P@N", ["P@N", "P@100", "P@200", "P@300"]),
    ("MT-MAP", "MAP", ["MAP", "平均精度均值"]),
    ("MT-MICROF1", "Micro-F1", ["Micro-F1"]),
    ("MT-MACROF1", "Macro-F1", ["Macro-F1"]),
    ("MT-NDCG", "NDCG", ["NDCG"]),
    ("MT-AUC", "AUC", ["AUC"]),
]

# Curated model-family edges: (variant, base)
VARIANTS = [
    ("B-02-02-51", "B-02-02-09"),  # TransH -> TransE
    ("B-02-03-13", "B-02-02-09"),  # TransR -> TransE
    ("B-02-03-14", "B-02-03-13"),  # CTransR -> TransR
    ("B-02-04-18", "B-02-02-09"),  # PTransE -> TransE
    ("B-02-02-52", "B-02-02-09"),  # TransD -> TransE
    ("A-04-03-61", "A-04-03-24"),  # PCNN -> CNN
    ("B-06-03-06", "B-06-03-05"),  # SPSE -> SPWE
    ("B-06-03-07", "B-06-03-05"),  # SPASE -> SPWE
    ("B-06-04-13", "B-06-04-11"),  # CSP -> SPWCF
    ("B-06-04-13", "B-06-04-12"),  # CSP -> SPCSE
    ("B-07-02-04", "B-07-02-03"),  # HDSA -> HD
    ("A-08-03-33", "A-08-03-31"),  # GAT -> GCN
    ("A-08-03-34", "A-08-03-31"),  # GraphSAGE -> GCN
    ("A-08-04-40", "A-08-04-39"),  # CompGCN -> R-GCN
]

# Curated "improves" style edges: (source, target, note)
IMPROVES = [
    ("B-02-03-13", "B-02-02-09", "TransR 相对 TransE"),
    ("B-02-03-14", "B-02-03-13", "CTransR 相对 TransR"),
    ("B-02-04-18", "B-02-02-09", "PTransE 相对 TransE"),
    ("B-02-05-24", "B-02-02-09", "KR-EAR 相对 TransE"),
    ("B-02-06-28", "B-02-02-09", "DKRL 相对 TransE"),
    ("B-02-07-33", "B-02-02-09", "TKRL 相对 TransE"),
    ("B-03-04-10", "B-03-02-84", "HATT 相对普通注意力"),
    ("B-06-04-13", "B-06-03-05", "CSP 相对 SPWE"),
    ("B-07-02-04", "B-07-02-03", "HDSA 相对 HD"),
]


def text_of(r):
    return " ".join([r["title"], r["definition"], r["key_points"], r["formula"]])


def alias_hit(text, alias):
    if re.fullmatch(r"[A-Za-z0-9@+\-]+", alias):
        return re.search(rf"(?<![A-Za-z0-9]){re.escape(alias)}(?![A-Za-z0-9])", text, re.I) is not None
    return alias in text


def main():
    nodes, edges = {}, []
    seen_edges = set()

    def add_node(nid, ntype, label, **props):
        if nid not in nodes:
            nodes[nid] = {"id": nid, "type": ntype, "label": label, **props}

    def add_edge(src, dst, etype, evidence=""):
        if src == dst:
            return
        key = (src, dst, etype)
        if key in seen_edges:
            return
        if src in nodes and dst in nodes and etype in REL_TYPES:
            seen_edges.add(key)
            edges.append({"source": src, "target": dst, "type": etype, "evidence": evidence})

    # hierarchy
    for book in ("A", "B"):
        add_node(f"BOOK-{book}", "Book", f"书{book}")
    for r in ROWS:
        cid = f"CH-{r['book']}-{r['chapter']:02d}"
        sec_part = "-".join(f"{int(x):02d}" for x in r["section"].split(".")[1:])
        sid = f"SEC-{r['book']}-{r['chapter']:02d}-{sec_part}"
        add_node(cid, "Chapter", r["chapter_title"], book=r["book"], chapter=r["chapter"])
        add_node(sid, "Section", r["section_title"], book=r["book"],
                 chapter=r["chapter"], section=r["section"])
        add_edge(cid, f"BOOK-{r['book']}", "part_of")
        add_edge(sid, cid, "part_of")

    # nested section parent (level-3 section -> level-2 section)
    for sid in list(nodes):
        if sid.startswith("SEC-"):
            parts = sid.split("-")
            if len(parts) > 4:
                parent = "-".join(parts[:-1])
                if parent in nodes:
                    add_edge(sid, parent, "part_of")

    # knowledge points
    for r in ROWS:
        add_node(r["id"], "KnowledgePoint", r["title"], point_type=r["type"],
                 book=r["book"], chapter=r["chapter"], section=r["section"],
                 page=r["page"], scope=r["scope"], coverage=r["coverage"])
        sec_part = "-".join(f"{int(x):02d}" for x in r["section"].split(".")[1:])
        sid = f"SEC-{r['book']}-{r['chapter']:02d}-{sec_part}"
        add_edge(r["id"], sid, "in_section")

    # prerequisite / related
    for r in ROWS:
        for pre in [x for x in r["prerequisites"].split("；") if x]:
            add_edge(pre, r["id"], "prerequisite_of", f"{r['id']} 的前置")
        for rel in [x for x in r["related"].split("；") if x]:
            add_edge(r["id"], rel, "related_to", "related 字段")

    # canonical
    for r in ROWS:
        if r["canonical_id"] != r["id"]:
            add_edge(r["id"], r["canonical_id"], "canonical_of", "近重复/跨书重复")

    # figures / tables (section-level attachment only)
    fig_path = os.path.join(KB, "figures", "figure-index.json")
    table_path = os.path.join(KB, "tables", "table-data.json")
    TDATA = {t["id"]: t for t in json.load(open(table_path, encoding="utf-8"))["tables"]} if os.path.exists(table_path) else {}
    if os.path.exists(fig_path):
        figs = json.load(open(fig_path, encoding="utf-8"))

        def section_node(book, chapter, sec):
            parts = [p for p in sec.split(".") if p]
            while parts:
                sec_part = "-".join(f"{int(x):02d}" for x in parts[1:])
                sid = f"SEC-{book}-{chapter:02d}-{sec_part}" if sec_part else None
                if sid and sid in nodes:
                    return sid
                parts = parts[:-1]
            return None

        for f in figs:
            ntype = "Table" if f["kind"] == "表" else "Figure"
            props = dict(book=f["book"], chapter=f["chapter"], number=f["number"],
                         page=f["page"], section=f["section"], role=f["role"],
                         note_status=f["note_status"])
            if f["id"] in TDATA:
                st = TDATA[f["id"]].get("status", "matrix")
                props.update(structured=(st != "index_only"), data_status=st,
                             data_rows=len(TDATA[f["id"]]["rows"]),
                             data_columns=len(TDATA[f["id"]]["columns"]))
            add_node(f["id"], ntype, f["caption"], **props)
            sid = section_node(f["book"], f["chapter"], f["section"])
            for pid in f.get("illustrates", []):
                add_edge(f["id"], pid, "illustrates", "人工图表映射")
            if sid:
                add_edge(f["id"], sid, "in_section")
            else:
                cid = f"CH-{f['book']}-{f['chapter']:02d}"
                if cid in nodes:
                    add_edge(f["id"], cid, "part_of")

    # datasets & metrics
    for did, label, aliases in DATASETS:
        add_node(did, "Dataset", label, aliases=aliases)
    for mid, label, aliases in METRICS:
        add_node(mid, "Metric", label, aliases=aliases)
    for r in ROWS:
        text = text_of(r)
        eval_cues = ("实验", "评测", "评估", "结果", "训练", "基准", "对比", "提升", "优于", "达到")
        is_result = r["type"] in ("案例", "方法", "模型", "算法") and any(c in text for c in eval_cues)
        for did, label, aliases in DATASETS:
            if any(alias_hit(text, a) for a in aliases):
                add_edge(r["id"], did, "evaluated_on" if is_result else "mentions_dataset", label)
        for mid, label, aliases in METRICS:
            if any(alias_hit(text, a) for a in aliases):
                add_edge(r["id"], mid, "reports_metric" if is_result else "mentions_metric", label)

    # curated variants and improvements
    for var, base in VARIANTS:
        if var in nodes and base in nodes:
            add_edge(var, base, "variant_of", "模型族")
    for src, dst, note in IMPROVES:
        if src in nodes and dst in nodes:
            add_edge(src, dst, "improves", note)

    # validate
    errors = []
    for e in edges:
        if e["source"] not in nodes or e["target"] not in nodes:
            errors.append(f"dangling edge {e}")
        if e["type"] not in REL_TYPES:
            errors.append(f"bad relation {e}")
    if errors:
        sys.exit("\n".join(errors[:20]))

    # stats
    deg = Counter()
    for e in edges:
        deg[e["source"]] += 1
        deg[e["target"]] += 1
    node_types = Counter(n["type"] for n in nodes.values())
    edge_types = Counter(e["type"] for e in edges)
    orphans = [n for n in nodes if deg[n] == 0]

    # prerequisite cycles
    adj = defaultdict(list)
    for e in edges:
        if e["type"] == "prerequisite_of":
            adj[e["source"]].append(e["target"])
    color, cycles = {}, []

    def dfs(u, stack):
        color[u] = 1
        stack.append(u)
        for v in adj[u]:
            if color.get(v, 0) == 0:
                dfs(v, stack)
            elif color.get(v) == 1:
                i = stack.index(v)
                cycles.append(stack[i:] + [v])
        stack.pop()
        color[u] = 2

    for n in nodes:
        if color.get(n, 0) == 0:
            dfs(n, [])

    # outputs
    graph = {"nodes": list(nodes.values()), "edges": edges,
             "meta": {"node_types": dict(node_types), "edge_types": dict(edge_types),
                      "relation_types": sorted(REL_TYPES)}}
    json.dump(graph, open(os.path.join(BASE, "kg-graph.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    # GraphML
    def x(s):
        return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                .replace('"', "&quot;"))
    gl = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<graphml xmlns="http://graphml.graphdrawing.org/xmlns">',
          '<key id="type" for="node" attr.name="type" attr.type="string"/>',
          '<key id="label" for="node" attr.name="label" attr.type="string"/>',
          '<key id="rel" for="edge" attr.name="type" attr.type="string"/>',
          '<graph id="kg" edgedefault="directed">']
    for n in nodes.values():
        gl.append(f'<node id="{x(n["id"])}"><data key="type">{x(n["type"])}</data>'
                  f'<data key="label">{x(n["label"])}</data></node>')
    for i, e in enumerate(edges):
        gl.append(f'<edge id="e{i}" source="{x(e["source"])}" target="{x(e["target"])}">'
                  f'<data key="rel">{x(e["type"])}</data></edge>')
    gl.append("</graph></graphml>")
    open(os.path.join(BASE, "kg-graph.graphml"), "w", encoding="utf-8").write("\n".join(gl))

    # Turtle
    def t(s):
        return str(s).replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")
    tt = ['@prefix kg: <http://example.org/kg/> .', '@prefix ex: <http://example.org/kg/node/> .',
          '@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .', ""]
    for n in nodes.values():
        tt.append(f'ex:{n["id"]} a kg:{n["type"]} ; rdfs:label "{t(n["label"])}" .')
    pred = {"part_of": "kg:partOf", "in_section": "kg:inSection",
            "prerequisite_of": "kg:prerequisiteOf", "related_to": "kg:relatedTo",
            "variant_of": "kg:variantOf", "improves": "kg:improves",
            "illustrates": "kg:illustrates",
            "evaluated_on": "kg:evaluatedOn", "reports_metric": "kg:reportsMetric",
            "mentions_dataset": "kg:mentionsDataset",
            "mentions_metric": "kg:mentionsMetric", "canonical_of": "kg:canonicalOf"}
    for e in edges:
        tt.append(f'ex:{e["source"]} {pred[e["type"]]} ex:{e["target"]} .')
    open(os.path.join(BASE, "kg-graph.ttl"), "w", encoding="utf-8").write("\n".join(tt))

    # report
    top = deg.most_common(15)
    lines = ["# 知识图谱导出报告\n",
             "## 规模\n",
             f"- 节点：{len(nodes)}",
             f"- 边：{len(edges)}",
             f"- 关系类型：{len(edge_types)}",
             f"- 孤立节点：{len(orphans)}",
             f"- 前置环：{len(cycles)}",
             f"- 结构化表格：{sum(1 for n in nodes.values() if n.get('structured'))}",
             "\n## 节点类型\n", "| 类型 | 数量 |", "|---|---:|"]
    for k, v in node_types.most_common():
        lines.append(f"| {k} | {v} |")
    lines += ["\n## 关系类型\n", "| 关系 | 数量 |", "|---|---:|"]
    for k, v in edge_types.most_common():
        lines.append(f"| {k} | {v} |")
    lines += ["\n## 高度节点 Top 15\n", "| 节点 | 标题 | 度数 |", "|---|---|---:|"]
    for nid, d in top:
        lines.append(f"| {nid} | {nodes[nid]['label']} | {d} |")
    if cycles:
        lines += ["\n## 前置环（需人工确认）\n"]
        for c in cycles[:10]:
            lines.append("- " + " → ".join(c))
    if orphans:
        lines += ["\n## 孤立节点\n"]
        for nid in orphans[:20]:
            lines.append(f"- {nid} {nodes[nid]['label']}")
    open(os.path.join(BASE, "graph-report.md"), "w", encoding="utf-8").write("\n".join(lines))

    print(json.dumps({"nodes": len(nodes), "edges": len(edges),
                      "node_types": node_types, "edge_types": edge_types,
                      "orphans": len(orphans), "cycles": len(cycles)},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
