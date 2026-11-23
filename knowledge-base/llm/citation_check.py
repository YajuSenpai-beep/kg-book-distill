# -*- coding: utf-8 -*-
"""Sentence-level citation support and pruning."""
import re


def tokens(text):
    text = text.lower()
    out = re.findall(r"[a-z0-9]+", text)
    for run in re.findall(r"[一-鿿]+", text):
        out.extend(run)
        out.extend(run[i:i + 2] for i in range(len(run) - 1))
    return set(out)


def sentences(answer):
    return [s.strip() for s in re.split(r"(?<=[。；！？\n])", answer) if s.strip()]


def support(sentence, context):
    a, b = tokens(sentence), tokens(context)
    if not a:
        return 0.0
    return len(a & b) / len(a)


def prune(answer, citations, context_map, min_support=0.0, max_citations=3):
    """Drop citations not inline or not lexically supported; cap count."""
    sents = sentences(answer)
    kept, dropped = [], []
    for c in citations:
        inline = [s for s in sents if f"[{c}]" in s]
        if not inline:
            dropped.append((c, "not inline"))
            continue
        ctx = context_map.get(c, "")
        score = max((support(s.replace(f"[{c}]", ""), ctx) for s in inline), default=0.0)
        if score < min_support:
            dropped.append((c, f"low support {score:.2f}"))
            continue
        kept.append((score, c))
    kept = [c for _, c in sorted(kept, reverse=True)[:max_citations]]
    for c, _ in dropped:
        answer = answer.replace(f"[{c}]", "")
    return answer, kept, dropped
