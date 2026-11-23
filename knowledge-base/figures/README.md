# 图表索引

把两本书里的图与表从“正文里的图注”变成可检索、可挂节的索引。

## 产物

| 文件 | 用途 |
|---|---|
| `figure-index.json` | 结构化记录，脚本/图谱使用 |
| `figure-index.csv` | Excel 查看与筛选 |
| `figure-index.md` | 按书排列的 Markdown 索引 |
| `../obsidian/40-图表索引.md` | Obsidian 内的单页索引 |
| `build_figure_index.py` | 重建脚本 |

## 规模

| 项 | 数量 |
|---|---:|
| 总数 | 442 |
| 图 | 342 |
| 表 | 100 |
| 书 A | 296 |
| 书 B | 146 |
| 表注 | 100（全部表） |
| 精确图表关联 | 44 条 / 46 边 |

## 字段

| 字段 | 含义 |
|---|---|
| `id` | `FIG-A-1-1` / `TAB-B-2-1`，书内唯一 |
| `book` / `chapter` | 来源 |
| `kind` | 图 / 表 |
| `number` | 原书编号，如 `图1-1`、`表2-1` |
| `caption` | 图注/表注 |
| `page` | PDF 页码 |
| `section` / `section_title` | 所属小节（优先三级，回退二级） |
| `role` | 架构/流程图、示意图、示例图、实验结果表、数据统计表、数据表 |
| `context` | 图注前后各 2–3 行原文（OCR） |
| `linked_points` | 同小节的知识点 ID（最多 5 个） |
| `note` | 表注；100 张表全部有 |
| `note_status` | `curated` / `auto` |
| `illustrates` | 精确关联的知识点 ID（44 条核心表） |

## 口径与限制

- **图注是原文，不是摘要**；`note` 为空时看 `context`。
- 100 张表都有表注；44 条核心表有精确 `illustrates` 关联；342 张图仍只有图注与上下文，没有逐图编造要点。
- `linked_points` 是**小节级关联**，不是“这张图精确解释了哪条知识点”。
- 图表内容本身没有做视觉理解/OCR 结构化；表里的行列关系仍可能受 OCR 串行影响。
- 图表挂到所属**二级节**；若图注在三级小节，会向上找到存在的二级节。

## 重建

```bash
python -I figures/build_figure_index.py
python -I graph/build_graph.py
```
