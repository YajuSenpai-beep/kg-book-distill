# -*- coding: utf-8 -*-
"""Build a citation-ready RAG context block from the knowledge base.

This does not call an LLM; it retrieves top-k points and formats them with
stable IDs so any model can cite [A-05-04-24] in its answer.
"""
import argparse, importlib.util, os, sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("kg_search", os.path.join(BASE, "kg_search.py"))
kg = importlib.util.module_from_spec(spec)
spec.loader.exec_module(kg)


def build(query, k=6, scope=None, max_chars=4000):
    hits = kg.bm25(query, limit=k, scope=scope)
    lines = [
        "你是知识图谱工程助手。请只依据下面的资料回答；每个结论后用 [ID] 标注来源。",
        "如果资料不足，请明确说“资料不足”，不要编造。",
        "",
        "资料：",
    ]
    used = 0
    for i, (score, r) in enumerate(hits, 1):
        block = (
            f"[{i}] ({r['id']}) {r['title']}（{r['page']}）\n"
            f"定义：{r['definition']}\n"
            f"要点：{r['key_points']}\n"
        )
        if r["formula"]:
            block += f"公式/示例：{r['formula']}\n"
        if used + len(block) > max_chars:
            break
        lines.append(block)
        used += len(block)
    lines += ["", f"问题：{query}", "", "回答："]
    return "\n".join(lines), hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--k", type=int, default=6)
    ap.add_argument("--scope")
    ap.add_argument("--max-chars", type=int, default=4000)
    a = ap.parse_args()
    text, hits = build(a.query, a.k, a.scope, a.max_chars)
    print(text)
    print("\n--- 命中 ---")
    for score, r in hits:
        print(f"{score:6.2f} {r['id']} {r['title']} [{r['page']}]")


if __name__ == "__main__":
    main()
