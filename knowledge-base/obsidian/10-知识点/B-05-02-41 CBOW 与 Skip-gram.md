---
id: "B-05-02-41"
canonical_id: "B-05-02-41"
book: "B"
chapter: 5
section: "5.2"
type: "模型"
coverage: "背景"
scope: "KG专项"
page: "p.162"
skill_module: "M10 / language §3"
tags:
  - KG
  - 书B
  - 第5章
  - 背景
  - 模型
  - KG专项
---

# CBOW 与 Skip-gram

> B-05-02-41 · 书B 第5章 语言知识的表示学习 · 5.2 相关工作

> 本节图表：图5-1 义项不敏感的义原向量表示学习神经网络、图5-2 义项敏感的义原向量表示学习神经网络模（[[40-图表索引]]）

## 定义

CBOW 用上下文预测中心词；Skip-gram 用中心词预测上下文；两者都学习静态词向量。

## 关键要点

- CBOW：上下文 → 中心词
- Skip-gram：中心词 → 上下文
- 负采样/层次 Softmax
- 静态向量

## 前置知识

- [[B-05-02-03 词表示学习]]

## 关联知识

- [[B-05-02-42 词义消歧的评估]]

## 来源

- PDF p.162
- Skill 模块：M10 / language §3
