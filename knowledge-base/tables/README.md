# 结构化表格

把 100 张表全部落成结构化记录：37 张完整矩阵、5 张键值配置表、58 张索引记录。

## 产物

| 文件 | 用途 |
|---|---|
| `table-data.json` | 100 张表的结构化记录 |
| `tables.md` | 人读的 Markdown 表格 |
| `table-index.csv` | 表清单与行列数 |
| `table-validation.md` | 结构校验 + 源码数字回溯 |
| `build_tables.py` | 重建/校验脚本 |

## 状态分布

| 状态 | 数量 | 含义 |
|---|---:|---|
| `matrix` | 37 | 完整行列矩阵 |
| `key_value` | 5 | 参数/取值配置表 |
| `index_only` | 58 | 图注+页码+表注+源行的索引记录，没有单元格级结构 |

37 张矩阵包括：

| 表 | 内容 |
|---|---|
| `TAB-B-2-1` | TransR/CTransR 在 WN18/FB15K 的链接预测 |
| `TAB-B-2-2` | FB15K 分关系类型的头/尾实体 Hits@10 |
| `TAB-B-2-5` | PTransE 实体预测 |
| `TAB-B-2-9` | KR-EAR 实体预测（头/尾/合计） |
| `TAB-B-2-10` | KR-EAR 关系预测 |
| `TAB-B-2-11` | KR-EAR 属性预测 |
| `TAB-B-2-13` | DKRL 实体预测 |
| `TAB-B-2-14` | DKRL 关系预测 |
| `TAB-B-2-16` | DKRL 实体类型分类 MAP |
| `TAB-B-2-17` | DKRL 零样本实体预测 |
| `TAB-B-2-18` | DKRL 零样本关系预测 |
| `TAB-B-2-19` | DKRL 零样本类型分类 |
| `TAB-B-2-20` | TKRL 实体预测 |
| `TAB-B-2-21` | TKRL 关系预测 |
| `TAB-B-2-22` | TKRL 测试时类型限制 |
| `TAB-B-3-5` | HATT 不同召回率精度 |
| `TAB-B-4-7` | IPTransE 实体对齐 |
| `TAB-B-5-2` | SemEval 2007 词义消歧 |
| `TAB-B-6-1` | 义原预测 MAP |
| `TAB-B-6-3` | 不同词性的义原预测 |
| `TAB-B-6-5` | 内外信息融合的义原预测 |
| `TAB-B-7-1` | LIWC 词典统计 |
| `TAB-B-7-5` | SDLM 语言模型困惑度 |
| `TAB-B-7-6` | SDLM 单义/多义困惑度 |
| `TAB-B-7-8` | LCSTS 标题生成 ROUGE |
| `TAB-B-3-2` | 选择性注意力 P@N（One/Two/All） |
| `TAB-B-4-8` | 对齐辅助的图谱补全 |
| `TAB-B-5-1` | Wordsim240 词相似度 |
| `TAB-B-5-6` | Wordsim240/297 词相似度对比 |
| `TAB-B-7-2` | HDSA 每层 Micro-F1/W-M-F1 |
| `TAB-B-7-3` | HDSA 每层精度/召回 |
| `TAB-B-7-7` | SDLM 不同义原数量的困惑度 |
| `TAB-B-3-10` | 中英文不平衡关系的预测准确率 |
| `TAB-B-3-16` | KATT 联合学习 P@N |
| `TAB-B-4-4` | 人物/组织/地点粗粒度类型效果 |
| `TAB-B-5-7` | 词类比推理 |
| `TAB-B-6-6` | CSP 在不同词频段的效果 |

5 张键值表：`TAB-B-3-1`、`TAB-B-3-4`、`TAB-B-3-8`、`TAB-B-3-11`、`TAB-B-4-2`（各模型超参数）。

## Schema

```json
{
  "id": "TAB-B-2-1",
  "caption": "...",
  "book": "B",
  "page": 40,
  "columns": ["model", "wn18_mr_raw", "..."],
  "numeric_columns": [2, 3],
  "rows": [["TransE", "-", 263, 251]],
  "note": "..."
}
```

## 校验

```bash
python -I tables/build_tables.py
```

校验内容：

- ID 必须存在于 `figures/figure-index.json`，且类型为表；
- 页码一致；
- 列名不重复；
- 每行列数与列名一致；
- `numeric_columns` 中的单元格可转 float；
- 每个数值能在引用页 OCR 文本中做去空格/去逗号匹配。

当前结果：**100 张表，0 结构错误，0 源码数字未匹配**。

## 限制

- 100 张表都有记录，但只有 37 张矩阵 + 5 张键值表有单元格级数据；58 张是索引记录。
- 数值回溯只能证明“数字在引用页出现过”，不能证明行列对应关系完全正确；行列结构来自人工整理。
- 58 张索引记录不能直接用于统计计算，只能定位与阅读。
- 书 B 为 OCR，个别表头/单位可能识别偏差；以原书为准。
- 没有把表格接入推理；目前是数据层，供检索/校验/二次分析使用。
