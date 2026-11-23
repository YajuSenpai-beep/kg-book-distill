---
id: "A-08-03-66"
canonical_id: "A-08-03-66"
book: "A"
chapter: 8
section: "8.3"
type: "方法"
coverage: "核心"
scope: "KG邻接"
page: "p.268-269"
skill_module: "M9 / graph §5.2"
tags:
  - KG
  - 书A
  - 第8章
  - 核心
  - 方法
  - KG邻接
---

# GraphSAGE 聚合器

> A-08-03-66 · 书A 第8章 图算法与图数据分析 · 8.3 图表示学习与图神经网络

> 本节图表：图8-19 社区发现算法、图8-20 图表示学习的基本思想、图8-21 随机游走序列模型与图神经网络模型、图8-22 DeepWalk模型：最大化随机序列、图8-23 Node2Vec：深度优先搜索与广度、图8-24 LINE：一阶近似与二阶近似（[[40-图表索引]]）

## 定义

GraphSAGE 采样邻居后用 Mean/Pool/LSTM 聚合，再与自身拼接。

## 关键要点

- 邻居采样
- Mean/Pool/LSTM
- 拼接自身
- 归纳学习

## 公式/示例

```text
h_v^k=σ(W·[h_v^{k−1}‖AGG({h_u})])
```

## 前置知识

- [[A-08-03-34 GraphSAGE]]

## 关联知识

- [[A-08-03-67 VGAE 目标]]

## 来源

- PDF p.268-269
- Skill 模块：M9 / graph §5.2
