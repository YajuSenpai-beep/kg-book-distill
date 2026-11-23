---
id: "B-02-02-10"
canonical_id: "B-02-02-10"
book: "B"
chapter: 2
section: "2.2"
type: "方法"
coverage: "核心"
scope: "KG核心"
page: "p.36"
skill_module: "M5 / distilled §6.4"
tags:
  - KG
  - 书B
  - 第2章
  - 核心
  - 方法
  - KG核心
---

# TransE 的训练目标

> B-02-02-10 · 书B 第2章 世界知识的表示学习 · 2.2 相关工作

> 本节图表：图2-1 平移模型图示（[[40-图表索引]]）

## 定义

用最大间隔损失拉大正负三元组得分差，负样本通过随机替换头/尾实体生成。

## 关键要点

- 正例：图谱三元组
- 负例：替换头/尾
- margin γ
- SGD 优化

## 公式/示例

```text
L=Σ max(γ+E(h,r,t)−E(h′,r,t′),0)
```

## 前置知识

- [[B-02-02-09 平移模型 TransE]]

## 关联知识

- [[B-02-02-11 TransE 的局限]]

## 来源

- PDF p.36
- Skill 模块：M5 / distilled §6.4
