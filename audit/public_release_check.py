# -*- coding: utf-8 -*-
"""Check the repo for material that must be removed/redacted before publishing.

Usage: python -I audit/public_release_check.py [--strict]
Output: audit/public-release-report.md
"""
import argparse, os, re, sys

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
TEXT_EXT = {".md", ".py", ".json", ".jsonl", ".csv", ".yml", ".yaml", ".txt", ".toml", ".html", ".js", ".sha256"}
SKIP_DIRS = {".git", ".venv-embed", ".embed_cache", "pages", "extracted", "work", "__pycache__"}
PATTERNS = [
    ("API key", re.compile(r"sk-[A-Za-z0-9]{20,}")),
    ("API key env", re.compile(r"(ANTHROPIC|DEEPSEEK|DASHSCOPE|ZHIPU|MOONSHOT)_API_KEY\s*=\s*['\"]?[A-Za-z0-9_\-]{10,}")),
    ("absolute Windows path", re.compile(r"[A-Za-z]:\\Users\\[^\s\"'<>]+")),
    ("absolute POSIX path", re.compile(r"/(?:Users|home)/[^\s\"'<>]+")),
    ("source site", re.compile(r"z-library|1lib|z-lib", re.I)),
    ("book PDF", re.compile(r"知识图谱(?:导论|与深度学习)[^\n]{0,40}\.pdf")),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--root", default=ROOT)
    a = ap.parse_args()
    scan_root = os.path.abspath(a.root)
    findings = []
    for dirpath, dirnames, filenames in os.walk(scan_root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            p = os.path.join(dirpath, fn)
            rel = os.path.relpath(p, scan_root)
            if rel.replace(os.sep, "/") in ("audit/public_release_check.py",
                                             "audit/public-release-report.md"):
                continue
            if os.path.getsize(p) > 2_000_000:
                continue
            if os.path.splitext(fn)[1].lower() not in TEXT_EXT:
                continue
            try:
                text = open(p, encoding="utf-8", errors="ignore").read()
            except Exception:
                continue
            for name, pat in PATTERNS:
                for m in pat.finditer(text):
                    findings.append((name, rel, m.group(0)[:80]))

    local_assets = []
    for rel in ("extracted", "knowledge-base/figures/pages", ".venv-embed", ".embed_cache"):
        p = os.path.join(scan_root, rel)
        if os.path.exists(p):
            size = sum(os.path.getsize(os.path.join(dp, f)) for dp, _, fs in os.walk(p) for f in fs)
            local_assets.append((rel, f"{size/1024/1024:.1f} MB"))

    lines = ["# 公开发布脱敏检查\n",
             "## 必须移除/脱敏\n"]
    if findings:
        for name, rel, hit in findings:
            lines.append(f"- `{name}` in `{rel}`: `{hit}`")
    else:
        lines.append("- 未发现 API key、绝对路径、来源站点或 PDF 文件名。")

    lines += ["\n## 本地资产（公开包应删除）\n"]
    for rel, size in local_assets:
        lines.append(f"- `{rel}`：{size}")
    if not local_assets:
        lines.append("- 未发现本地大资产。")

    lines += ["\n## 发布前检查清单\n",
              "- [ ] 删除 `extracted/`、`knowledge-base/figures/pages/`、`.embed_cache/`、`.venv-embed/`",
              "- [ ] 删除 `search/*_vectors.npz`、`search/vector_index.npz`（可重建）",
              "- [ ] 替换所有 `C:\\Users\\...` / `/Users/...` 绝对路径",
              "- [ ] 确认 `NOTICE.md` 与实际文件一致",
              "- [ ] 轮换任何曾出现在聊天/日志中的 API key",
              "- [ ] 确认公开包不含原书 PDF、扫描页、长段原文",
              "- [ ] 为派生内容确认授权/许可证"]
    open(os.path.join(BASE, "public-release-report.md"), "w", encoding="utf-8").write("\n".join(lines))
    print(f"findings {len(findings)}; local assets {len(local_assets)}")
    if a.strict and (findings or local_assets):
        sys.exit(1)


if __name__ == "__main__":
    main()
