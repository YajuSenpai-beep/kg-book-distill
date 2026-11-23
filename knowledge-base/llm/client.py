# -*- coding: utf-8 -*-
"""Minimal provider-agnostic LLM client (stdlib only).

Providers:
  anthropic   ANTHROPIC_API_KEY
  deepseek    DEEPSEEK_API_KEY
  qwen        DASHSCOPE_API_KEY
  glm         ZHIPU_API_KEY
  moonshot    MOONSHOT_API_KEY
  ollama      local http://localhost:11434
  mock        deterministic fallback (no network)

Set KG_LLM_PROVIDER / KG_LLM_MODEL / KG_LLM_BASE_URL to override.
"""
import json, os, re, urllib.request

PROVIDERS = {
    "anthropic": {"url": "https://api.anthropic.com/v1/messages", "model": "claude-sonnet-5-5"},
    "deepseek": {"url": "https://api.deepseek.com/v1/chat/completions", "model": "deepseek-chat"},
    "qwen": {"url": "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
             "model": "qwen-plus"},
    "glm": {"url": "https://open.bigmodel.cn/api/paas/v4/chat/completions", "model": "glm-4-flash"},
    "moonshot": {"url": "https://api.moonshot.cn/v1/chat/completions", "model": "moonshot-v1-8k"},
    "ollama": {"url": "http://localhost:11434/api/chat", "model": "qwen3:8b"},
}


def available():
    if os.environ.get("KG_LLM_PROVIDER"):
        return os.environ["KG_LLM_PROVIDER"]
    for p, key in [("anthropic", "ANTHROPIC_API_KEY"), ("deepseek", "DEEPSEEK_API_KEY"),
                   ("qwen", "DASHSCOPE_API_KEY"), ("glm", "ZHIPU_API_KEY"),
                   ("moonshot", "MOONSHOT_API_KEY")]:
        if os.environ.get(key):
            return p
    try:
        urllib.request.urlopen("http://localhost:11434/api/tags", timeout=1)
        return "ollama"
    except Exception:
        return "mock"


def extract_json(text):
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.M)
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None


class Client:
    def __init__(self, provider=None):
        self.provider = provider or available()
        cfg = PROVIDERS.get(self.provider, {})
        self.url = os.environ.get("KG_LLM_BASE_URL") or cfg.get("url")
        self.model = os.environ.get("KG_LLM_MODEL") or cfg.get("model")

    def generate(self, prompt, temperature=0.1, max_tokens=800):
        if self.provider == "mock":
            return json.dumps({"answer": "", "citations": [], "insufficient": True,
                               "note": "mock provider: no LLM configured"})
        if self.provider == "anthropic":
            body = {"model": self.model, "max_tokens": max_tokens, "temperature": temperature,
                    "messages": [{"role": "user", "content": prompt}]}
            req = urllib.request.Request(self.url, data=json.dumps(body).encode(),
                                         headers={"x-api-key": os.environ["ANTHROPIC_API_KEY"],
                                                  "anthropic-version": "2023-06-01",
                                                  "content-type": "application/json"})
            data = json.loads(urllib.request.urlopen(req, timeout=120).read())
            return data["content"][0]["text"]
        if self.provider == "ollama":
            body = {"model": self.model, "stream": False, "options": {"temperature": temperature},
                    "messages": [{"role": "user", "content": prompt}]}
            req = urllib.request.Request(self.url, data=json.dumps(body).encode(),
                                         headers={"content-type": "application/json"})
            data = json.loads(urllib.request.urlopen(req, timeout=300).read())
            return data["message"]["content"]
        # OpenAI-compatible
        key = {"deepseek": "DEEPSEEK_API_KEY", "qwen": "DASHSCOPE_API_KEY",
               "glm": "ZHIPU_API_KEY", "moonshot": "MOONSHOT_API_KEY"}[self.provider]
        body = {"model": self.model, "temperature": temperature, "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}]}
        req = urllib.request.Request(self.url, data=json.dumps(body).encode(),
                                     headers={"Authorization": f"Bearer {os.environ[key]}",
                                              "content-type": "application/json"})
        data = json.loads(urllib.request.urlopen(req, timeout=120).read())
        return data["choices"][0]["message"]["content"]
