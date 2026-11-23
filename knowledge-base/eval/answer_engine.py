# -*- coding: utf-8 -*-
"""Extractive answer engine with citations over unified search."""
import importlib.util, json, os, re

BASE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.dirname(BASE)
spec = importlib.util.spec_from_file_location("unified", os.path.join(KB, "search", "unified_search.py"))
u = importlib.util.module_from_spec(spec)
spec.loader.exec_module(u)
ROWS = {r["id"]: r for r in json.load(open(os.path.join(KB, "kg-knowledge-points.json"), encoding="utf-8"))}


def answer(q, k=10, max_points=6, threshold=0.6):
    hits = u.search(q, k)
    points = [(s, d) for s, d in hits if d["kind"] == "point"]
    if points:
        top = points[0][0]
        kept = [(s, d) for s, d in points if s >= threshold * top][:max_points]
        points = kept or points[:2]
    points = points[:max_points]
    tables = [(s, d) for s, d in hits if d["kind"] == "table"][:1]
    lines, cites = [], []
    for s, d in points:
        r = ROWS[d["id"]]
        first = re.split(r"[。；]", r["definition"])[0].strip()
        points_txt = "；".join([x for x in r["key_points"].split("；") if x][:4])
        lines.append(f"- {first}；{points_txt} [{r['id']}]")
        cites.append(r["id"])
    for s, d in tables:
        lines.append(f"- 表 {d['title']}：{d['text'][:120]} [{d['id']}]")
        cites.append(d["id"])
    return "\n".join(lines), cites


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    a = ap.parse_args()
    text, cites = answer(a.query)
    print(text)
    print("\n引用：", " ".join(cites))


if __name__ == "__main__":
    main()
