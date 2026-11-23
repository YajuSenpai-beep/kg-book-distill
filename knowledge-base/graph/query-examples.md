# 查询示例

## Python（JSON）

```python
import json
g = json.load(open("kg-graph.json", encoding="utf-8"))
nodes = {n["id"]: n for n in g["nodes"]}

# 1. 某知识点的直接前置
pre = [e["source"] for e in g["edges"]
       if e["type"] == "prerequisite_of" and e["target"] == "B-02-03-13"]
print([nodes[x]["label"] for x in pre])

# 2. 某模型族的所有变体
var = [e["source"] for e in g["edges"]
       if e["type"] == "variant_of" and e["target"] == "A-05-04-24"]
print([nodes[x]["label"] for x in var])

# 3. 用到 FB15K 的知识点
ds = [e["source"] for e in g["edges"]
      if e["type"] == "mentions_dataset" and e["target"] == "DS-FB15K"]
print(len(ds), [nodes[x]["label"] for x in ds[:10]])
```

## SPARQL（Turtle 导入后）

```sparql
PREFIX kg: <http://example.org/kg/>
PREFIX ex: <http://example.org/kg/node/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

# TransR 的前置链（一跳）
SELECT ?pre ?label WHERE {
  ?pre kg:prerequisiteOf ex:B-02-03-13 ;
       rdfs:label ?label .
}

# 提到 FB15K 的模型类知识点
SELECT ?p ?label WHERE {
  ?p kg:mentionsDataset ex:DS-FB15K ;
     rdfs:label ?label .
  FILTER(CONTAINS(STR(?p), "B-02"))
}

# 所有模型变体边
SELECT ?variant ?base WHERE {
  ?variant kg:variantOf ?base .
}
```

## Cypher（Neo4j）

```cypher
// 节点标签：KnowledgePoint / Dataset / Metric / Section / Chapter / Book
// 关系类型：PREREQUISITE_OF / VARIANT_OF / IMPROVES / MENTIONS_DATASET / ...

MATCH (p:KnowledgePoint {id: "B-02-03-13"})<-[:PREREQUISITE_OF]-(pre)
RETURN pre.id, pre.label;

MATCH (p:KnowledgePoint)-[:MENTIONS_DATASET]->(d:Dataset {id: "DS-FB15K"})
RETURN p.id, p.label LIMIT 20;

MATCH path = (v:KnowledgePoint)-[:VARIANT_OF*1..3]->(base:KnowledgePoint)
WHERE base.id = "A-05-04-24"
RETURN path;

// 某节下的图表
MATCH (f)-[:IN_SECTION]->(s:Section {id: "SEC-B-02-03"})
WHERE f:Figure OR f:Table
RETURN f.id, f.label, f.page;
```

## Gephi

1. 导入 `kg-graph.graphml`。
2. 布局用 ForceAtlas2，按 `type` 着色。
3. 可按 `KnowledgePoint` 过滤，只保留知识点子图。

## Obsidian

Canvas 只画书→章；如果要在 Obsidian 里看类型化关系，建议用 Dataview 读取 `kg-graph.json`，或把 GraphML 导入 Gephi 截图。
