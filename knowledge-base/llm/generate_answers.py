# -*- coding: utf-8 -*-
"""Retrieve contexts and ask an LLM for a citation-grounded answer."""
import argparse, importlib.util, json, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from client import Client, extract_json
from citation_check import prune

BASE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.dirname(BASE)
spec = importlib.util.spec_from_file_location("u", os.path.join(KB, "search", "unified_search.py"))
u = importlib.util.module_from_spec(spec)
spec.loader.exec_module(u)
GOLD = [json.loads(x) for x in open(os.path.join(KB, "eval", "qa_gold.jsonl"),
                                   encoding="utf-8") if x.strip()]

PROMPT = """你是知识图谱工程助手。只能使用下面给出的资料回答，不得使用资料之外的知识。
每条结论后用 [ID] 标注来源；优先引用知识点（ID 以 A-/B- 开头），图表/表格只在直接给出数据时引用；每条结论最多 2 个引用、全文最多 4 条；资料不足时把 insufficient 设为 true，并在 answer 中说明缺什么。
只输出 JSON：{{"answer": "...", "citations": ["ID1"], "insufficient": false}}

问题：{q}

资料：
{ctx}
"""


def contexts(q, k=10):
    return [(s, d) for s, d in u.search(q, k)]


POINTS_ONLY = False


def build(q):
    hits = contexts(q)
    if POINTS_ONLY:
        hits = [h for h in hits if h[1]["kind"] == "point"]
    lines = [f"[{d['id']}] {d['title']}: {d['text'][:400]}" for _, d in hits]
    return PROMPT.format(q=q, ctx="\n".join(lines)), [d["id"] for _, d in hits], hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider")
    ap.add_argument("--model")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", default=os.path.join(BASE, "answers-generated.jsonl"))
    ap.add_argument("--points-only", action="store_true")
    a = ap.parse_args()
    global POINTS_ONLY
    POINTS_ONLY = a.points_only
    if a.model:
        os.environ["KG_LLM_MODEL"] = a.model
    c = Client(a.provider)
    items = GOLD[:a.limit] if a.limit else GOLD
    ctx_dump, answers = [], []
    for i, x in enumerate(items, 1):
        prompt, ids, hits = build(x["q"])
        ctx_dump.append({"q": x["q"], "ids": ids,
                         "contexts": [{"id": d["id"], "title": d["title"],
                                       "text": d["text"][:400]} for _, d in hits]})
        raw = c.generate(prompt)
        obj = extract_json(raw) or {"answer": raw, "citations": [], "insufficient": None}
        context_map = {d["id"]: d["text"] for _, d in hits}
        raw_cites = [c for c in obj.get("citations", []) if c in ids]
        answer_text, citations, dropped = prune(obj.get("answer", ""), raw_cites, context_map)
        answers.append({"q": x["q"], "answer": answer_text,
                        "citations": citations, "dropped": dropped,
                        "insufficient": obj.get("insufficient"),
                        "context_ids": ids, "provider": c.provider, "model": c.model})
        print(f"{i}/{len(items)} {x['q'][:30]} citations={len(citations)}")
    json.dump(ctx_dump, open(os.path.join(BASE, "contexts.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    with open(a.out, "w", encoding="utf-8") as f:
        for x in answers:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")
    print("wrote", a.out)


if __name__ == "__main__":
    main()
