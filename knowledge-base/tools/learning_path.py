# -*- coding: utf-8 -*-
"""Generate a prerequisite learning path for a target point or topic.

Usage:
    python -I tools/learning_path.py --target B-02-03-13
    python -I tools/learning_path.py --topic "TransR"
    python -I tools/learning_path.py --topic "知识图谱问答" --json
"""
import argparse, json, os, re, sys

BASE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.dirname(BASE)
ROWS = json.load(open(os.path.join(KB, "kg-knowledge-points.json"), encoding="utf-8"))
BY = {r["id"]: r for r in ROWS}


def find_id(topic):
    t = topic.lower()
    exact = [r for r in ROWS if r["title"].lower() == t]
    if exact:
        return exact[0]["id"]
    starts = [r for r in ROWS if r["title"].lower().startswith(t)]
    if starts:
        return starts[0]["id"]
    contains = [r for r in ROWS if t in (r["title"] + " " + r["definition"]).lower()]
    return contains[0]["id"] if contains else None


def ancestors(target):
    seen, order = set(), []

    def dfs(nid):
        if nid in seen:
            return
        seen.add(nid)
        for pre in [x for x in BY[nid]["prerequisites"].split("；") if x]:
            if pre in BY:
                dfs(pre)
        order.append(nid)

    dfs(target)
    return order


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target")
    ap.add_argument("--topic")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--known", default="", help="已掌握 ID，逗号分隔")
    ap.add_argument("--max-steps", type=int, default=0)
    ap.add_argument("--minutes", type=int, default=15, help="每步预计分钟")
    ap.add_argument("--md", default="", help="输出 Markdown 文件")
    a = ap.parse_args()
    tid = a.target or (find_id(a.topic) if a.topic else None)
    if not tid or tid not in BY:
        sys.exit("target/topic not found")
    path = ancestors(tid)
    known = {x.strip() for x in a.known.split(",") if x.strip()}
    path = [x for x in path if x not in known]
    if a.max_steps and len(path) > a.max_steps:
        # keep early foundations plus the last N-3 steps
        path = path[:3] + path[-(a.max_steps - 3):]
    if a.json:
        print(json.dumps([{"id": x, "title": BY[x]["title"], "page": BY[x]["page"],
                           "section": BY[x]["section"], "type": BY[x]["type"]}
                          for x in path], ensure_ascii=False, indent=2))
        return
    print(f"学习路径：{BY[tid]['title']}（{len(path)} 步）\n")
    for i, x in enumerate(path, 1):
        r = BY[x]
        print(f"{i:02d}. {r['title']}  [{r['id']}]  p.{r['page']}  {r['section']}")
    print(f"\n预计：{len(path) * a.minutes} 分钟（每步 {a.minutes} 分钟）")
    print("说明：按 prerequisites 拓扑排序；不是课程设计，只是最小前置链。")
    if a.md:
        lines = [f"# 学习路径：{BY[tid]['title']}\n",
                 "| # | 知识点 | ID | 页 | 类型 | 范围 |", "|---:|---|---|---|---|---|"]
        for i, x in enumerate(path, 1):
            r = BY[x]
            lines.append(f"| {i} | {r['title']} | {r['id']} | {r['page']} | {r['type']} | {r['scope']} |")
        open(a.md, "w", encoding="utf-8").write("\n".join(lines))


if __name__ == "__main__":
    main()
