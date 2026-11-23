# -*- coding: utf-8 -*-
"""Build a sanitized public package.

Usage: python -I tools/make_public.py
Output: dist/public-kg/ and dist/kg-public.zip
"""
import os, re, shutil, sys, zipfile

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)
DIST = os.path.join(ROOT, "dist")
STAGE = os.path.join(DIST, "public-kg")
ZIP = os.path.join(DIST, "kg-public.zip")

INCLUDE = ["README.md", ".gitignore", "LICENSE", "run_all.py", "knowledge-base", "outputs/kg-engineering", "tools", "audit", ".github"]
EXCLUDE_NAMES = {"__pycache__", ".git", ".venv-embed", ".embed_cache"}
EXCLUDE_PATHS = {
    "extracted", "work", "dist",
    "knowledge-base/figures/pages",
    "knowledge-base/search/unified_vectors.npz",
    "knowledge-base/search/vector_index.npz",
    "knowledge-base/llm/answers-generated.jsonl",
    "knowledge-base/llm/answers-gen-haiku.jsonl",
    "knowledge-base/llm/answers-gen-sonnet.jsonl",
    "knowledge-base/llm/answers-gen-opus.jsonl",
    "knowledge-base/llm/answers-gen-deepseek.jsonl",
    "knowledge-base/llm/answers-deepseek.jsonl",
    "knowledge-base/llm/answers-deepseek-points.jsonl",
    "knowledge-base/llm/answers-deepseek-v2.jsonl",
    "knowledge-base/llm/answers-deepseek-pruned.jsonl",
    "knowledge-base/llm/answers-nli.jsonl",
    "knowledge-base/llm/answers-nli-partial.jsonl",
    "knowledge-base/llm/answers-gen-deepseek-nli.jsonl",
    "knowledge-base/llm/nli_cache.json",
    "knowledge-base/llm/contexts.json",
    "knowledge-base/llm/nli_cache.json",
    "knowledge-base/sources.sha256",
    "knowledge-base/sample-review.txt",
    "knowledge-base/sample-v2.txt",
    "knowledge-base/near_dups.txt",
    "knowledge-base/anki_sample.txt",
    "knowledge-base/audit_granularity.py",
    "knowledge-base/check_pages.py",
    "knowledge-base/figures/render_pages.py",
    "audit/source_freeze_check.py",
    "audit/source-freeze-report.md",
    "SOURCE-FREEZE.md",
}
SKIP_DIRS = {"__pycache__", ".git", ".venv-embed", ".embed_cache", "pages", "extracted", "work", "dist"}

PATH_PATTERNS = [
    (re.compile(r"[A-Za-z]:\\Users\\[^\\/]+\\kg-distill\\"), ""),
    (re.compile(r"[A-Za-z]:\\Users\\[^\\/]+\\"), ""),
    (re.compile(r"/(?:Users|home)/[^/]+/"), ""),
]
TEXT_EXT = {".md", ".py", ".json", ".jsonl", ".csv", ".yml", ".yaml", ".txt", ".html", ".js", ".sha256"}

PUBLIC_README = """# 知识图谱两书蒸馏（公开包）

把《知识图谱导论》与《知识图谱与深度学习》蒸馏成可检索知识库、图表索引、结构化表格、类型化图谱与工程 Skill。

## 包含

- 770 个知识点、94 节
- 442 条图表索引（342 图 / 100 表）
- 100 张表记录（37 矩阵 / 5 键值 / 58 索引）
- 主图谱 1361 节点 / 3140 边；实例层 118 节点 / 176 边
- Obsidian / Anki / BM25 / BGE / 统一检索 / 轻量图谱 API
- Skill：outputs/kg-engineering

## 快速开始

    python -I run_all.py --check
    python -I knowledge-base/service/graph_service.py --port 8765

## 不包含

- 原书 PDF、抽取全文、图表扫描页、模型缓存、API key。
- 公开/商业再分发前，请阅读 knowledge-base/NOTICE.md 并确认授权。

## 版本

3.0.0
"""


def excluded(rel):
    rel = rel.replace(os.sep, "/")
    if rel in EXCLUDE_PATHS:
        return True
    if rel.startswith("outputs/kg-engineering/evals/answers-"):
        return True
    if rel.startswith("knowledge-base/llm/answers-"):
        return True
    return any(rel.startswith(p + "/") for p in EXCLUDE_PATHS)


def copy_tree(src, dst):
    for dirpath, dirnames, filenames in os.walk(src):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        rel_dir = os.path.relpath(dirpath, ROOT).replace(os.sep, "/")
        if excluded(rel_dir):
            dirnames[:] = []
            continue
        for fn in filenames:
            rel = os.path.relpath(os.path.join(dirpath, fn), ROOT)
            if excluded(rel):
                continue
            target = os.path.join(dst, rel)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.copy2(os.path.join(dirpath, fn), target)


def sanitize_text():
    changed = 0
    skip = {"audit/public_release_check.py", "tools/make_public.py"}
    for dirpath, _, filenames in os.walk(STAGE):
        for fn in filenames:
            if os.path.splitext(fn)[1].lower() not in TEXT_EXT:
                continue
            p = os.path.join(dirpath, fn)
            if os.path.relpath(p, STAGE).replace(os.sep, "/") in skip:
                continue
            s = open(p, encoding="utf-8", errors="ignore").read()
            t = s
            for pat, repl in PATH_PATTERNS:
                t = pat.sub(repl, t)
            if t != s:
                open(p, "w", encoding="utf-8").write(t)
                changed += 1
    return changed


def main():
    if os.path.exists(STAGE):
        shutil.rmtree(STAGE)
    os.makedirs(STAGE, exist_ok=True)
    for item in INCLUDE:
        src = os.path.join(ROOT, item)
        if os.path.isdir(src):
            copy_tree(src, STAGE)
        elif os.path.exists(src):
            os.makedirs(os.path.dirname(os.path.join(STAGE, item)), exist_ok=True)
            shutil.copy2(src, os.path.join(STAGE, item))
    readme_public = os.path.join(ROOT, "README.public.md")
    if os.path.exists(readme_public):
        shutil.copy2(readme_public, os.path.join(STAGE, "README.md"))
    else:
        open(os.path.join(STAGE, "README.md"), "w", encoding="utf-8").write(PUBLIC_README)
    changed = sanitize_text()
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as z:
        for dirpath, _, filenames in os.walk(STAGE):
            for fn in filenames:
                p = os.path.join(dirpath, fn)
                z.write(p, os.path.relpath(p, STAGE))
    manifest = ["# 公开发布包清单\n",
                f"- 文件数：{sum(len(fs) for _, _, fs in os.walk(STAGE))}",
                f"- 绝对路径改写：{changed} 个文件",
                "- 已排除：extracted/、figures/pages/、.embed_cache/、.venv-embed/、向量缓存、原始答案、NLI 缓存",
                "- 仍需人工确认：授权/许可证、NOTICE 与实际文件一致",
                "- 发布前运行：python -I audit/public_release_check.py --root dist/public-kg --strict"]
    open(os.path.join(DIST, "PUBLIC-MANIFEST.md"), "w", encoding="utf-8").write("\n".join(manifest))
    print("staged", STAGE, "zip", ZIP, "path_rewrites", changed)


if __name__ == "__main__":
    main()
