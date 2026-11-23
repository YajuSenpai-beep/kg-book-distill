# 引用句级 NLI 核验

日期：2026-11-22
输入：`answers-gen-deepseek.jsonl`（15 条，DeepSeek）
Judge：DeepSeek `deepseek-chat`，逐句判断 cited context 是否支持句子

## 结果

| 标签 | 数量 |
|---|---:|
| supported | 30 |
| partial | 3 |
| unsupported | 1 |
| 合计 | 34 |

严格模式（只保留 supported）后：

| 指标 | 修前 | 修后 |
|---|---:|---:|
| 引用数 | 34 | 30 |
| 引用精确率（gold） | 0.589 | 0.556 |
| 引用召回率（gold） | 0.522 | 0.500 |
| 引用有效率 | 1.000 | 1.000 |
| 引用句支持度（词面） | 0.636 | 未重算 |
| NLI 支持率 | 88.2% | 100% |

## 解读

- NLI 过滤掉了 1 条明确不支持、保留了 3 条 partial 之外的 supported。
- **gold 引用精确率反而略降**：因为 NLI 判断“句子被资料支持”与“资料属于 gold 点”不是同一个标准；有些引用语义支持，但不是标注的 gold。
- 说明：**引用精确率（对 gold）不能单独衡量引用质量**；需要同时报 NLI 支持率。

## 命令

```bash
set DEEPSEEK_API_KEY=...
python -I llm/nli_check.py --answers llm/answers-gen-deepseek.jsonl \
  --out llm/answers-nli.jsonl
python -I llm/eval_generated.py --answers llm/answers-nli.jsonl
```

缓存：`llm/nli_cache.json`（公开包已排除）。

## 限制

- Judge 与生成模型同源（都是 DeepSeek），存在同源偏差。
- 只做句级二/三分类，没有做完整 NLI 数据集校准。
- 样本只有 15 条，不能给置信区间。
