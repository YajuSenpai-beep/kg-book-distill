# -*- coding: utf-8 -*-
import importlib.util, json, os, unittest

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestTools(unittest.TestCase):
    def test_glossary(self):
        terms = json.load(open(os.path.join(BASE, "glossary", "terms.json"), encoding="utf-8"))["terms"]
        self.assertEqual(len(terms), 40)
        self.assertEqual(len({t["term"] for t in terms}), 40)

    def test_learning_path(self):
        lp = load("lp", os.path.join(BASE, "tools", "learning_path.py"))
        path = lp.ancestors("B-02-03-13")
        self.assertGreater(len(path), 1)
        self.assertEqual(path[-1], "B-02-03-13")

    def test_exhibit_search(self):
        es = load("es", os.path.join(BASE, "search", "exhibit_search.py"))
        hits = es.bm25("表2-1", 3)
        self.assertEqual(hits[0][1]["id"], "TAB-B-2-1")


if __name__ == "__main__":
    unittest.main()
