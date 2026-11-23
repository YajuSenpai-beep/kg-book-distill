---
id: "B-02-02-51"
canonical_id: "B-02-02-51"
book: "B"
chapter: 2
section: "2.2"
type: "模型"
coverage: "核心"
scope: "KG核心"
page: "p.36-37"
skill_module: "M5 / distilled §6.1"
tags:
  - KG
  - 书B
  - 第2章
  - 核心
  - 模型
  - KG核心
---

# TransH 超平面投影

> B-02-02-51 · 书B 第2章 世界知识的表示学习 · 2.2 相关工作

> 本节图表：图2-1 平移模型图示（[[40-图表索引]]）

## 定义

TransH 把实体投影到关系超平面，在超平面上做平移，缓解一对多/多对多。

## 关键要点

- 关系超平面法向量 w_r
- h⊥=h−w_rᵀh w_r
- 超平面上 h⊥+r≈t⊥
- 比 TransE 表达力强

## 公式/示例

```text
h⊥=h−w_rᵀh w_r；E=‖h⊥+r−t⊥‖
```

## 前置知识

- [[B-02-02-11 TransE 的局限]]

## 关联知识

- [[B-02-03-13 TransR 关系特定空间]]

## 来源

- PDF p.36-37
- Skill 模块：M5 / distilled §6.1
