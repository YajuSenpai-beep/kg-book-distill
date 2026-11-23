---
id: "A-03-01-02"
canonical_id: "A-03-01-02"
book: "A"
chapter: 3
section: "3.1"
type: "方法"
coverage: "核心"
scope: "KG核心"
page: "p.58"
skill_module: "M2 / distilled §4.4"
tags:
  - KG
  - 书A
  - 第3章
  - 核心
  - 方法
  - KG核心
---

# SPARQL 与子图匹配

> A-03-01-02 · 书A 第3章 知识图谱的存储与查询 · 3.1 基于关系数据库的知识图谱存储

> 本节图表：图3-1 图的查询语言、图3-2 基于三元组表的知识图谱存储、图3-3 基于属性表的知识图谱存储方法、图3-4 基于垂直划分表的知识图谱存储（[[40-图表索引]]）

## 定义

SPARQL 是面向 RDF 的语义查询语言，语法类似 SQL；带变量的查询可转化为子图匹配问题。

## 关键要点

- 查询可表示为带变量的图
- 计算本质是子图匹配
- 适合 RDF/语义查询

## 公式/示例

```text
SELECT ?name WHERE { ?m bornIn ?city . ?m hasName ?name }
```

## 前置知识

- [[A-03-01-01 图数据存储的三个问题]]

## 关联知识

- [[A-03-02-11 图查询语言]]

## 来源

- PDF p.58
- Skill 模块：M2 / distilled §4.4
