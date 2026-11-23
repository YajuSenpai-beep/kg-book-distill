---
id: "B-07-02-46"
canonical_id: "B-07-02-46"
book: "B"
chapter: 7
section: "7.2"
type: "方法"
coverage: "核心"
scope: "KG专项"
page: "p.215"
skill_module: "M10 / language §5.1"
tags:
  - KG
  - 书B
  - 第7章
  - 核心
  - 方法
  - KG专项
---

# beam search 与阈值

> B-07-02-46 · 书B 第7章 语言知识的计算应用 · 7.2 义原驱动的词典扩展

> 本节图表：图7-1 例词顶点和它在 LIWC 中的标签、表7-1 LIWC 词典统计结果、图7-2 例词顶点在知网中的义原标注、表7-2 Micro-F1 和 W-M-F1 、图7-3 HDSA 的结构、表7-3 W-M在每一层的平均精度和召回率（[[40-图表索引]]）

## 定义

预测时用 beam search 搜索标签路径，并用阈值 δ 过滤低置信路径。

## 关键要点

- beam search
- 路径概率
- 阈值 δ
- 多标签输出

## 公式/示例

```text
log P(y)>δ
```

## 前置知识

- [[B-07-02-43 层次解码器 LSTM]]

## 关联知识

- [[B-07-02-47 加权 Micro-F1]]

## 来源

- PDF p.215
- Skill 模块：M10 / language §5.1
