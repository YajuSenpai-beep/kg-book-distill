# -*- coding: utf-8 -*-
import importlib.util, os, unittest

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestCitation(unittest.TestCase):
    def test_prune_caps_and_inline(self):
        cc = load("cc", os.path.join(BASE, "llm", "citation_check.py"))
        ans = "甲结论 [A-1]；乙结论 [A-2]；丙结论 [A-3]"
        ctx = {"A-1": "甲结论 的原文", "A-2": "乙结论 的原文", "A-3": "丙结论 的原文"}
        text, kept, dropped = cc.prune(ans, ["A-1", "A-2", "A-3", "A-4"], ctx, 0.0, 2)
        self.assertEqual(len(kept), 2)
        self.assertTrue(set(kept).issubset({"A-1", "A-2", "A-3"}))
        self.assertIn(("A-4", "not inline"), dropped)

    def test_variants_glossary(self):
        mq = load("mq", os.path.join(BASE, "search", "multi_query.py"))
        vs = mq.variants("知识图谱怎么存")
        self.assertGreater(len(vs), 1)
        self.assertTrue(any("knowledge graph" in v for v in vs))

    def test_public_script_exists(self):
        self.assertTrue(os.path.exists(os.path.join(BASE, "..", "tools", "make_public.py")))


if __name__ == "__main__":
    unittest.main()
