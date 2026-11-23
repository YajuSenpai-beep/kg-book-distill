# -*- coding: utf-8 -*-
import json, os, unittest

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAPH = os.path.join(BASE, "graph")
REL_TYPES = {"part_of", "in_section", "prerequisite_of", "related_to",
             "variant_of", "improves", "illustrates", "evaluated_on",
             "reports_metric", "mentions_dataset", "mentions_metric",
             "canonical_of"}


class TestGraph(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.g = json.load(open(os.path.join(GRAPH, "kg-graph.json"), encoding="utf-8"))
        cls.nodes = {n["id"]: n for n in cls.g["nodes"]}

    def test_counts(self):
        self.assertGreater(len(self.g["nodes"]), 0)
        self.assertGreater(len(self.g["edges"]), 0)
        kb = json.load(open(os.path.join(BASE, "kg-knowledge-points.json"), encoding="utf-8"))
        figs = json.load(open(os.path.join(BASE, "figures", "figure-index.json"), encoding="utf-8"))
        self.assertEqual(sum(1 for n in self.g["nodes"] if n["type"] == "KnowledgePoint"), len(kb))
        self.assertEqual(sum(1 for n in self.g["nodes"] if n["type"] in ("Figure", "Table")), len(figs))

    def test_endpoints_and_types(self):
        for e in self.g["edges"]:
            self.assertIn(e["source"], self.nodes)
            self.assertIn(e["target"], self.nodes)
            self.assertIn(e["type"], REL_TYPES)
            self.assertNotEqual(e["source"], e["target"])

    def test_key_relations(self):
        by_type = {}
        for e in self.g["edges"]:
            by_type[e["type"]] = by_type.get(e["type"], 0) + 1
        self.assertGreater(by_type["prerequisite_of"], 0)
        self.assertGreater(by_type["variant_of"], 0)
        self.assertGreater(by_type["improves"], 0)
        figs = json.load(open(os.path.join(BASE, "figures", "figure-index.json"), encoding="utf-8"))
        self.assertEqual(by_type["illustrates"], sum(len(f.get("illustrates", [])) for f in figs))

    def test_exports(self):
        for name in ("kg-graph.graphml", "kg-graph.ttl", "graph-report.md"):
            path = os.path.join(GRAPH, name)
            self.assertTrue(os.path.exists(path), name)
            self.assertGreater(os.path.getsize(path), 100, name)


if __name__ == "__main__":
    unittest.main()
