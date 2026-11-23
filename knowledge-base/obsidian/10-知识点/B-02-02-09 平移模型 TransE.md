---
id: "B-02-02-09"
canonical_id: "B-02-02-09"
book: "B"
chapter: 2
section: "2.2"
type: "模型"
coverage: "核心"
scope: "KG核心"
page: "p.35-36"
skill_module: "M5 / distilled §6.1"
tags:
  - KG
  - 书B
  - 第2章
  - 核心
  - 模型
  - KG核心
---

# 平移模型 TransE

> B-02-02-09 · 书B 第2章 世界知识的表示学习 · 2.2 相关工作

> 本节图表：图2-1 平移模型图示（[[40-图表索引]]）

## 定义

TransE 把关系视为头到尾的平移向量，要求 h+r≈t；简单高效、可扩展。

## 关键要点

- h+r≈t
- L1/L2 距离评分
- 负采样 + 最大间隔
- 大规模图谱效果好

## 公式/示例

```text
E(h,r,t)=‖h+r−t‖
```

## 前置知识

- [[B-02-02-08 神经张量网络 NTN]]

## 关联知识

- [[B-02-02-10 TransE 的训练目标]]

## 来源

- PDF p.35-36
- Skill 模块：M5 / distilled §6.1
