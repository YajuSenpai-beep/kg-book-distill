# -*- coding: utf-8 -*-
import csv, glob, json, os, unittest

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KB = os.path.join(BASE, "kg-knowledge-points.json")
CSV = os.path.join(BASE, "kg-knowledge-points.csv")
OBS = os.path.join(BASE, "obsidian")


class TestKnowledgeBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = json.load(open(KB, encoding="utf-8"))
        cls.byid = {r["id"]: r for r in cls.rows}

    def test_count(self):
        self.assertGreater(len(self.rows), 0)

    def test_unique_ids_titles(self):
        self.assertEqual(len(self.byid), len(self.rows))
        self.assertEqual(len({r["title"] for r in self.rows}), len(self.rows))

    def test_required_fields(self):
        for r in self.rows:
            for k in ("id", "book", "chapter", "section", "title", "type", "definition",
                      "page", "skill_module", "coverage", "scope", "canonical_id"):
                self.assertTrue(str(r[k]).strip(), f"{r.get('id')} missing {k}")

    def test_canonical(self):
        for r in self.rows:
            self.assertIn(r["canonical_id"], self.byid)
            if r["canonical_id"] != r["id"]:
                self.assertEqual(self.byid[r["canonical_id"]]["canonical_id"],
                                 r["canonical_id"])

    def test_scope(self):
        allowed = {"KG核心", "KG专项", "KG邻接", "背景"}
        for r in self.rows:
            self.assertIn(r["scope"], allowed)

    def test_csv(self):
        rows = list(csv.reader(open(CSV, encoding="utf-8-sig")))
        self.assertEqual(len(rows), len(self.rows) + 1)
        self.assertEqual(len(rows[0]), 18)

    def test_obsidian_notes(self):
        notes = glob.glob(os.path.join(OBS, "10-知识点", "*.md"))
        self.assertEqual(len(notes), len(self.rows))

    def test_canvas(self):
        canvas = json.load(open(os.path.join(OBS, "知识图谱总览.canvas"), encoding="utf-8"))
        self.assertGreaterEqual(len(canvas["nodes"]), 20)
        self.assertGreaterEqual(len(canvas["edges"]), 19)

    def test_application_cards(self):
        rows = list(csv.reader(open(os.path.join(BASE, "anki", "kg-application-cards.csv"),
                                    encoding="utf-8-sig")))
        self.assertGreaterEqual(len(rows) - 1, 100)

    def test_obsidian_links(self):
        files = glob.glob(os.path.join(OBS, "**", "*.md"), recursive=True)
        names = {os.path.splitext(os.path.basename(p))[0] for p in files}
        import re
        for p in files:
            with open(p, encoding="utf-8") as f:
                text = f.read()
            for target in re.findall(r"\[\[([^\]]+)\]\]", text):
                t = target.split("|")[0].split("#")[0].strip()
                self.assertIn(t, names, f"broken link {t} in {p}")


if __name__ == "__main__":
    unittest.main()
