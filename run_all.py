# -*- coding: utf-8 -*-
"""One-command rebuild.

Default: rebuild everything from the already extracted text (fast).
--from-pdf: re-run extraction/OCR first (slow; needs the original PDFs).
--check: run the 30-point final consistency check at the end.

Usage:
    python -I run_all.py
    python -I run_all.py --from-pdf
    python -I run_all.py --check
"""
import argparse, os, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
KB = os.path.join(ROOT, "knowledge-base")
PY = sys.executable


def run(name, args):
    print(f"\n== {name} ==")
    r = subprocess.run([PY, "-I"] + args, cwd=ROOT)
    if r.returncode != 0:
        sys.exit(f"FAILED: {name} (exit {r.returncode})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from-pdf", action="store_true", help="re-extract/OCR before rebuilding")
    ap.add_argument("--check", action="store_true", help="run audit/final_check.py at the end")
    ap.add_argument("--with-vector", action="store_true", help="rebuild BGE + unified index")
    ap.add_argument("--with-multimodal", action="store_true", help="render pages + CLIP index")
    ap.add_argument("--with-llm", action="store_true", help="generate answers with auto LLM provider")
    a = ap.parse_args()

    if a.from_pdf:
        run("extract book A", ["work/extract_book_a.py"])
        run("OCR book B", ["work/ocr_book_b.py"])
        run("assemble book B", ["work/assemble_book_b.py"])

    run("build knowledge base", ["knowledge-base/build_kb.py"])
    run("build exports", ["knowledge-base/build_exports.py"])
    run("build figure index", ["knowledge-base/figures/build_figure_index.py"])
    run("build table data", ["knowledge-base/tables/build_table_data.py"])
    run("validate tables", ["knowledge-base/tables/build_tables.py"])
    run("build graph", ["knowledge-base/graph/build_graph.py"])
    run("build instances", ["knowledge-base/instances/build_instances.py"])
    run("build glossary", ["knowledge-base/glossary/build_glossary.py"])
    run("answer context eval", ["knowledge-base/eval/eval_answer_context.py"])
    run("formula audit", ["knowledge-base/audit/formula_audit.py"])
    run("number audit", ["knowledge-base/audit/number_audit.py"])
    run("coverage audit", ["knowledge-base/audit/coverage_audit.py"])
    run("tests", ["-m", "unittest", "discover", "-s", "knowledge-base/tests"])

    if a.with_vector:
        embed = os.path.join(ROOT, ".venv-embed", "Scripts", "python.exe")
        if os.path.exists(embed):
            run("vector index", ["knowledge-base/search/kg_vector_search.py", "重建索引", "--rebuild"])
            r = subprocess.run([embed, "-I", "knowledge-base/search/unified_search.py", "索引", "--limit", "1"],
                               cwd=ROOT)
            if r.returncode != 0:
                print("unified vector index skipped/failed")
            r = subprocess.run([embed, "-I", "knowledge-base/eval/eval_unified_answer.py"], cwd=ROOT)
            if r.returncode != 0:
                print("unified answer eval skipped/failed")
            r = subprocess.run([embed, "-I", "knowledge-base/eval/eval_answer_quality.py"], cwd=ROOT)
            if r.returncode != 0:
                print("answer quality eval skipped/failed")
        else:
            print("skip vector index: .venv-embed/Scripts/python.exe not found")

    if a.with_llm:
        run("generate answers", ["knowledge-base/llm/generate_answers.py"])
        run("eval generated", ["knowledge-base/llm/eval_generated.py"])

    if a.with_multimodal:
        renderer = os.path.join(KB, "figures", "render_pages.py")
        if os.path.exists(renderer):
            run("render figure pages", ["knowledge-base/figures/render_pages.py"])
        else:
            print("skip page rendering: render_pages.py is not included in the public package")
        embed = os.path.join(ROOT, ".venv-embed", "Scripts", "python.exe")
        if os.path.exists(embed):
            r = subprocess.run([embed, "-I", "knowledge-base/figures/build_multimodal.py"], cwd=ROOT)
            if r.returncode != 0:
                print("multimodal index skipped/failed")
        else:
            print("skip multimodal index: .venv-embed not found")

    if a.check:
        run("final check", ["knowledge-base/audit/final_check.py"])
    print("\nDONE")


if __name__ == "__main__":
    main()
