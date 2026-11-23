# -*- coding: utf-8 -*-
import importlib.util, json, os, sys, unittest

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE, "llm"))
spec = importlib.util.spec_from_file_location("client", os.path.join(BASE, "llm", "client.py"))
client = importlib.util.module_from_spec(spec)
spec.loader.exec_module(client)


class TestLLM(unittest.TestCase):
    def test_extract_json(self):
        self.assertEqual(client.extract_json('{"a": 1}')["a"], 1)
        self.assertEqual(client.extract_json('```json\n{"a": 2}\n```')["a"], 2)
        self.assertIsNone(client.extract_json("not json"))

    def test_mock(self):
        c = client.Client("mock")
        obj = json.loads(c.generate("hello"))
        self.assertTrue(obj["insufficient"])
        self.assertEqual(obj["citations"], [])

    def test_providers_configured(self):
        for p in ("anthropic", "deepseek", "qwen", "glm", "moonshot", "ollama"):
            self.assertIn(p, client.PROVIDERS)


if __name__ == "__main__":
    unittest.main()
