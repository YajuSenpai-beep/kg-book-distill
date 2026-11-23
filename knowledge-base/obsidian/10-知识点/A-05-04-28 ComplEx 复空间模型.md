---
id: "A-05-04-28"
canonical_id: "A-05-04-28"
book: "A"
chapter: 5
section: "5.4"
type: "模型"
coverage: "核心"
scope: "KG核心"
page: "p.151-152"
skill_module: "M5 / distilled §8.4"
tags:
  - KG
  - 书A
  - 第5章
  - 核心
  - 模型
  - KG核心
---

# ComplEx 复空间模型

> A-05-04-28 · 书A 第5章 知识图谱推理 · 5.4 基于表示学习的知识图谱推理

> 本节图表：表5-4 知识图谱嵌入与推理模型列表举例、表5-5 EL本体语言、图5-21 Rete算法举例、图5-22 TransE推理模型、图5-23 利用类比思想实现知识图谱推理、图5-24 处理一对多和多对多关系（[[40-图表索引]]）

## 定义

ComplEx 把实体/关系映射到复数空间，解决 DistMult 只能建模对称关系的问题。

## 关键要点

- 复数空间不满足交换律
- 可建模非对称关系
- 得分包含实部/虚部组合

## 公式/示例

```text
f(h,r,t)=Re(hᵀ diag(r) conj(t))
```

## 前置知识

- [[A-05-04-26 DistMult 与双线性模型]]

## 关联知识

- [[A-05-04-29 复杂关系建模：TransH－R－D]]

## 来源

- PDF p.151-152
- Skill 模块：M5 / distilled §8.4
