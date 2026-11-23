# -*- coding: utf-8 -*-
"""Build a 100-query retrieval smoke set from knowledge-point key phrases."""
import json, os, random
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
ROWS = json.load(open(os.path.join(BASE, "..", "kg-knowledge-points.json"), encoding="utf-8"))
random.seed(42)

by_scope = defaultdict(list)
for r in ROWS:
    if r["key_points"]:
        by_scope[r["scope"]].append(r)

# 按范围比例分配 100 条
total = len(ROWS)
queries = []
for scope, items in by_scope.items():
    n = max(1, round(100 * len(items) / total))
    queries.extend(random.sample(items, min(n, len(items))))

# 补齐/裁剪到 100
all_items = [r for r in ROWS if r["key_points"]]
random.shuffle(all_items)
for r in all_items:
    if len(queries) >= 100:
        break
    if r not in queries:
        queries.append(r)
queries = queries[:100]

out = []
for r in queries:
    kp = [x for x in r["key_points"].split("；") if x][:2]
    q = "；".join(kp) + f"（{r['section_title']}）"
    out.append({
        "q": q,
        "relevant": [r["id"]],
        "scope": r["scope"],
        "book": r["book"],
    })

path = os.path.join(BASE, "retrieval_queries.jsonl")
with open(path, "w", encoding="utf-8") as f:
    for x in out:
        f.write(json.dumps(x, ensure_ascii=False) + "\n")
print("wrote", path, len(out))
