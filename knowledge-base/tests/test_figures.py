# -*- coding: utf-8 -*-
import json, os, unittest

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGS = os.path.join(BASE, "figures", "figure-index.json")
KB = os.path.join(BASE, "kg-knowledge-points.json")


class TestFigures(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.figs = json.load(open(FIGS, encoding="utf-8"))
        cls.ids = {r["id"] for r in json.load(open(KB, encoding="utf-8"))}

    def test_counts(self):
        self.assertGreater(len(self.figs), 0)
        self.assertEqual(sum(1 for f in self.figs if f["kind"] == "图")
                         + sum(1 for f in self.figs if f["kind"] == "表"), len(self.figs))

    def test_unique_ids(self):
        self.assertEqual(len({f["id"] for f in self.figs}), len(self.figs))

    def test_fields_and_links(self):
        for f in self.figs:
            for k in ("id", "book", "chapter", "kind", "number", "caption",
                      "page", "section", "role", "linked_points", "note_status"):
                self.assertIn(k, f)
            for pid in f["linked_points"]:
                self.assertIn(pid, self.ids, f"{f['id']} links missing {pid}")

    def test_illustrates(self):
        ill = [f for f in self.figs if f.get("illustrates")]
        self.assertGreater(len(ill), 0)
        self.assertGreater(sum(len(f["illustrates"]) for f in ill), 0)
        for f in ill:
            for pid in f["illustrates"]:
                self.assertIn(pid, self.ids, f"{f['id']} illustrates missing {pid}")

    def test_obsidian_index(self):
        path = os.path.join(BASE, "obsidian", "40-图表索引.md")
        self.assertTrue(os.path.exists(path))
        self.assertGreater(os.path.getsize(path), 1000)


if __name__ == "__main__":
    unittest.main()
