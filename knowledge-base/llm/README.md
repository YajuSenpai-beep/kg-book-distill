# 生成式答案层

把统一的检索上下文交给 LLM，生成**带 [ID] 引用**的答案；再用 15 条 gold QA 评估。

## 文件

| 文件 | 用途 |
|---|---|
| `client.py` | 多 provider 客户端（stdlib，无 SDK） |
| `generate_answers.py` | 检索 → 拼 prompt → 调模型 → 校验引用 |
| `eval_generated.py` | 关键词覆盖、引用精确/召回、引用有效性、拒答率、引用句支持度 |
| `citation_check.py` | 句内引用过滤、支持度、3 条上限 |
| `contexts.json` | 15 条 QA 的检索上下文 |
| `answers-gen-*.jsonl` | 各模型生成的答案 |
| `report-generated*.md` | 评估报告 |

## Provider

设置一个 API key 即可，`KG_LLM_PROVIDER` 可显式指定：

| Provider | 环境变量 | 默认模型 |
|---|---|---|
| Anthropic | `ANTHROPIC_API_KEY` | `claude-sonnet-5-5` |
| DeepSeek | `DEEPSEEK_API_KEY` | `deepseek-chat` |
| Qwen/DashScope | `DASHSCOPE_API_KEY` | `qwen-plus` |
| GLM | `ZHIPU_API_KEY` | `glm-4-flash` |
| Moonshot | `MOONSHOT_API_KEY` | `moonshot-v1-8k` |
| Ollama | 本地 `localhost:11434` | `qwen3:8b` |
| Mock | 无 | 无（全部拒答） |

可选：`KG_LLM_MODEL`、`KG_LLM_BASE_URL`。

## 运行

```bash
# 无 key 时跑通链路（全部拒答）
python -I llm/generate_answers.py --provider mock --limit 3

# 有 key 时
set DEEPSEEK_API_KEY=...
python -I llm/generate_answers.py --provider deepseek
python -I llm/eval_generated.py --answers llm/answers-generated.jsonl

# DeepSeek 实跑结果（15 条）
# 覆盖 0.717、引用精确 0.589、引用召回 0.522、支持度 0.636
python -I llm/eval_generated.py --answers llm/answers-gen-deepseek.jsonl

# 本地 Ollama
ollama pull qwen3:8b
python -I llm/generate_answers.py --provider ollama
```

## Prompt 约束

- 只能用给定资料；
- 每条结论带 [ID]；
- 资料不足时 `insufficient=true`；
- 输出 JSON，引用 ID 必须来自上下文，否则脚本会丢弃。

## 评测口径

- 关键词覆盖：答案中命中 gold 关键词的比例（正确性代理）。
- 引用精确率：引用中属于 gold 知识点的比例。
- 引用召回率：gold 知识点被引用的比例。
- 引用有效性：引用 ID 是否出现在检索上下文。
- 拒答率：`insufficient=true` 的比例。

## 重要限制

- 关键词覆盖不等于答案正确；需要人工抽检。
- 引用来自上下文，不代表引用支持该句；需要 NLI/人工核验。
- 生成式模型不能修复缺失数据、OCR 错误、错误 Schema。
- 只把检索片段发给外部 API，不要上传整本书。
