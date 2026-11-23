# -*- coding: utf-8 -*-
"""End-to-end consistency check for the knowledge base, figure index and graph.

Outputs audit/final-verification.md. Exits non-zero if any hard check fails.
"""
import csv, glob, json, os, re, sys

BASE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.dirname(BASE)
PUBLIC_MODE = not os.path.exists(os.path.join(KB, "figures", "pages"))
checks = []


def add(name, ok, detail=""):
    checks.append((name, bool(ok), detail))


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main():
    rows = load(os.path.join(KB, "kg-knowledge-points.json"))
    figs = load(os.path.join(KB, "figures", "figure-index.json"))
    graph = load(os.path.join(KB, "graph", "kg-graph.json"))
    nodes = {n["id"]: n for n in graph["nodes"]}
    ids = {r["id"] for r in rows}

    add("知识点 770", len(rows) == 770, f"实际 {len(rows)}")
    add("书 A 419 / 书 B 351",
        sum(1 for r in rows if r["book"] == "A") == 419
        and sum(1 for r in rows if r["book"] == "B") == 351)
    add("节 94", len({(r["book"], r["chapter"], r["section"]) for r in rows}) == 94)
    add("ID 唯一", len(ids) == len(rows))
    add("字段完整", all(r["title"] and r["definition"] and r["page"] for r in rows))
    add("引用无悬空",
        all(x in ids for r in rows
            for x in (r["prerequisites"].split("；") + r["related"].split("；")) if x))

    add("图表 442（图 342 / 表 100）", len(figs) == 442
        and sum(1 for f in figs if f["kind"] == "图") == 342
        and sum(1 for f in figs if f["kind"] == "表") == 100)
    add("图表 ID 唯一", len({f["id"] for f in figs}) == len(figs))
    add("全部表格有表注", sum(1 for f in figs if f["kind"] == "表" and f["note"]) == 100)
    ill = [f for f in figs if f.get("illustrates")]
    add("精确图表关联 44 条 / 46 边", len(ill) == 44
        and sum(len(f["illustrates"]) for f in ill) == 46)
    add("图表关联点存在",
        all(p in ids for f in figs for p in f.get("illustrates", [])))

    rel_types = {"part_of", "in_section", "prerequisite_of", "related_to",
                 "variant_of", "improves", "illustrates", "evaluated_on",
                 "reports_metric", "mentions_dataset", "mentions_metric",
                 "canonical_of"}
    idx_ok = all(os.path.exists(os.path.join(KB, "search", name))
                 for name in ("unified_vectors.npz", "vector_index.npz"))
    add("向量索引存在", idx_ok or PUBLIC_MODE,
        "source_hash 自愈；run_all --with-vector 强制刷新；公开包可缺省")
    add("图谱 1361 节点", len(graph["nodes"]) == 1361, f"实际 {len(graph['nodes'])}")
    add("图谱 3140 边", len(graph["edges"]) == 3140, f"实际 {len(graph['edges'])}")
    add("图谱端点完整",
        all(e["source"] in nodes and e["target"] in nodes for e in graph["edges"]))
    add("图谱关系类型合法", all(e["type"] in rel_types for e in graph["edges"]))
    add("图谱无自环", all(e["source"] != e["target"] for e in graph["edges"]))
    add("图表节点 442", sum(1 for n in graph["nodes"] if n["type"] in ("Figure", "Table")) == 442)

    tables = load(os.path.join(KB, "tables", "table-data.json"))["tables"]
    fig_map = {f["id"]: f for f in figs}
    note_diff = [t["id"] for t in tables if fig_map.get(t["id"], {}).get("note") != t.get("note", "")]
    add("图表/表格注一致", not note_diff, f"{len(note_diff)} 条不一致")
    status = {}
    for t in tables:
        status[t.get("status")] = status.get(t.get("status"), 0) + 1
    add("表格记录 100 张", len(tables) == 100, f"实际 {len(tables)}")
    add("表格状态 37/5/58",
        status.get("matrix") == 37 and status.get("key_value") == 5
        and status.get("index_only") == 58, str(status))
    val = open(os.path.join(KB, "tables", "table-validation.md"), encoding="utf-8").read()
    add("表格校验 PASS", "结论：PASS" in val)
    add("图谱标记结构化表 42",
        sum(1 for n in graph["nodes"] if n.get("structured")) == 42)

    inst = load(os.path.join(KB, "instances", "instance-graph.json"))
    add("实例层 118 节点 / 176 边", len(inst["nodes"]) == 118 and len(inst["edges"]) == 176)
    add("实例层无未解析方法", inst["meta"]["unresolved_methods"] == [])
    gloss = load(os.path.join(KB, "glossary", "terms.json"))["terms"]
    add("术语表 40 条", len(gloss) == 40)
    add("上下文答案评估报告存在",
        os.path.exists(os.path.join(KB, "eval", "report-answer-context.md")))
    add("真实场景重复/追问报告",
        os.path.exists(os.path.join(KB, "..", "outputs", "kg-engineering", "evals", "backtest-real-stability.md")))
    add("真实场景回测报告",
        os.path.exists(os.path.join(KB, "..", "outputs", "kg-engineering", "evals", "backtest-real.md")))
    add("引用 NLI 报告",
        os.path.exists(os.path.join(KB, "llm", "nli-report.md")))
    add("多查询对比报告",
        os.path.exists(os.path.join(KB, "eval", "report-multi-query.md")))
    add("公开包存在",
        PUBLIC_MODE or os.path.exists(os.path.join(KB, "..", "dist", "kg-public.zip")))
    add("公开发布检查报告",
        os.path.exists(os.path.join(KB, "..", "audit", "public-release-report.md")))
    add("生成式答案对比报告",
        os.path.exists(os.path.join(KB, "llm", "report-generated-compare.md")))
    add("答案级评估报告",
        os.path.exists(os.path.join(KB, "eval", "report-answer-quality.md")))
    add("统一检索答案报告",
        os.path.exists(os.path.join(KB, "eval", "report-unified-answer.md")))
    add("多模态索引",
        os.path.exists(os.path.join(KB, "figures", "multimodal_index.npz")))
    add("图谱边审计",
        os.path.exists(os.path.join(KB, "graph", "edge-audit-full.md")))
    add("P2 边界文档存在",
        os.path.exists(os.path.join(BASE, "content-scope.md"))
        and os.path.exists(os.path.join(BASE, "cross-book-conflicts.md"))
        and os.path.exists(os.path.join(BASE, "bibliography-index.md")))
    add("Skill 稳定性报告存在",
        os.path.exists(os.path.join(KB, "..", "outputs", "kg-engineering", "evals", "backtest-stability.md")))
    add("Web UI 与 CI 存在",
        os.path.exists(os.path.join(KB, "service", "web", "index.html"))
        and os.path.exists(os.path.join(KB, "..", ".github", "workflows", "ci.yml")))

    f_csv = list(csv.DictReader(open(os.path.join(BASE, "formula-audit.csv"),
                                    encoding="utf-8-sig")))
    add("公式 132 条全部核对",
        len(f_csv) == 132 and all(x["manual_status"] in ("通过", "已修正") for x in f_csv))
    n_csv = list(csv.DictReader(open(os.path.join(BASE, "number-audit.csv"),
                                    encoding="utf-8-sig")))
    add("实验数值 0 条待复核",
        all(x["status"] in ("通过", "人工确认") for x in n_csv),
        f"{len(n_csv)} 条")

    secs = list(csv.DictReader(open(os.path.join(BASE, "coverage-sections.csv"),
                                    encoding="utf-8-sig")))
    def covered(book, level):
        xs = [s for s in secs if s["book"] == book and s["level"] == str(level)]
        return sum(1 for s in xs if int(s["points"]) > 0), len(xs)
    add("覆盖 A 二级 50/50", covered("A", 2) == (50, 50), str(covered("A", 2)))
    add("覆盖 A 三级 158/158", covered("A", 3) == (158, 158), str(covered("A", 3)))
    add("覆盖 B 二级 41/41", covered("B", 2) == (41, 41), str(covered("B", 2)))
    add("覆盖 B 三级 82/82", covered("B", 3) == (82, 82), str(covered("B", 3)))

    # Obsidian links
    names = {os.path.splitext(os.path.basename(p))[0]
             for p in glob.glob(os.path.join(KB, "obsidian", "**", "*.md"), recursive=True)}
    broken = []
    for p in glob.glob(os.path.join(KB, "obsidian", "**", "*.md"), recursive=True):
        text = open(p, encoding="utf-8").read()
        for target in re.findall(r"\[\[([^\]]+)\]\]", text):
            t = target.split("|")[0].split("#")[0].strip()
            if t not in names:
                broken.append((p, t))
    add("Obsidian 0 断链", not broken, f"{len(broken)} 条")

    readme = open(os.path.join(KB, "README.md"), encoding="utf-8").read()
    add("README 计数同步", all(x in readme for x in
        ("770", "94", "442", "1361", "3140", "100 张表")))
    version = open(os.path.join(KB, "VERSION"), encoding="utf-8").read().strip()
    add("版本 3.0.0", version == "3.0.0", version)

    failed = [c for c in checks if not c[1]]
    lines = ["# 完工核查\n", f"- 检查项：{len(checks)}", f"- 通过：{len(checks) - len(failed)}",
             f"- 失败：{len(failed)}", "\n| 检查 | 结果 | 说明 |", "|---|---|---|"]
    for name, ok, detail in checks:
        lines.append(f"| {name} | {'PASS' if ok else 'FAIL'} | {detail} |")
    lines += ["\n## 已知限制\n",
              "- 图表索引的 342 张图没有逐图人工要点；100 张表已有表注。",
              "- `mentions_dataset` / `mentions_metric` 是词面匹配，20 条抽样中 7/20 为严格评估。",
              "- 图表 `illustrates` 只覆盖 44 条核心表，其余为小节级 `in_section`。",
              "- 100 张表都有记录，但只有 30 张有单元格级数据；行列表头为人工整理，数值回溯不等于行列语义全对。",
              "- 书 B 为 OCR，公式/表格仍可能有识别误差。"]
    open(os.path.join(BASE, "final-verification.md"), "w", encoding="utf-8").write("\n".join(lines))
    print(f"checks {len(checks)} pass {len(checks)-len(failed)} fail {len(failed)}")
    for name, ok, detail in failed:
        print("FAIL", name, detail)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
