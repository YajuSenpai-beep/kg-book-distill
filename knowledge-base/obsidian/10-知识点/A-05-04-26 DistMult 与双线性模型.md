---
id: "A-05-04-26"
canonical_id: "A-02-04-23"
book: "A"
chapter: 5
section: "5.4"
type: "模型"
coverage: "核心"
scope: "KG核心"
page: "p.151"
skill_module: "M5 / distilled §8.4"
tags:
  - KG
  - 书A
  - 第5章
  - 核心
  - 模型
  - KG核心
---

# DistMult 与双线性模型

> A-05-04-26 · 书A 第5章 知识图谱推理 · 5.4 基于表示学习的知识图谱推理

> 规范条目：[[A-02-04-23 DistMult 双线性模型]]

> 本节图表：表5-4 知识图谱嵌入与推理模型列表举例、表5-5 EL本体语言、图5-21 Rete算法举例、图5-22 TransE推理模型、图5-23 利用类比思想实现知识图谱推理、图5-24 处理一对多和多对多关系（[[40-图表索引]]）

## 定义

DistMult 用双线性函数给三元组打分，关系用对角矩阵表示。

## 关键要点

- hᵀ diag(r) t
- 比 TransE 表达力强
- 对角矩阵限制为对称关系

## 公式/示例

```text
f(h,r,t)=hᵀ diag(r) t
```

## 前置知识

- [[A-05-04-24 TransE 推理]]

## 关联知识

- [[A-05-04-27 Analogy 类比推理模型]]

## 来源

- PDF p.151
- Skill 模块：M5 / distilled §8.4
