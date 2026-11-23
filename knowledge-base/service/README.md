# 图谱查询服务与 Web UI

零依赖：只用 Python 标准库 + 原生 JS，不需要 Flask/FastAPI/Neo4j。

## 运行

```bash
cd knowledge-base
python -I service/graph_service.py --port 8765
```

打开 http://127.0.0.1:8765/

## API

| 端点 | 说明 |
|---|---|
| `GET /healthz` | 健康检查 |
| `GET /api/stats` | 节点/边/可检索条目统计 |
| `GET /api/search?q=TransE&kind=table&limit=10&offset=0` | 统一搜索（分页）：知识点/图表/表格/术语/方法 |
| `GET /api/node/<id>` | 节点/文档详情 + 出入边 + 邻居 |
| `GET /api/neighbors/<id>` | 邻居映射 |
| `GET /api/path?from=M-TransE&to=DS-FB15K` | 5 跳内 BFS 路径 |

示例：

```bash
curl "http://127.0.0.1:8765/api/search?q=FB15K"
curl "http://127.0.0.1:8765/api/node/M-TransR"
curl "http://127.0.0.1:8765/api/path?from=M-DKRL&to=DS-FB20K"
```

## UI

- 左侧搜索，中间 1 跳邻域 SVG，右侧节点详情与关系。
- 点击邻居继续展开；路径输入框支持 BFS 找链。
- 只读，不写入图。

## 可选 token 与 Docker

```bash
python -I service/graph_service.py --port 8765 --token secret
# 请求带 ?token=secret 或 Authorization: Bearer secret

docker compose -f service/docker-compose.yml up --build
```

## 检索说明

- 系统 Python：BM25 统一检索（约 1370 条文档）。
- 嵌入 venv：自动用 BGE + bge-reranker 重排；首次会下载模型。
- 图像检索见 `../search/image_search.py`（CLIP；图像→图像较稳，中文文本→图较弱）。

## 限制

- 服务加载实例层做图查询，另用统一索引做文档检索；主图仍用 JSON/GraphML/TTL 交换。
- 默认绑定 `127.0.0.1`，不要直接暴露到公网。
- 有可选 token、分页、60 秒内存缓存、120 次/分钟/IP 限流；没有用户体系/持久化，仍是演示级服务。
