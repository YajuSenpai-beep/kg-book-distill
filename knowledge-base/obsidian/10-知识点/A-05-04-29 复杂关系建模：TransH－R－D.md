---
id: "A-05-04-29"
canonical_id: "A-05-04-29"
book: "A"
chapter: 5
section: "5.4"
type: "模型"
coverage: "核心"
scope: "KG核心"
page: "p.152-153"
skill_module: "M5 / distilled §8.4"
tags:
  - KG
  - 书A
  - 第5章
  - 核心
  - 模型
  - KG核心
---

# 复杂关系建模：TransH/R/D

> A-05-04-29 · 书A 第5章 知识图谱推理 · 5.4 基于表示学习的知识图谱推理

> 本节图表：表5-4 知识图谱嵌入与推理模型列表举例、表5-5 EL本体语言、图5-21 Rete算法举例、图5-22 TransE推理模型、图5-23 利用类比思想实现知识图谱推理、图5-24 处理一对多和多对多关系（[[40-图表索引]]）

## 定义

TransH 把实体投影到关系超平面；TransR 为每个关系建独立空间；TransD 用动态映射矩阵。

## 关键要点

- TransH：关系超平面投影
- TransR：关系特定矩阵 M_r
- TransD：头尾各自的动态投影
- 参数增多、训练成本上升

## 公式/示例

```text
TransR：h_r=M_r h, t_r=M_r t, E=‖h_r+r−t_r‖
```

## 前置知识

- [[A-05-04-24 TransE 推理]]

## 关联知识

- [[B-02-03-13 TransR 关系特定空间]]
- [[A-05-04-30 RotatE 旋转模型]]

## 来源

- PDF p.152-153
- Skill 模块：M5 / distilled §8.4
