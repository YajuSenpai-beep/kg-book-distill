# -*- coding: utf-8 -*-
"""Build a method/dataset/metric/task instance graph from the point graph.

This is a meta-KG of methods, datasets, metrics and tasks mentioned in the two
books, not a domain instance KG (no patients/drugs/companies).

Outputs:
  instances/instance-graph.json
  instances/instance-graph.graphml
  instances/instance-graph.ttl
  instances/instance-report.md
"""
import json, os, re, sys
from collections import Counter

BASE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.dirname(BASE)
ROWS = json.load(open(os.path.join(KB, "kg-knowledge-points.json"), encoding="utf-8"))
MAIN = json.load(open(os.path.join(KB, "graph", "kg-graph.json"), encoding="utf-8"))
SPEC = json.load(open(os.path.join(BASE, "methods.json"), encoding="utf-8"))
REL = {"solves", "evaluated_on", "reports_metric", "mentions_dataset", "mentions_metric", "variant_of", "improves", "uses"}


def norm(s):
    return re.sub(r"[\s_\-/]", "", s.lower())


def resolve(label, aliases):
    names = [label] + aliases
    normed = {norm(x) for x in names}
    exact, starts, contains = [], [], []
    for r in ROWS:
        t = r["title"]
        nt = norm(t)
        if nt in normed:
            exact.append(r)
        elif any(nt.startswith(norm(x)) for x in names):
            starts.append(r)
        elif any(norm(x) in nt for x in names) and len(t) <= 40:
            contains.append(r)
    pool = exact or starts or contains
    if not pool:
        return None
    # prefer model/algorithm points, then the shortest title
    pool.sort(key=lambda r: (r["type"] not in ("模型", "算法", "方法"), len(r["title"])))
    return pool[0]


def main():
    nodes, edges = {}, []
    point_to_method = {}
    point_to_methods = {}

    def add_node(nid, ntype, label, **props):
        nodes.setdefault(nid, {"id": nid, "type": ntype, "label": label, **props})

    def add_edge(s, t, r, evidence=""):
        if s in nodes and t in nodes and s != t and r in REL:
            edges.append({"source": s, "target": t, "type": r, "evidence": evidence})

    # tasks
    for t in SPEC["tasks"]:
        add_node(t["id"], "Task", t["label"])

    # methods
    unresolved = []
    for m in SPEC["methods"]:
        rep = resolve(m["label"], m["aliases"])
        add_node(m["id"], "Method", m["label"], aliases=m["aliases"],
                 point_id=rep["id"] if rep else "", book=rep["book"] if rep else "",
                 page=rep["page"] if rep else "")
        if rep:
            point_to_method[rep["id"]] = m["id"]
        else:
            unresolved.append(m["label"])
        names = [m["label"]] + m["aliases"]
        for r in ROWS:
            nt = norm(r["title"])
            if len(r["title"]) <= 40 and any(norm(x) in nt for x in names):
                point_to_methods.setdefault(r["id"], set()).add(m["id"])
        for task in m.get("tasks", []):
            add_edge(m["id"], task, "solves", "任务映射")

    # datasets / metrics from the main graph
    for n in MAIN["nodes"]:
        if n["type"] in ("Dataset", "Metric"):
            add_node(n["id"], n["type"], n["label"], **{k: v for k, v in n.items()
                                                       if k not in ("id", "type", "label")})

    # point-level edges -> method-level edges
    for e in MAIN["edges"]:
        if e["type"] not in ("mentions_dataset", "mentions_metric", "evaluated_on", "reports_metric", "variant_of", "improves"):
            continue
        srcs = point_to_methods.get(e["source"], set())
        if not srcs:
            continue
        if e["type"] in ("mentions_dataset", "mentions_metric", "evaluated_on", "reports_metric"):
            dst = e["target"] if e["target"] in nodes else None
            if dst:
                for src in srcs:
                    add_edge(src, dst, e["type"], e.get("evidence", ""))
        else:
            # variant/improve edges point to point IDs; map via title of target
            tgt_point = e["target"]
            tgt = None
            for m in SPEC["methods"]:
                if m["id"] == point_to_method.get(tgt_point):
                    tgt = m["id"]
                    break
            if not tgt:
                for m in SPEC["methods"]:
                    rep = point_to_method.get(tgt_point)
                    if rep:
                        tgt = rep
                        break
            # fallback: map by target title
            if not tgt:
                for r in ROWS:
                    if r["id"] == tgt_point:
                        for m in SPEC["methods"]:
                            if norm(m["label"]) in norm(r["title"]):
                                tgt = m["id"]
                                break
                        break
            if tgt:
                add_edge(src, tgt, "variant_of" if e["type"] == "variant_of" else "improves",
                         e.get("evidence", ""))

    # curated uses
    for a, b in SPEC.get("uses", []):
        add_edge(a, b, "uses", "方法依赖")

    # validate
    errors = []
    for e in edges:
        if e["source"] not in nodes or e["target"] not in nodes:
            errors.append(e)
    if errors:
        sys.exit(f"dangling edges: {errors[:5]}")

    graph = {"nodes": list(nodes.values()), "edges": edges,
             "meta": {"node_types": dict(Counter(n["type"] for n in nodes.values())),
                      "edge_types": dict(Counter(e["type"] for e in edges)),
                      "unresolved_methods": unresolved}}
    json.dump(graph, open(os.path.join(BASE, "instance-graph.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    def x(s):
        return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                .replace('"', "&quot;"))
    gl = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<graphml xmlns="http://graphml.graphdrawing.org/xmlns">',
          '<key id="type" for="node" attr.name="type" attr.type="string"/>',
          '<key id="label" for="node" attr.name="label" attr.type="string"/>',
          '<key id="rel" for="edge" attr.name="type" attr.type="string"/>',
          '<graph id="instances" edgedefault="directed">']
    for n in nodes.values():
        gl.append(f'<node id="{x(n["id"])}"><data key="type">{x(n["type"])}</data>'
                  f'<data key="label">{x(n["label"])}</data></node>')
    for i, e in enumerate(edges):
        gl.append(f'<edge id="e{i}" source="{x(e["source"])}" target="{x(e["target"])}">'
                  f'<data key="rel">{x(e["type"])}</data></edge>')
    gl.append("</graph></graphml>")
    open(os.path.join(BASE, "instance-graph.graphml"), "w", encoding="utf-8").write("\n".join(gl))

    pred = {"solves": "kg:solves", "evaluated_on": "kg:evaluatedOn",
            "reports_metric": "kg:reportsMetric", "mentions_dataset": "kg:mentionsDataset",
            "mentions_metric": "kg:mentionsMetric", "variant_of": "kg:variantOf",
            "improves": "kg:improves", "uses": "kg:uses"}
    tt = ['@prefix kg: <http://example.org/kg/> .', '@prefix ex: <http://example.org/kg/node/> .',
          '@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .', ""]
    for n in nodes.values():
        tt.append(f'ex:{n["id"]} a kg:{n["type"]} ; rdfs:label "{str(n["label"]).replace(chr(34), chr(39))}" .')
    for e in edges:
        tt.append(f'ex:{e["source"]} {pred[e["type"]]} ex:{e["target"]} .')
    open(os.path.join(BASE, "instance-graph.ttl"), "w", encoding="utf-8").write("\n".join(tt))

    lines = ["# 实例层图谱报告\n",
             f"- 节点：{len(nodes)}",
             f"- 边：{len(edges)}",
             f"- 方法：{sum(1 for n in nodes.values() if n['type'] == 'Method')}",
             f"- 任务：{sum(1 for n in nodes.values() if n['type'] == 'Task')}",
             f"- 数据集：{sum(1 for n in nodes.values() if n['type'] == 'Dataset')}",
             f"- 指标：{sum(1 for n in nodes.values() if n['type'] == 'Metric')}",
             f"- 未解析方法：{len(unresolved)}", "",
             "## 未解析方法\n"]
    lines += [f"- {x}" for x in unresolved] or ["- 无"]
    lines += ["\n## 关系\n", "| 关系 | 数量 |", "|---|---:|"]
    for k, v in Counter(e["type"] for e in edges).most_common():
        lines.append(f"| {k} | {v} |")
    open(os.path.join(BASE, "instance-report.md"), "w", encoding="utf-8").write("\n".join(lines))
    print(json.dumps({"nodes": len(nodes), "edges": len(edges),
                      "unresolved": unresolved}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
