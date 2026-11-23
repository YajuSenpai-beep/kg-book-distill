# -*- coding: utf-8 -*-
"""Validate a lightweight KG schema JSON.

Usage:
    python validate_schema.py schema.json [--strict]

Schema format:
{
  "classes": [{"name":"Disease","parent":"","identity":"disease_id","required":["name"]}],
  "relations": [{"name":"has_symptom","domain":"Disease","range":"Symptom","cardinality":"N"}],
  "competency_questions": [{"q":"某疾病的症状有哪些？","path":["Disease","has_symptom","Symptom"]}]
}
"""
import argparse, json, sys
from collections import defaultdict

CARDINALITIES = {"1", "1..N", "N", "M..N", "0..1", "0..N"}


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def validate(s):
    errors, warnings = [], []
    classes = s.get("classes", [])
    relations = s.get("relations", [])
    cqs = s.get("competency_questions", [])

    names = {}
    for c in classes:
        n = c.get("name", "").strip()
        if not n:
            errors.append("存在空类名")
            continue
        if n in names:
            errors.append(f"重复类名：{n}")
        names[n] = c
    for c in classes:
        p = c.get("parent", "").strip()
        if p and p not in names:
            errors.append(f"{c['name']}: 父类不存在 {p}")
        if not c.get("identity", "").strip():
            errors.append(f"{c['name']}: 缺少身份规则 identity")
        if not c.get("required"):
            warnings.append(f"{c['name']}: 未定义必填属性")

    # parent cycles
    for n, c in names.items():
        seen, cur = set(), n
        while cur and cur in names:
            if cur in seen:
                errors.append(f"父类存在环：{n}")
                break
            seen.add(cur)
            cur = names[cur].get("parent", "").strip()

    rel_names = set()
    used = set()
    for r in relations:
        n = r.get("name", "").strip()
        if not n:
            errors.append("存在空关系名")
            continue
        if n in rel_names:
            errors.append(f"重复关系名：{n}")
        rel_names.add(n)
        d, rg = r.get("domain", "").strip(), r.get("range", "").strip()
        if d not in names:
            errors.append(f"{n}: domain 不存在 {d}")
        if rg not in names:
            errors.append(f"{n}: range 不存在 {rg}")
        used.update([d, rg])
        card = str(r.get("cardinality", "N"))
        if card not in CARDINALITIES:
            errors.append(f"{n}: 非法基数 {card}（允许 {sorted(CARDINALITIES)}）")

    for c in classes:
        n = c.get("name")
        is_parent = any(x.get("parent") == n for x in classes)
        if n not in used and not is_parent:
            warnings.append(f"{n}: 孤立类（未被关系使用，也不是父类）")

    for i, q in enumerate(cqs, 1):
        path = q.get("path", [])
        if len(path) != 3:
            errors.append(f"CQ{i}: path 必须是 [类, 关系, 类]")
            continue
        a, r, b = path
        if a not in names or b not in names:
            errors.append(f"CQ{i}: 类不存在 {a}/{b}")
        if r not in rel_names:
            errors.append(f"CQ{i}: 关系不存在 {r}")
        else:
            rel = next(x for x in relations if x["name"] == r)
            if rel.get("domain") != a or rel.get("range") != b:
                errors.append(f"CQ{i}: 与关系 domain/range 不一致（{a}-{r}-{b}）")

    return errors, warnings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("schema")
    ap.add_argument("--strict", action="store_true", help="把 warning 也视为失败")
    a = ap.parse_args()
    errors, warnings = validate(load(a.schema))
    for w in warnings:
        print("WARN", w)
    for e in errors:
        print("ERROR", e)
    print(f"classes/relations/CQs: {len(load(a.schema).get('classes', []))}/"
          f"{len(load(a.schema).get('relations', []))}/{len(load(a.schema).get('competency_questions', []))}")
    print(f"errors={len(errors)} warnings={len(warnings)}")
    sys.exit(1 if errors or (a.strict and warnings) else 0)


if __name__ == "__main__":
    main()
