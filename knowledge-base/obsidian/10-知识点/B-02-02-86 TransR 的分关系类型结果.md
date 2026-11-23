---
id: "B-02-02-86"
canonical_id: "B-02-02-86"
book: "B"
chapter: 2
section: "2.3"
type: "案例"
coverage: "专项"
scope: "KG核心"
page: "p.41-42"
skill_module: "M5 / distilled §6.2"
tags:
  - KG
  - 书B
  - 第2章
  - 专项
  - 案例
  - KG核心
---

# TransR 的分关系类型结果

> B-02-02-86 · 书B 第2章 世界知识的表示学习 · 2.3 基于翻译的知识表示学习

> 本节图表：表2-1 WN18 和 FB15K 上的评测结、图2-2 TransR 的简易示意图、表2-2 将关系分类后在 FB15K 上的评测、表2-3 〈头实体，尾实体〉对于“地区包含”的、图2-3 TransE、TransH 与 Tr、表2-4 三元组分类的评测结果（[[40-图表索引]]）

## 定义

FB15K 上按 1-1/1-N/N-1/N-N 切片，CTransR(bern) 的尾实体 Hits@10 分别为 80.8/38.6/90.1/73.8，均高于 TransE 的 43.7/19.7/66.7/50.0；多对一关系受益最大。

## 关键要点

- 1-1 80.8
- N-1 90.1
- 多对一提升最大
- 关系特定映射

## 前置知识

- [[B-02-02-85 TransR－CTransR 训练配置]]

## 关联知识

- [[B-02-02-82 TransR－CTransR 实验结果]]

## 来源

- PDF p.41-42
- Skill 模块：M5 / distilled §6.2
