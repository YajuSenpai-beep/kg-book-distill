# 图谱边质量审计（P3）

日期：2026-11-22
范围：`evaluated_on` 33、`mentions_dataset` 60、`variant_of` 14、`improves` 9

## 方法

- 固定随机种子 42 抽样：`evaluated_on` 20 条、`mentions_dataset` 10 条；`variant_of`、`improves` 全量。
- 逐条看“知识点标题/定义 + 目标节点”，判断边是否成立。
- 只审计数据集边与模型族边，不审计 `related_to`（它是原书 `related` 字段，语义本来就宽）。

## 结果

| 关系 | 抽样 | 成立 | 估计精确率 | 说明 |
|---|---:|---:|---:|---|
| `evaluated_on` | 20 | 20 | **100%** | 都是“在该数据集上训练/评测/报告结果” |
| `mentions_dataset` | 10 | 10 | **100%** | 都确实提到数据集，但不承诺评估 |
| `variant_of` | 14 | 14 | **100%** | TransH/TransR/CTransR/PTransE/TransD、PCNN、SPSE/SPASE、CSP、HDSA、GAT/GraphSAGE、CompGCN |
| `improves` | 9 | 9 | **100%** | 方向均为“改进模型→被改进模型” |

## 例子

`evaluated_on`：

- `B-02-02-86` → FB15K：TransR 分关系类型实验。
- `B-02-04-54` → FB15K：PTransE 实体预测。
- `B-06-03-82` → HowNet：义原预测 MAP。
- `B-07-03-82` → LCSTS/人民日报：SDLM 困惑度与标题生成。

`mentions_dataset`：

- `A-07-01-03` → SQuAD：开放域问答历史里提到 SQuAD。
- `A-01-02-06` → Wikidata：Freebase/Wikidata 对比。
- `B-03-02-44` → NYT：NYT 远程监督数据集介绍。

`variant_of`：

- `B-02-03-13`（TransR）→ `B-02-02-09`（TransE）。
- `B-06-04-13`（CSP）→ `B-06-04-12`（SPCSE）。
- `B-07-02-04`（HDSA）→ `B-07-02-03`（HD）。

`improves`：

- `B-02-03-14`（CTransR）→ `B-02-03-13`（TransR）。
- `B-06-04-13`（CSP）→ `B-06-03-05`（SPWE）。

## 结论

- 数据集边的两种语义已经分开：严格评估 33 条，弱提及 60 条；抽样未发现误标。
- 模型族边 23 条全量复核，未发现方向错误。
- 这不代表全量 93 条数据集边都正确；它是 30 条抽样 + 23 条全量模型边的结果。

## 限制

- 抽样由主会话完成，不是独立标注者。
- `evaluated_on` 的“评估”判断仍依赖语境线索，边界例子（如“用该数据集构建”）可能有争议。
- 没有审计 `mentions_metric` 和 `related_to`。
