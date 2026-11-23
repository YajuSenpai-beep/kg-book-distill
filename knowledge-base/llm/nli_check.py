# -*- coding: utf-8 -*-
"""Sentence-level citation entailment check with an LLM judge.

Usage:
  DEEPSEEK_API_KEY=... python -I llm/nli_check.py \
      --answers llm/answers-gen-deepseek.jsonl --out llm/answers-nli.jsonl

For each sentence with [ID], ask the judge whether the cited context supports
the sentence. Keep supported citations; drop unsupported; record partial.
"""
import argparse, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from client import Client, extract_json

BASE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.dirname(BASE)
CACHE_PATH = os.path.join(BASE, "nli_cache.json")
PROMPT = """判断“资料”是否支持“句子”中的结论。只输出 JSON：
{{"label":"supported|partial|unsupported","reason":"一句话"}}

句子：{sentence}
资料：[{cid}] {context}
"""


def sentences(answer):
    return [s.strip() for s in re.split(r"(?<=[。；！？\n])", answer) if s.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--answers", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--provider", default="deepseek")
    ap.add_argument("--min-label", choices=["supported", "partial"], default="supported")
    a = ap.parse_args()
    answers = [json.loads(x) for x in open(a.answers, encoding="utf-8") if x.strip()]
    ctx = {x["q"]: {c["id"]: c["text"] for c in x["contexts"]}
           for x in json.load(open(os.path.join(BASE, "contexts.json"), encoding="utf-8"))}
    cache = json.load(open(CACHE_PATH, encoding="utf-8")) if os.path.exists(CACHE_PATH) else {}
    c = Client(a.provider)

    out = []
    stats = {"supported": 0, "partial": 0, "unsupported": 0}
    for item in answers:
        text = item.get("answer", "")
        kept = []
        for cid in item.get("citations", []):
            sents = [s for s in sentences(text) if f"[{cid}]" in s]
            if not sents:
                continue
            labels = []
            for s in sents:
                sent = s.replace(f"[{cid}]", "")
                key = f"{a.provider}|{sent}|{cid}"
                if key not in cache:
                    raw = c.generate(PROMPT.format(sentence=sent, cid=cid,
                                                   context=ctx.get(item["q"], {}).get(cid, "")[:800]))
                    obj = extract_json(raw) or {}
                    cache[key] = {"label": obj.get("label", "unsupported"),
                                  "reason": obj.get("reason", "")}
                labels.append(cache[key]["label"])
            best = "supported" if "supported" in labels else ("partial" if "partial" in labels else "unsupported")
            stats[best] += 1
            if best == "supported" or (a.min_label == "partial" and best == "partial"):
                kept.append(cid)
            else:
                text = text.replace(f"[{cid}]", "")
        item = dict(item)
        item["answer"] = text
        item["citations"] = kept
        out.append(item)
        print(f"{item['q'][:30]} kept={len(kept)}")
    json.dump(cache, open(CACHE_PATH, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    with open(a.out, "w", encoding="utf-8") as f:
        for x in out:
            f.write(json.dumps(x, ensure_ascii=False) + "\n")
    print("labels", stats, "wrote", a.out)


if __name__ == "__main__":
    main()
