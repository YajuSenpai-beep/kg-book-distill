---
id: "A-05-04-52"
canonical_id: "A-05-04-52"
book: "A"
chapter: 5
section: "5.4"
type: "模型"
coverage: "核心"
scope: "KG核心"
page: "p.153"
skill_module: "M5 / distilled §8.4"
tags:
  - KG
  - 书A
  - 第5章
  - 核心
  - 模型
  - KG核心
---

# TransD 动态映射

> A-05-04-52 · 书A 第5章 知识图谱推理 · 5.4 基于表示学习的知识图谱推理

> 本节图表：表5-4 知识图谱嵌入与推理模型列表举例、表5-5 EL本体语言、图5-21 Rete算法举例、图5-22 TransE推理模型、图5-23 利用类比思想实现知识图谱推理、图5-24 处理一对多和多对多关系（[[40-图表索引]]）

## 定义

TransD 用头/尾各自的动态投影矩阵，把实体映射到关系空间。

## 关键要点

- 头尾不同投影
- 动态矩阵
- 参数效率
- 改进复杂关系

## 公式/示例

```text
h⊥=M_rh h, t⊥=M_rt t
```

## 前置知识

- [[A-05-04-51 TransH 超平面]]

## 关联知识

- [[A-05-04-53 TransG－KG2E－ManifoldE（推理视角）]]

## 来源

- PDF p.153
- Skill 模块：M5 / distilled §8.4
