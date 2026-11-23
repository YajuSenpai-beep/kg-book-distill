# -*- coding: utf-8 -*-
import json, os, unittest

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(BASE, "instances", "instance-graph.json")
REL = {"solves", "evaluated_on", "reports_metric", "mentions_dataset", "mentions_metric", "variant_of", "improves", "uses"}


class TestInstances(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g = json.load(open(PATH, encoding="utf-8"))
        cls.nodes = {n["id"]: n for n in cls.g["nodes"]}

    def test_counts(self):
        self.assertEqual(len(self.g["nodes"]), 118)
        self.assertEqual(len(self.g["edges"]), 176)
        self.assertEqual(sum(1 for n in self.g["nodes"] if n["type"] == "Method"), 64)
        self.assertEqual(sum(1 for n in self.g["nodes"] if n["type"] == "Task"), 18)

    def test_edges(self):
        for e in self.g["edges"]:
            self.assertIn(e["source"], self.nodes)
            self.assertIn(e["target"], self.nodes)
            self.assertIn(e["type"], REL)
            self.assertNotEqual(e["source"], e["target"])

    def test_unresolved(self):
        self.assertEqual(self.g["meta"]["unresolved_methods"], [])


if __name__ == "__main__":
    unittest.main()
