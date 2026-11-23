---
id: "B-05-03-42"
canonical_id: "B-05-03-42"
book: "B"
chapter: 5
section: "5.3"
type: "方法"
coverage: "专项"
scope: "KG专项"
page: "p.163-164"
skill_module: "M10 / language §3.1"
tags:
  - KG
  - 书B
  - 第5章
  - 专项
  - 方法
  - KG专项
---

# 层次 Softmax 加速

> B-05-03-42 · 书B 第5章 语言知识的表示学习 · 5.3 义原的表示学习

> 本节图表：表5-1 不同模型在 Wordsim240 词、表5-2 不同模型在 SemEval 2007、表5-3 义项向量和义原向量的最近邻词示例、表5-4 义原向量之间最近邻示例、表5-5 低频词的最近邻词示例（[[40-图表索引]]）

## 定义

词表大时用层次 Softmax 降低预测词的计算复杂度。

## 关键要点

- Huffman 树
- O(log V)
- 替代全词表 softmax
- 训练更快

## 前置知识

- [[B-05-03-41 义原向量学习目标]]

## 关联知识

- [[B-05-03-43 义项敏感与不敏感对比]]

## 来源

- PDF p.163-164
- Skill 模块：M10 / language §3.1
