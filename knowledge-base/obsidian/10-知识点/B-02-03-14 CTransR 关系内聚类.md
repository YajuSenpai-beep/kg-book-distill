---
id: "B-02-03-14"
canonical_id: "B-02-03-14"
book: "B"
chapter: 2
section: "2.3"
type: "模型"
coverage: "核心"
scope: "KG核心"
page: "p.39"
skill_module: "M5 / distilled §6.2"
tags:
  - KG
  - 书B
  - 第2章
  - 核心
  - 模型
  - KG核心
---

# CTransR 关系内聚类

> B-02-03-14 · 书B 第2章 世界知识的表示学习 · 2.3 基于复杂关系建模的知识表示学习

> 本节图表：表2-1 WN18 和 FB15K 上的评测结、图2-2 TransR 的简易示意图、表2-2 将关系分类后在 FB15K 上的评测、表2-3 〈头实体，尾实体〉对于“地区包含”的、图2-3 TransE、TransH 与 Tr、表2-4 三元组分类的评测结果（[[40-图表索引]]）

## 定义

CTransR 对同一关系的实体对按 h−t 聚类，为每簇学习单独关系向量，并约束其接近全局关系。

## 关键要点

- 关系内部语义多样
- 按 h−t 聚类
- 每簇 r_c
- 正则项 α‖r_c−r‖

## 公式/示例

```text
f_r=‖h_{r,c}+r_c−t_{r,c}‖+α‖r_c−r‖
```

## 前置知识

- [[B-02-03-13 TransR 关系特定空间]]

## 关联知识

- [[B-02-03-15 链接预测评测]]

## 来源

- PDF p.39
- Skill 模块：M5 / distilled §6.2
