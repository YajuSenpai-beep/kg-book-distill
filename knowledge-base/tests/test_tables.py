# -*- coding: utf-8 -*-
import json, os, unittest
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TABLES = os.path.join(BASE, "tables", "table-data.json")
FIGS = os.path.join(BASE, "figures", "figure-index.json")


class TestTables(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tables = json.load(open(TABLES, encoding="utf-8"))["tables"]
        cls.figs = {f["id"]: f for f in json.load(open(FIGS, encoding="utf-8"))}

    def test_count_and_ids(self):
        tables_in_figs = [f for f in self.figs.values() if f["kind"] == "表"]
        self.assertEqual(len(self.tables), len(tables_in_figs))
        self.assertEqual(len({t["id"] for t in self.tables}), len(self.tables))
        self.assertEqual(sum(Counter(t.get("status") for t in self.tables).values()), len(self.tables))

    def test_structure(self):
        for t in self.tables:
            self.assertIn(t["id"], self.figs)
            self.assertEqual(self.figs[t["id"]]["kind"], "表")
            self.assertEqual(t["page"], self.figs[t["id"]]["page"])
            for row in t["rows"]:
                self.assertEqual(len(row), len(t["columns"]))
                if t.get("status") in ("matrix", "key_value"):
                    for i in t["numeric_columns"]:
                        float(row[i])

    def test_rendered(self):
        for name in ("tables.md", "table-index.csv", "table-validation.md"):
            path = os.path.join(BASE, "tables", name)
            self.assertTrue(os.path.exists(path))
            self.assertGreater(os.path.getsize(path), 100)


if __name__ == "__main__":
    unittest.main()
