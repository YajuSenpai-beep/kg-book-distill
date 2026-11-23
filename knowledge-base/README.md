# 知识图谱两书知识点库

把《知识图谱导论》（陈华钧）与《知识图谱与深度学习》（刘知远等）拆成可检索、可追溯、可映射到 Skill 的知识点。

## 产物

| 文件 | 用途 |
|---|---|
| `knowledge-map.md` | 按“书→章→节→知识点”阅读的 Markdown 地图 |
| `kg-knowledge-points.csv` | Excel/表格查看与筛选（UTF-8 with BOM） |
| `kg-knowledge-points.json` | 脚本/知识库/向量化使用 |
| `coverage-matrix.md` | 知识点 → Skill 模块的覆盖矩阵 |
| `validation-report.md` | 总量、类型、覆盖层级、引用完整性 |
| `spot-check.md` | 32 条随机抽检与 8 个核心公式核对 |
| `data/*.json` | 按章维护的源数据（基础 17 个 + 细节补充文件） |
| `build_kb.py` | 校验并生成上述产物 |
| `obsidian/` | Obsidian Vault：770 条知识点笔记 + 索引 + 总览 Canvas，双链已连通 |
| `obsidian/30-批注/` | 人工批注层：不会被重建覆盖，含 10 条示例与模板 |
| `anki/kg-cards.csv` | Anki 定义卡：770 张 |
| `anki/kg-application-cards.csv` | Anki 应用判断卡：120 张 |
| `search/kg_search.py` | 本地 BM25 检索，支持 `--book/--module/--scope` |
| `search/kg_lsa_search.py` | TF-IDF + SVD 的向量空间检索（scikit-learn） |
| `search/kg_hybrid_search.py` | BM25 + LSA 分数融合 |
| `search/kg_vector_search.py` | BGE 中文神经向量检索（fastembed） |
| `search/kg_hybrid_vector.py` | BM25 + BGE 向量混合检索 |
| `search/kg_rag.py` | 生成带 [ID] 引用的 RAG 上下文块（不调用 LLM） |
| `search/unified_search.py` | 知识点/图表/表格/术语/实例统一检索（BM25 + BGE + reranker） |
| `search/exhibit_search.py` | 图表/表格专用 BM25 |
| `search/image_search.py` | CLIP 图像检索（373 个图表页） |
| `eval/` | 100 条检索集 + 30 条 QA 集 + 基线评测报告 |
| `audit/` | 公式/数值/覆盖审计 + 公开发布脱敏检查 |
| `figures/` | 图表索引 442 条 + 373 个页面图 + CLIP 多模态索引 |
| `tables/` | 100 张表的结构化记录：37 矩阵 / 5 键值 / 58 索引（JSON + Markdown + 校验） |
| `graph/` | 类型化知识图谱导出：1361 节点 / 3140 边 / 12 种关系，JSON + GraphML + TTL |
| `instances/` | 实例层：64 方法 / 18 任务 / 26 数据集 / 10 指标，118 节点 176 边 |
| `service/` | 零依赖图谱 API + Web UI + Docker；统一搜索/邻居/路径/healthz/token |
| `glossary/` | 40 条中英术语表，37 条已解析到知识点 |
| `tools/` | 学习路径生成器（known/max-steps/minutes/Markdown） |
| `llm/` | 生成式答案层：Anthropic/DeepSeek/Qwen/GLM/Moonshot/Ollama/Mock |
| `tests/` | 数据/图谱/图表/表格/服务测试 |
| `build_exports.py` | 生成 Obsidian / Anki / Canvas / 检索脚本 |
| `VERSION` / `CHANGELOG.md` / `NOTICE.md` | 版本、变更、来源边界 |

## 规模

| 指标 | 数值 |
|---|---:|
| 知识点总数 | **770** |
| 书 A（导论） | 419 |
| 书 B（深度学习） | 351 |
| 章 | 17 |
| 节 | 94 |
| 含公式/示例 | 204 |
| 含前置知识 | 765 |
| 重复标题 | 0 |
| 悬空引用 | 0 |
| 正文规模 | 约 6.6 万字，约为两书原文的 14.8% |
| 图表索引 | 442 条（342 图 / 100 表） |
| 表格记录 | 100 张（37 矩阵 / 5 键值 / 58 索引） |
| 图谱导出 | 1361 节点（770 知识点 + 442 图表 + 154 结构/数据/指标）、3140 边 |

类型分布：方法 313、模型 111、概念 107、原则 98、案例 43、系统 39、对比 37、算法 22。

覆盖层级：核心 560（72.7%）、专项 150（19.5%）、背景 60（7.8%）。

范围：KG核心 449、KG专项 196、KG邻接 61、背景 64。

规范条目：17 条近重复/跨书重复条目通过 `canonical_id` 指向规范条目。

> v2 在 v1（447 点）基础上补了书 B 第 2/3/4/5/6/7 章的模型结构、训练目标、数据集与评估，书 A 9.5/9.6 的 PKGM/联邦细节，以及合并点的拆分。v2.1 增加去重、范围标签、评测、公式抽检与测试。v2.2 补实验/评估细节与批注层；v2.3 再补 42 条带具体数据集/指标/数值的实验点。

## 字段说明

| 字段 | 含义 |
|---|---|
| `id` | 稳定 ID，格式 `书-章-节-序号`，如 `A-05-04-24` |
| `canonical_id` | 规范条目 ID；自身为规范条目时等于 `id` |
| `book` / `chapter` / `section` | 来源位置 |
| `title` | 知识点名称 |
| `type` | 概念/方法/模型/算法/系统/公式/案例/对比/原则 |
| `definition` | 1–2 句转述定义 |
| `key_points` | 2–4 条关键要点，分号分隔 |
| `formula` | 公式或简短示例（可空） |
| `prerequisites` | 前置知识点 ID，分号分隔 |
| `related` | 关联知识点 ID，分号分隔 |
| `page` | PDF 页码或页码范围 |
| `skill_module` | 对应 `kg-engineering` Skill 的模块/小节 |
| `coverage` | 核心/专项/背景 |
| `scope` | KG核心 / KG专项 / KG邻接 / 背景 |

## 三种打开方式

### Obsidian

1. 打开 Obsidian → “打开文件夹作为仓库” → 选择 `knowledge-base/obsidian`。
2. 从 `00-索引/总索引.md` 进入书 A/书 B，再进章节。
3. 每条知识点是一个笔记，含定义、要点、公式、前置/关联双链、来源页、Skill 模块、范围与规范条目。
4. 打开 `知识图谱总览.canvas` 可看到书→章的全局图。
5. 人工批注写到 `30-批注/批注-<ID>.md`，不会被重建覆盖；重跑 `build_exports.py` 后知识点顶部会出现批注链接。
6. 已检查 808 个 Markdown 文件、0 个断链。

### Anki

1. Anki → 导入 `anki/kg-cards.csv`。
2. 字段映射：第 1 列 Front，第 2 列 Back，第 3 列 Tags。
3. 勾选“允许 HTML”，否则 Back 里的换行不生效。
4. `kg-cards.csv` 770 张定义卡；`kg-application-cards.csv` 120 张应用判断卡。
5. 标签包含书/章/覆盖层级/类型/范围。

### 本地检索

```bash
python -I search/kg_search.py "TransE 负采样" --limit 8
python -I search/kg_search.py "实体对齐" --book B --module M4 --limit 5
python -I search/kg_search.py "TransE" --scope KG核心 --limit 5
python -I search/kg_lsa_search.py "零样本实体表示" --limit 5
python -I search/kg_hybrid_search.py "远程监督 噪声" --limit 5
python -I search/kg_rag.py "TransE 怎么处理一对多关系？" --k 3

# 神经向量检索（可选，需自行安装 sentence-transformers / fastembed）
python -I search/kg_vector_search.py "零样本实体表示" --limit 5
python -I search/kg_hybrid_vector.py "远程监督 噪声" --limit 5
```

BM25 是词法检索；语义检索用 `kg_vector_search.py`（BGE 中文向量）或 `kg_hybrid_vector.py`（BM25+向量）。需用 `.venv-embed` 的 Python 运行。

## 数据查询示例

按章浏览：

```bash
grep "A-05-" knowledge-map.md
```

筛出所有“模型”类知识点：

```python
import json
rows = json.load(open("kg-knowledge-points.json", encoding="utf-8"))
for r in rows:
    if r["type"] == "模型":
        print(r["id"], r["title"], r["page"])
```

查某个 Skill 模块覆盖了哪些知识点：

```bash
grep "M5 / distilled §8.4" coverage-matrix.md
```

按前置关系做学习路径：从某点出发，递归读取 `prerequisites`，即可得到拓扑排序。

## 再生成

```bash
python -I build_kb.py                     # 重建 CSV/JSON/Markdown/覆盖矩阵
python -I build_exports.py                # 重建 Obsidian/Anki/Canvas/检索
python -I eval/make_retrieval_set.py      # 重建 100 条检索 smoke 集
python -I eval/eval_retrieval.py          # 跑检索/QA 基线
python -I audit/formula_audit.py          # 重建 132 条公式核对表
python -I audit/number_audit.py           # 实验数值回溯
python -I audit/coverage_audit.py         # 四级覆盖审计
python -I figures/build_figure_index.py   # 重建图表索引
python -I tables/build_tables.py          # 校验/渲染结构化表格
python -I graph/build_graph.py            # 重建类型化图谱 JSON/GraphML/TTL
python -I instances/build_instances.py    # 重建实例层：方法/任务/数据/指标
python -I glossary/build_glossary.py      # 重建术语表
python -I eval/eval_answer_context.py     # 上下文级答案评估
python -I service/graph_service.py --port 8765  # 启动 API/UI
python -I -m unittest discover -s tests   # 数据/链接/CSV 测试
```

构建脚本会：
1. 读取 `data/*.json`；
2. 校验 ID 唯一、字段完整、类型/覆盖合法、引用存在；
3. 生成 CSV/JSON/Markdown/覆盖矩阵/校验报告。

新增章节时，复制一个 `data/A-chXX.json`，按同一结构填写即可。

## 工具版本

- Python 3.13.9
- PyMuPDF 1.28.0（文本层抽取与页面渲染）
- PaddleOCR 3.7.0 / PP-OCRv6 medium（书 B 扫描页 OCR）
- fastembed 0.9.1 + BAAI/bge-small-zh-v1.5（神经向量检索，可选）

## 质量说明

- 定义与要点为**转述**，不是原书摘录；公式保留必要符号。
- 页码为 PDF 页码，通常与实际内容有 ±1 页误差（章节标题与正文共享页面）。
- 书 B 为 OCR 文本，公式、表格、图注可能有识别误差；涉及关键公式时请对照原书。
- 本知识库是“知识点索引 + 简要解释”，不能替代原书阅读；它的价值是检索、路径、覆盖审计和与 Skill 的映射。
- `coverage` 表示该点在 Skill 中的使用层级，不代表原书重要性。
- 检索基线：BM25 在 100 条 smoke 集 Recall@5=1.0、MRR=0.958；30 条 QA 集 Recall@5=0.833、MRR=0.763。语义改写查询上 Hybrid-vector 的 MRR 0.524 高于 BM25 0.449，但关键词查询仍以 BM25 为主。详见 `eval/report*.md`。
- 公式核对：132 条，自动检查 132/132，逐条人工 101 条 + 源码符号对照 31 条，修正 4 条。详见 `audit/formula-audit.md`。
- 实验数值回溯：61 条实验/评估点，57 条在引用页可检索到关键数字，4 条派生/指标名/取整经人工确认，0 条待复核。详见 `audit/number-audit.md`。
- 覆盖审计：书 A 二级 50/50、三级 158/158；书 B 二级 41/41、三级 82/82；442 个图表中 0 个被知识点显式引用。A 1.5 与 B 7.3.1 已补点。详见 `audit/coverage-audit.md`。
- 图表索引：442 条（342 图 / 100 表）；100 张表有表注，44 条核心图表有精确关联；见 `figures/figure-index.md`。
- 表格记录：100 张（37 矩阵 / 5 键值 / 58 索引），0 结构错误、0 源码数字未匹配；见 `tables/table-validation.md`。
- 图谱导出：1361 节点、3140 边、12 种关系、0 前置环；图表挂到二级节；`mentions_dataset` / `mentions_metric` 是词面匹配，不是逐条人工确认。详见 `graph/README.md`。
- 统一检索 + BGE + bge-reranker：30 条 QA、k=15 时命中 0.900、支持覆盖 0.719、上下文精确率 0.118。见 `eval/report-unified-answer.md`。
- 答案级评估（15 条 gold）：覆盖优先 0.756 / 引用精确 0.439；引用优先 0.622 / 0.700。见 `eval/report-answer-quality.md`。
- 生成式答案（15 条 gold）：DeepSeek 覆盖 0.717 / 引用精确 0.589 / 引用召回 0.522 / 支持度 0.636；Opus 覆盖 0.889 但引用 0.367。见 `llm/report-generated-compare.md`。
- 引用 NLI：34 条引用中 30 supported / 3 partial / 1 unsupported；严格过滤后全部 supported，但 gold 精确率 0.556。见 `llm/nli-report.md`。
- 公开包：`dist/kg-public.zip`；`public_release_check --root dist/public-kg --strict` 为 0 敏感项 / 0 本地资产。
- 多查询分解：k=15 支持覆盖 0.613，低于统一检索 0.719，暂不采用。见 `eval/report-multi-query.md`。
- 索引刷新：BGE 与统一向量缓存带 `source_hash`，源数据变化自动重建；`--rebuild` 强制刷新；`final_check` 检查索引文件存在。
- 真实场景回测：Haiku 3 次重复均 10/10；3 模型追问 30/30 分支、117/120 概念。见 `outputs/kg-engineering/evals/backtest-real-stability.md`。
- 图谱边审计：`evaluated_on` 20/20、`mentions_dataset` 10/10、`variant_of` 14/14、`improves` 9/9。见 `graph/edge-audit-full.md`。
- 真实场景 Skill 回测：3 模型 × 10 场景，30/30 分支、123/123 概念。见 `outputs/kg-engineering/evals/backtest-real.md`。
- 多模态：373 个图表页 + CLIP 索引；图像→图像稳定，中文文本→图较弱。
- 测试：`tests/` 38 项通过（含知识图谱端点/关系/导出文件、图表索引与精确关联校验）。

## 与 Skill 的关系

- Skill `kg-engineering` 负责“怎么做”；
- 本知识库负责“有哪些点、在哪、前置是什么、对应 Skill 哪个模块”；
- `coverage-matrix.md` 是两者的桥：可以反查某个 Skill 模块覆盖了哪些知识点，也可以查某章知识点是否已被 Skill 吸收。
