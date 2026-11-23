---
id: "A-08-03-62"
canonical_id: "A-08-03-62"
book: "A"
chapter: 8
section: "8.3"
type: "方法"
coverage: "核心"
scope: "KG邻接"
page: "p.261-263"
skill_module: "M9 / graph §4"
tags:
  - KG
  - 书A
  - 第8章
  - 核心
  - 方法
  - KG邻接
---

# Node2Vec 的 p/q

> A-08-03-62 · 书A 第8章 图算法与图数据分析 · 8.3 图表示学习与图神经网络

> 本节图表：图8-19 社区发现算法、图8-20 图表示学习的基本思想、图8-21 随机游走序列模型与图神经网络模型、图8-22 DeepWalk模型：最大化随机序列、图8-23 Node2Vec：深度优先搜索与广度、图8-24 LINE：一阶近似与二阶近似（[[40-图表索引]]）

## 定义

p 控制返回概率，q 控制 BFS/DFS 倾向；q>1 偏同质，q<1 偏结构。

## 关键要点

- p 返回
- q 进出
- BFS/DFS
- 需调参

## 前置知识

- [[A-08-03-25 Node2Vec]]

## 关联知识

- [[A-08-03-63 LINE 一阶－二阶]]

## 来源

- PDF p.261-263
- Skill 模块：M9 / graph §4
