---
id: "A-02-04-23"
canonical_id: "A-02-04-23"
book: "A"
chapter: 2
section: "2.4"
type: "模型"
coverage: "核心"
scope: "KG核心"
page: "p.54"
skill_module: "M5 / distilled §6.1"
tags:
  - KG
  - 书A
  - 第2章
  - 核心
  - 模型
  - KG核心
---

# DistMult 双线性模型

> A-02-04-23 · 书A 第2章 知识图谱的表示 · 2.4 知识图谱的向量表示方法

> 本节图表：图2-8 OWL语言家族、图2-9 One-hot Encoding和词、图2-10 词的向量表示举例、图2-11 词向量的特性（1）、图2-12 词向量的特性（2）、图2-13 从词向量到实体和关系的向量（[[40-图表索引]]）

## 定义

DistMult 用乘法/双线性函数给三元组打分，关系用矩阵（常为对角）表示。

## 关键要点

- h 与关系矩阵相乘后接近 t
- 比 TransE 表达力更强
- 对角矩阵时只能建模对称关系

## 公式/示例

```text
E(h,r,t)=hᵀ diag(r) t
```

## 前置知识

- [[A-02-04-22 TransE 平移模型]]

## 关联知识

- [[A-05-04-26 DistMult 与双线性模型]]

## 来源

- PDF p.54
- Skill 模块：M5 / distilled §6.1
