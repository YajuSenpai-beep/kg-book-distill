# -*- coding: utf-8 -*-
"""Smoke-check that decision rules exist in the Skill references.

This checks rule *presence*, not whether an Agent applies them correctly.
For a real backtest, run the Skill on each case and grade the output.

Usage:
    python skill_rule_check.py ../evals/decision-cases.jsonl
"""
import argparse, json, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(BASE)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cases", nargs="?", default=os.path.join(ROOT, "evals", "decision-cases.jsonl"))
    a = ap.parse_args()
    cases = [json.loads(x) for x in open(a.cases, encoding="utf-8") if x.strip()]
    failed = 0
    for c in cases:
        path = os.path.join(ROOT, "references", c["file"])
        if not os.path.exists(path):
            path = os.path.join(ROOT, c["file"])
        text = open(path, encoding="utf-8").read().lower()
        missing = [k for k in c["expected"] if k.lower() not in text]
        if missing:
            failed += 1
            print(f"FAIL {c['id']} {c['q']} -> 缺少 {missing}")
        else:
            print(f"PASS {c['id']} {c['q']}")
    print(f"\n{len(cases)-failed}/{len(cases)} passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
