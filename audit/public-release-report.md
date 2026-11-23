# 公开发布脱敏检查

## 必须移除/脱敏

- 未发现 API key、绝对路径、来源站点或 PDF 文件名。

## 本地资产（公开包应删除）

- 未发现本地大资产。

## 发布前检查清单

- [ ] 删除 `extracted/`、`knowledge-base/figures/pages/`、`.embed_cache/`、`.venv-embed/`
- [ ] 删除 `search/*_vectors.npz`、`search/vector_index.npz`（可重建）
- [ ] 替换所有 `C:\Users\...` / `/Users/...` 绝对路径
- [ ] 确认 `NOTICE.md` 与实际文件一致
- [ ] 轮换任何曾出现在聊天/日志中的 API key
- [ ] 确认公开包不含原书 PDF、扫描页、长段原文
- [ ] 为派生内容确认授权/许可证