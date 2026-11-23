---
id: "A-05-04-59"
canonical_id: "A-05-04-59"
book: "A"
chapter: 5
section: "5.4"
type: "方法"
coverage: "专项"
scope: "KG核心"
page: "p.172-177"
skill_module: "M5 / distilled §8.4"
tags:
  - KG
  - 书A
  - 第5章
  - 专项
  - 方法
  - KG核心
---

# EL Embedding 损失

> A-05-04-59 · 书A 第5章 知识图谱推理 · 5.4 基于表示学习的知识图谱推理

> 本节图表：表5-4 知识图谱嵌入与推理模型列表举例、表5-5 EL本体语言、图5-21 Rete算法举例、图5-22 TransE推理模型、图5-23 利用类比思想实现知识图谱推理、图5-24 处理一对多和多对多关系（[[40-图表索引]]）

## 定义

把概念映射为球，用球包含近似概念包含，用 margin loss 约束合取/量词/不相交。

## 关键要点

- 球心+半径
- C⊑D 包含
- margin loss
- 近似语义

## 公式/示例

```text
f(c), r(c)；dist+margin
```

## 前置知识

- [[A-05-04-42 本体嵌入 EL Embedding]]

## 关联知识

- [[A-05-04-60 JOIE 双视图]]

## 来源

- PDF p.172-177
- Skill 模块：M5 / distilled §8.4
