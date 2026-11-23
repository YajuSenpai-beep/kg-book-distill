# 实例层图谱

把“方法 / 任务 / 数据集 / 指标”抽成实体，形成可查询的元知识图谱。

## 规模

| 类型 | 数量 |
|---|---:|
| Method | 64 |
| Task | 18 |
| Dataset | 26 |
| Metric | 10 |
| 节点合计 | 118 |
| 边合计 | 176 |

关系：

| 关系 | 数量 | 含义 |
|---|---:|---|
| `solves` | 79 | 方法解决什么任务 |
| `reports_metric` | 27 | 方法报告什么指标 |
| `evaluated_on` | 23 | 方法在哪些数据集上评估 |
| `uses` | 18 | 方法依赖/组合 |
| `variant_of` | 14 | 变体→基础模型 |
| `improves` | 8 | 改进关系 |
| `mentions_dataset` | 4 | 只提到数据集（弱） |
| `mentions_metric` | 3 | 只提到指标（弱） |

## 文件

| 文件 | 用途 |
|---|---|
| `methods.json` | 方法/任务/依赖的策展清单 |
| `build_instances.py` | 从知识点图谱构建实例层 |
| `instance-graph.json` | JSON |
| `instance-graph.graphml` | Gephi/yEd |
| `instance-graph.ttl` | RDF/Turtle |
| `instance-report.md` | 规模、未解析方法、关系统计 |

## 口径

- 方法实体来自书名/模型名 + `methods.json` 策展，不是自动实体识别。
- `evaluated_on` / `reports_metric` 来自知识点文本的词面匹配，可能把“提到数据集”误当“在该数据集评估”。
- 64 个方法是核心模型，不是全书所有方法；`methods.json` 可继续扩。
- 这是**元知识图谱**（方法/任务/数据/指标），不是领域实例图谱（没有病人、药品、公司等实例）。

## 重建

```bash
python -I instances/build_instances.py
python -I service/graph_service.py --port 8765
```
