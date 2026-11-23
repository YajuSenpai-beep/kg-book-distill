---
id: "B-02-02-52"
canonical_id: "B-02-02-52"
book: "B"
chapter: 2
section: "2.2"
type: "模型"
coverage: "核心"
scope: "KG核心"
page: "p.37"
skill_module: "M5 / distilled §6.1"
tags:
  - KG
  - 书B
  - 第2章
  - 核心
  - 模型
  - KG核心
---

# TransD 动态投影

> B-02-02-52 · 书B 第2章 世界知识的表示学习 · 2.2 相关工作

> 本节图表：图2-1 平移模型图示（[[40-图表索引]]）

## 定义

TransD 用头/尾实体各自的动态映射矩阵，将实体投影到关系空间。

## 关键要点

- 头尾不同投影
- 动态矩阵由实体/关系向量生成
- 参数效率较高
- 仍受平移假设限制

## 公式/示例

```text
h⊥=M_rh h, t⊥=M_rt t
```

## 前置知识

- [[B-02-02-51 TransH 超平面投影]]

## 关联知识

- [[B-02-03-14 CTransR 关系内聚类]]

## 来源

- PDF p.37
- Skill 模块：M5 / distilled §6.1
