# Changelog

## 3.0.0（引用 NLI、公开包、多查询实验）

- 引用 NLI：`llm/nli_check.py`，DeepSeek 逐句判断 34 条引用：30 supported / 3 partial / 1 unsupported。
  - 严格过滤后 30 条全部 supported；gold 引用精确率 0.556、召回 0.500。
  - 说明：NLI 支持率 100%，但 gold 精确率下降；两个指标不能互相替代。
- 公开包：`tools/make_public.py`，生成 `dist/public-kg/` + `dist/kg-public.zip`；排除扫描页、抽取文本、缓存、原始答案；`public_release_check --root dist/public-kg --strict` 结果 0 findings / 0 local assets。
- 多查询分解：`search/multi_query.py` + `eval/eval_multi_query.py`。
  - unified k=15：命中 0.900、支持 0.719。
  - multi-query k=15：命中 0.867、支持 0.613。
  - 结论：当前查询扩展/分解没有超过统一检索，**不采用为默认**，保留实验脚本。
- 测试 38 项；final_check 50 项；版本 3.0.0。

## 2.9.0（DeepSeek 实跑、索引刷新、引用修补）

- DeepSeek `deepseek-chat` 实跑 15 条 QA：
  - 覆盖 0.717、引用精确 0.589、引用召回 0.522、引用有效性 1.000、拒答 0.133。
  - 引用句支持度（词面代理）0.636。
  - 相比未加约束的 DeepSeek（0.482 / 0.539），引用精确率明显提升。
- 引用修补：prompt 要求优先引用知识点、每条结论最多 2 个引用、全文最多 4 条；`citation_check.py` 做句内过滤与 3 条上限。
- 索引刷新：`kg_vector_search.py` / `unified_search.py` 的缓存写入 `source_hash`，源数据变化自动重建；`--rebuild` 强制刷新；`final_check` 检查索引是否新于数据。
- NOTICE 修正：`figures/pages/` 明确为本地核对缓存，公开/商业交付必须删除；新增 `.gitignore`。
- 测试 35 项；final_check 47 项；版本 2.9.0。

## 2.8.0（生成式答案层）

- 新增 `llm/`：provider 无关客户端（Anthropic/DeepSeek/Qwen/GLM/Moonshot/Ollama/Mock），零 SDK 依赖。
- `generate_answers.py`：检索 → prompt → 生成 → 引用 ID 校验；`eval_generated.py` 评估覆盖/引用/拒答。
- 用 15 条 gold QA 做生成式对比（3 个模型）：
  - Haiku：覆盖 0.800、引用精确 0.500、引用召回 0.544。
  - Sonnet：覆盖 0.806、引用精确 0.384、引用召回 0.578。
  - Opus：覆盖 0.889、引用精确 0.367、引用召回 0.594。
  - 抽取式基线：覆盖 0.756、引用精确 0.439、引用召回 0.660。
- 结论：生成式提高答案覆盖，但引用精确率/召回率没有同步提高；需要引用约束或 NLI 复核。
- 测试 35 项；final_check 45 项；版本 2.8.0。

## 2.7.0（补齐 1–7 的缺口）

- 答案级评估：`eval/answer_engine.py` + `eval/eval_answer_quality.py`，15 条 gold QA。
  - 覆盖优先：关键词覆盖 0.756、引用精确率 0.439、引用召回率 0.660。
  - 引用优先：覆盖 0.622、引用精确率 0.700、引用召回率 0.516。
- 表格：37 矩阵 + 5 键值 + 58 索引（新增 3-10、3-16、4-4、5-7、6-6）。
- 真实回测：Haiku 基础场景 3 次重复均 10/10；3 模型追问 30/30 分支、117/120 概念。见 `backtest-real-stability.md`。
- 多模态：文本→图默认走图注 BM25（中文可用），CLIP 仍可 `--mode clip`。
- 服务：分页 offset、60 秒缓存、120 次/分钟/IP 限流。
- 测试 32 项；final_check 44 项；版本 2.7.0。

## 2.6.0（1–7 改进）

- 统一检索：`search/unified_search.py`，索引 1370 条（知识点/图表/表格/术语/实例），BM25 + BGE + bge-reranker。
- 答案评估：`eval/eval_unified_answer.py`，k=15 命中 0.900、支持覆盖 0.719、上下文精确率 0.118。
- 图谱边审计：`graph/edge-audit-full.md`，evaluated_on 20/20、mentions 10/10、variant 14/14、improves 9/9。
- 真实场景回测：`evals/backtest-real.md`，3 模型 × 10 场景，30/30 分支、123/123 概念。
- 多模态：本地页面渲染脚本（不随公开包分发）；`figures/build_multimodal.py` CLIP 索引；`search/image_search.py`。
- 表格：37 矩阵 + 5 键值 + 58 索引（新增 7 张矩阵）。
- 学习路径：`tools/learning_path.py` 支持 known/max-steps/minutes/Markdown。
- 服务：统一搜索、healthz、可选 token、Dockerfile/compose；UI 支持知识点/图表/表格检索。
- 测试 32 项；final_check 42 项；版本 2.6.0。

## 2.5.0（P0–P3 收尾）

- P0：移除 5 个孤立节点；拆分 `evaluated_on` / `mentions_dataset` 与 `reports_metric` / `mentions_metric`；补三级节父边；测试改为按数据推导；图表注/表注统一到 `table-data.json`；`run_all.py` 支持 `--with-vector`。
- P1：新增 `search/exhibit_search.py`（图表检索）、`glossary/`（40 术语）、`eval/eval_answer_context.py`（上下文级答案评估）、`tools/learning_path.py`（前置路径）、Obsidian 笔记增加“本节图表”。
- P2：明确内容边界：25 张矩阵、10 张键值、70 张索引；无习题可抽；不逐图写 342 条摘要。详见 `audit/content-scope.md`。
- P3：新增 `instances/`（64 方法 / 18 任务 / 26 数据集 / 10 指标，118 节点 176 边）、`service/`（零依赖 API + Web UI）、`.github/workflows/ci.yml`。
- 图谱：1361 节点、3140 边、12 种关系、0 孤立节点、0 前置环。
- 测试：32 项；final_check 扩到 38 项。
- 版本 2.5.0。

## 2.4.6

- 表格矩阵再补 12 张：表2-10、2-11、2-17、2-18、2-19、2-21、2-22、5-2、6-3、6-5、7-6、7-8。
- 状态更新为 25 张矩阵 + 5 张键值 + 70 张索引；42 张有单元格级数据。
- 校验：100 张表、0 结构错误、0 源码数字未匹配。
- 测试 22 项；final_check 30 项全部通过。

## 2.4.5

- 表格数据层扩展到全部 100 张表：13 张完整矩阵、5 张键值配置表、82 张索引记录。
- 新增矩阵：表2-2（分关系类型）、表2-14（DKRL 关系预测）、表7-1（LIWC 统计）。
- 新增键值表：表3-1、表3-4、表3-8、表3-11、表4-2（超参数）。
- 校验：100 张表、0 结构错误、0 源码数字未匹配。
- 图谱 Table 节点增加 data_status；18 张有单元格级数据，82 张为索引记录。
- 测试仍 22 项；final_check 扩到 30 项。

## 2.4.4

- 新增表格数据层：`tables/table-data.json`，10 张核心实验表结构化（TransR、PTransE、KR-EAR、DKRL、TKRL、HATT、IPTransE、义原、SDLM）。
- 新增 `tables/build_tables.py`：行列一致性、数值类型、页码、源码数字回溯校验；结果 10 张表、0 结构错误、0 未匹配。
- 图谱 Table 节点增加 `structured` / `data_rows` / `data_columns` 属性；10 张表已标记。
- 测试增至 22 项；新增表格结构/渲染测试。
- 已知边界：只结构化 10/100 张表，行列表头为人工整理。

## 2.4.3

- 图表索引补全：100 张表全部有表注（原 44 张）。
- 新增 44 条核心图表的精确 `illustrates` 映射（46 条边），图表→知识点不再只靠小节级关联。
- 图谱：1366 节点、3139 边、10 种关系；新增 `illustrates`。
- 新增 `audit/final_check.py` 与 `final-verification.md`：26 项一致性检查全部通过。
- 测试增至 19 项。

## 2.4.2

- 新增图表索引层：`figures/build_figure_index.py`，输出 `figure-index.json/csv/md`。
  - 442 条（342 图 / 100 表），含图注、页码、所属小节、角色、上下文、关联知识点。
  - 44 条核心实验表/架构图有人工要点；其余保留图注与上下文，不编造摘要。
- Obsidian 新增 `40-图表索引.md`。
- 图谱接入图表节点：1366 节点、3139 边、10 种关系；Figure 342、Table 100；`in_section` 1212。
- 覆盖审计改用图表索引口径：442 个图表，显式引用仍为 0。
- 测试更新：图谱节点/边/图表节点校验；新增图表索引 5 项测试，总计 19 项。

## 2.4.1

- 补齐 P0 发现的两个实质稀薄节：
  - 书 A 1.5“建立知识图谱的系统工程观”：+3 条（持续积累的领域知识工程、技术栈五层、按领域设计系统架构）。
  - 书 B 7.3.1“相关工作”：+4 条（神经语言模型分工、分层解码器路线、专家积/稀疏乘积、标题生成定位）。
- 知识点 770（A 419 / B 351），节 94。
- 覆盖审计：书 B 三级 82/82；稀薄小节从 19 降到 14，剩余均为小结/结构/展望。
- 图谱重建：924 节点、2651 边、9 种关系、0 前置环。
- 数据集边抽样 20 条：20/20 确实提到数据集，但仅 7/20 是严格“在该数据集上评估”；原 `evaluated_on` 改名为 `mentions_dataset`，`reports_metric` 改为 `mentions_metric`，见 `graph/edge-audit.md`。
- 测试与 README 计数同步；Obsidian 807 个 Markdown、0 断链。

## 2.4.0

- P0 四级覆盖审计：`audit/coverage_audit.py`，输出 `coverage-audit.md` / `coverage-gaps.csv` / `coverage-sections.csv`。
  - 书 A：二级 50/50、三级 158/158；书 B：二级 41/41、三级 81/82。
  - 图表 411 个，同页有知识点 408 个，但被知识点显式引用 0 个。
  - 发现 19 个稀薄小节（二级 17 + 三级 2），其中 A 1.5“知识图谱的系统工程”是实质缺口，其余多为“小结”。
- P1 公式全量核对：132 条，自动 132/132；逐条人工 101 条 + 源码符号对照 31 条；修正 4 条（新增 PMI 括号修正）。
- P1 实验数值回溯：61 条实验/评估点，57 条引用页可检索关键数字，4 条派生/指标名/取整人工确认，0 条待复核。
- P2 类型化图谱：`graph/build_graph.py`，输出 JSON/GraphML/TTL。
  - 916 节点：763 知识点 + 93 节 + 17 章 + 2 书 + 29 数据集 + 12 指标。
  - 2629 边、9 种关系：part_of、in_section、prerequisite_of、related_to、variant_of、improves、evaluated_on、reports_metric、canonical_of。
  - 0 前置环、5 个孤立节点。
- 测试扩展到 14 项，新增图谱端点/关系/导出文件校验。
- README、根 README 同步覆盖审计、数值核对与图谱导出说明。

## 2.3.0

- 内容深度第二批：新增 42 条实验/评估细节，知识点 763（A 416 / B 347）。
- 书 B 第 2 章：TransR/CTransR 训练配置与分关系结果、PTransE 结果与重排序、KR-EAR 三子任务、DKRL 补全/类型/零样本、TKRL 类型约束与长尾。
- 书 B 第 3 章：NYT 远程监督口径、选择性注意力对比、HATT 设置/长尾、MNRE 双语数据/结果、KATT 联合学习结果。
- 书 B 第 4 章：DFB 数据集、实体对齐结果、迭代软对齐收敛、EDRM 场景/消融。
- 书 B 第 5–7 章：义原词表示、WSD、SAT、义原预测 MAP、CSP 低频鲁棒性、LIWC/HDSA、SDLM 困惑度。
- 书 A：少样本/零样本评估边界、GNN 长尾关系迁移、PKGM 下游指标。
- 测试与应用卡数量同步：定义卡 763、应用卡 120、Obsidian 800 个 Markdown。
- 检索基线随语料更新：BM25 检索 MRR 0.958、QA MRR 0.763；Hybrid-vector 语义改写 MRR 0.524。

## 2.2.0

- 内容深度：新增 19 条实验/评估细节，知识点 721。
- 公式抽检：100/100 人工核对，修正 GCN、模块度、义原正则 3 条。
- Obsidian：新增 `30-批注/` 人工批注层，重建不覆盖。
- 检索：新增 BGE 中文神经向量检索与 BM25+BGE 混合检索；语义改写查询 Hybrid MRR 0.530 > BM25 0.457。
- 测试：扩展到 10 项，覆盖 Canvas、应用卡、链接。

## 2.1.0

- 增加 `canonical_id`：17 条近重复/跨书重复条目指向规范条目。
- 增加 `scope`：KG核心 417、KG专项 180、KG邻接 60、背景 64。
- 生成范围索引与 `--scope` 检索过滤。
- 新增 100 条检索 smoke 集、30 条 QA 集，BM25 基线：检索 Recall@5=1.0、MRR=0.958；QA Recall@5=0.867、MRR=0.774。
- 新增 LSA 与 Hybrid 检索；当前评测未超过 BM25，默认仍用 BM25，报告见 `eval/report-lsa.md`、`eval/report-hybrid.md`。
- 新增 `kg_rag.py`：输出带 [ID] 引用的 RAG 上下文块，不调用 LLM。
- 新增 BGE 中文神经向量检索与 BM25+向量混合检索；在 20 条语义改写查询上 Hybrid MRR 0.530 > BM25 0.457。
- 新增 Obsidian 批注层 `30-批注/`：人工批注不会被重建覆盖，含 10 条示例。
- 新增 100 条公式抽检表：自动检查 100/100 通过，人工核对 100/100，修正 3 条。
- Obsidian：新增知识图谱总览 Canvas、范围索引。
- Anki：新增 99 张应用判断卡。
- 新增 `tests/`、`VERSION`、`NOTICE.md`。
- Skill：新增路由表、3 个可执行脚本（Schema/抽取/链接预测）。
- 内容深度：新增 19 条实验/评估细节，知识点总数 721。

## 2.0.0

- 知识点从 447 扩到 702，补书 B 第2–7章细节、书 A 9.5/9.6、合并点拆分。
- 生成 Obsidian Vault（702 笔记 + 索引）、Anki 702 张、BM25 检索脚本。

## 1.0.0

- 知识点 447，覆盖 17 章 / 93 节。
- 生成 knowledge-map、CSV、JSON、coverage-matrix、validation-report、spot-check。
