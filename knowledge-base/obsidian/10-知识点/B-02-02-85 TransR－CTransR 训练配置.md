---
id: "B-02-02-85"
canonical_id: "B-02-02-85"
book: "B"
chapter: 2
section: "2.3"
type: "方法"
coverage: "专项"
scope: "KG核心"
page: "p.40-41"
skill_module: "M5 / distilled §6.2"
tags:
  - KG
  - 书B
  - 第2章
  - 专项
  - 方法
  - KG核心
---

# TransR/CTransR 训练配置

> B-02-02-85 · 书B 第2章 世界知识的表示学习 · 2.3 基于翻译的知识表示学习

> 本节图表：表2-1 WN18 和 FB15K 上的评测结、图2-2 TransR 的简易示意图、表2-2 将关系分类后在 FB15K 上的评测、表2-3 〈头实体，尾实体〉对于“地区包含”的、图2-3 TransE、TransH 与 Tr、表2-4 三元组分类的评测结果（[[40-图表索引]]）

## 定义

TransR/CTransR 在 WN18/FB15K 上训练 500 轮，用验证集平均排名选参：WN18 取 λ=0.001、γ=4、k=d=50、B=1440、α=0.001；FB15K 取 λ=0.001、γ=1、k=d=50、B=4800、α=0.01。

## 关键要点

- 500 轮
- 验证集平均排名选参
- WN18 γ=4
- FB15K γ=1

## 前置知识

- [[B-02-02-09 平移模型 TransE]]

## 关联知识

- [[B-02-02-82 TransR－CTransR 实验结果]]
- [[B-02-02-86 TransR 的分关系类型结果]]

## 来源

- PDF p.40-41
- Skill 模块：M5 / distilled §6.2
