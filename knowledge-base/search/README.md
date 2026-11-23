# 检索脚本

| 脚本 | 范围 | 依赖 |
|---|---|---|
| `kg_search.py` | 770 知识点 BM25 | 无 |
| `kg_vector_search.py` | 知识点 BGE 向量 | `.venv-embed` + fastembed |
| `kg_hybrid_search.py` | BM25 + LSA | scikit-learn |
| `kg_hybrid_vector.py` | BM25 + BGE | `.venv-embed` |
| `exhibit_search.py` | 442 图表 + 100 表 BM25 | 无 |
| `unified_search.py` | 知识点/图表/表格/术语/实例统一检索 | 系统 Python 走 BM25；venv 走 BGE + reranker |
| `image_search.py` | 373 个图表页的 CLIP 图像检索 | `.venv-embed` + fastembed |
| `kg_rag.py` | 带 [ID] 引用的 RAG 上下文块 | 无 |

## 统一检索

```bash
python -I search/unified_search.py "TransR 结果" --limit 5
python -I search/unified_search.py "表2-1" --kind table
```

嵌入 venv 会自动加 BGE 向量和 `bge-reranker-base` 重排：

```bash
.venv-embed\Scripts\python.exe -I search/unified_search.py "多跳逻辑查询" --limit 5
```

## 图像检索

```bash
.venv-embed\Scripts\python.exe -I search/image_search.py --image figures/pages/A-282.jpg
.venv-embed\Scripts\python.exe -I search/image_search.py --text "TransR architecture"
```

默认文本查询走 **图注 BM25**（中文可用），`--mode clip` 才走 CLIP 文本→图。CLIP 图像→图像稳定；原版 CLIP 中文文本→图较弱。

## 评测

- `../eval/eval_unified_answer.py`：统一检索 + 重排的上下文答案评估。
- 结果：k=15 时命中 0.900、支持覆盖 0.719、上下文精确率 0.118。
