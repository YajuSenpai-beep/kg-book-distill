# 可执行校验脚本

三个零依赖脚本，用于把 Skill 的“检查清单”落成命令。

## 1. Schema 校验

```bash
python validate_schema.py schema.json --strict
```

检查：类/关系唯一、父类存在且无环、domain/range 有效、身份规则非空、基数合法、CQ 路径与关系一致、孤立类警告。

示例：`examples/schema.example.json`

## 2. 抽取评估

```bash
python eval_extraction.py gold.jsonl pred.jsonl --report report.md
```

输入每行：

```json
{"doc_id": "d1", "triples": [["比尔·盖茨", "创始人", "微软"], ["微软", "总部", "雷德蒙德"]]}
```

输出：micro P/R/F1、按关系 P/R/F1、Macro-F1、缺失/多余文档。

示例：`examples/gold.example.jsonl` / `examples/pred.example.jsonl`

## 3. 链接预测评估

```bash
python eval_link_prediction.py ranks.jsonl --report report.md
```

输入每行：

```json
{"gold": "杭州", "ranked": ["上海", "杭州", "北京"], "filtered_ranked": ["杭州", "上海", "北京"], "relation": "locatedIn"}
```

输出：raw/filtered 的 MR、MRR、Hit@1/3/10，并按关系拆分。

示例：`examples/ranks.example.jsonl`

## 4. 决策规则存在性检查

```bash
python skill_rule_check.py ../evals/decision-cases.jsonl
```

检查 20 条场景对应的规则关键词是否仍在 references 中。注意：这只证明规则存在，不证明 Agent 会正确执行；真正回测见 `evals/README.md`。

## 建议接入流程

1. Schema 设计完 → 跑 `validate_schema.py`，不过不进入建库。
2. 抽取模型产出 → 跑 `eval_extraction.py`，按关系看长尾。
3. 链接预测/补全 → 跑 `eval_link_prediction.py`，必须同时报 raw/filtered。
