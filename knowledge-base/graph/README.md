# 知识图谱导出

把 770 个知识点和 442 个图表从“带链接的笔记”升级为**带类型的属性图**，同时保留原始 `prerequisites` / `related` 语义。图表挂到所属二级节，不做逐图要点推理。

## 文件

| 文件 | 用途 |
|---|---|
| `kg-graph.json` | 通用节点/边 JSON，脚本可直接读 |
| `kg-graph.graphml` | Gephi / yEd / Cytoscape 导入 |
| `kg-graph.ttl` | RDF/Turtle，可导入 Jena、GraphDB、Neo4j n10s |
| `graph-report.md` | 规模、类型分布、高度节点、孤立点、前置环 |
| `build_graph.py` | 重建脚本 |
| `query-examples.md` | Python / SPARQL / Cypher 查询示例 |
| `edge-audit.md` | 20 条数据集边抽样：20/20 提到数据集，7/20 是严格评估 |

## 节点类型

| 类型 | 数量 | 说明 |
|---|---:|---|
| Book | 2 | 两本书 |
| Chapter | 17 | 章 |
| Section | 94 | 二级节 |
| KnowledgePoint | 770 | 知识点 |
| Figure | 342 | 图（来自 `figures/figure-index.json`） |
| Table | 100 | 表（30 张有单元格级数据，70 张索引记录） |
| Dataset | 29 | 数据集（如 FB15K、NYT、HowNet） |
| Metric | 12 | 指标（MR、MRR、Hit@10、MAP、F1 等） |

## 关系类型

| 关系 | 数量 | 方向 | 来源 |
|---|---:|---|---|
| `part_of` | 112 | 章→书、节→章、三级节→二级节 | 结构生成 |
| `in_section` | 1212 | 知识点/图表→节 | 结构生成 |
| `prerequisite_of` | 788 | 前置点→后继点 | `prerequisites` 字段 |
| `related_to` | 794 | 双向语义关联 | `related` 字段 |
| `variant_of` | 14 | 变体→基础模型 | 人工整理的模型族 |
| `improves` | 9 | 改进模型→被改进模型 | 人工整理的关键对比 |
| `illustrates` | 46 | 图表→知识点 | 人工映射（44 条核心图表） |
| `evaluated_on` | 33 | 知识点→数据集 | 词面匹配 + 评估语境 |
| `mentions_dataset` | 60 | 知识点→数据集 | 只提到，未判断为评估 |
| `reports_metric` | 48 | 知识点→指标 | 词面匹配 + 结果语境 |
| `mentions_metric` | 7 | 知识点→指标 | 只提到 |
| `canonical_of` | 17 | 重复点→规范点 | `canonical-map.json` |

## 重要限制

- `evaluated_on` / `reports_metric` 是“词面匹配 + 语境线索”的弱标注，不是人工逐条确认；`mentions_*` 更弱，只表示文本提到。
- `variant_of` / `improves` 是人工整理的少量核心边，不覆盖全部模型谱系。
- 所有点都是 `KnowledgePoint`，没有把“实体/关系/属性”从书中抽成独立实例；这是“知识点图谱”，不是领域实例图谱。
- `graph-report.md` 会报告前置环；当前为 0，但不代表语义上所有前置都合理。
- 导入 Neo4j 时注意 `type` 是保留字，建议用 `nodeType` 字段。

## 重建

```bash
python -I graph/build_graph.py
```
