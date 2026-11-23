# -*- coding: utf-8 -*-
import importlib.util, os, unittest

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location(
    "graph_service", os.path.join(BASE, "service", "graph_service.py"))
svc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(svc)


class TestService(unittest.TestCase):
    def test_stats(self):
        s = svc.stats()
        self.assertEqual(s["nodes"], 118)
        self.assertEqual(s["edges"], 176)

    def test_search(self):
        hits = svc.search("TransE")
        self.assertEqual(hits[0]["id"], "M-TransE")

    def test_path(self):
        self.assertEqual(svc.path("M-TransE", "DS-FB15K"), ["M-TransE", "DS-FB15K"])

    def test_detail(self):
        d = svc.node_detail("M-TransE")
        self.assertEqual(d["node"]["label"], "TransE")
        self.assertGreater(len(d["out"]) + len(d["in"]), 0)


if __name__ == "__main__":
    unittest.main()
