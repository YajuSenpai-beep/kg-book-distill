# -*- coding: utf-8 -*-
"""Zero-dependency graph API + static web UI.

Run:
    python -I service/graph_service.py --port 8765
Then open http://127.0.0.1:8765/

Endpoints:
  GET /api/stats
  GET /api/search?q=TransE
  GET /api/node/<id>
  GET /api/neighbors/<id>
  GET /api/path?from=M-TransE&to=DS-FB15K
"""
import argparse, json, os, posixpath, re, time, importlib.util
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote, urlparse

BASE = os.path.dirname(os.path.abspath(__file__))
KB = os.path.dirname(BASE)
WEB = os.path.join(BASE, "web")
DATA = json.load(open(os.path.join(KB, "instances", "instance-graph.json"), encoding="utf-8"))
spec = importlib.util.spec_from_file_location("unified", os.path.join(KB, "search", "unified_search.py"))
U = importlib.util.module_from_spec(spec)
spec.loader.exec_module(U)
DOCS = {d["id"]: d for d in U.DOCS}
NODES = {n["id"]: n for n in DATA["nodes"]}
OUT = {}
IN = {}
for e in DATA["edges"]:
    OUT.setdefault(e["source"], []).append(e)
    IN.setdefault(e["target"], []).append(e)


TOKEN = None
CACHE = {}
RATE = {}
CACHE_TTL = 60
RATE_LIMIT = 120


def stats():
    from collections import Counter
    return {"nodes": len(NODES), "edges": len(DATA["edges"]), "docs": len(DOCS),
            "node_types": dict(Counter(n["type"] for n in NODES.values())),
            "edge_types": dict(Counter(e["type"] for e in DATA["edges"]))}


def node_detail(nid):
    n = NODES.get(nid)
    if not n and nid in DOCS:
        d = DOCS[nid]
        return {"node": {"id": d["id"], "type": d["kind"], "label": d["title"],
                          "book": d["book"], "page": d["page"]},
                "out": [], "in": [], "neighbors": {}}
    if not n:
        return None
    return {"node": n, "out": OUT.get(nid, []), "in": IN.get(nid, []),
            "neighbors": {e["target"]: NODES.get(e["target"], {}).get("label", e["target"])
                          for e in OUT.get(nid, [])} |
                         {e["source"]: NODES.get(e["source"], {}).get("label", e["source"])
                          for e in IN.get(nid, [])}}


def search(q, limit=20, kind=None):
    if U is not None:
        return [d for _, d in U.search(q, limit, kind)]
    ql = q.lower()
    hits = []
    for n in NODES.values():
        label = n["label"].lower()
        if ql in label or ql in n["id"].lower():
            hits.append((0 if label.startswith(ql) else 1, len(label), n))
    hits.sort(key=lambda x: (x[0], x[1]))
    return [n for _, _, n in hits[:limit]]


def path(a, b, max_depth=5):
    if a not in NODES or b not in NODES:
        return None
    q = deque([(a, [a])])
    seen = {a}
    while q:
        cur, p = q.popleft()
        if cur == b:
            return p
        if len(p) > max_depth:
            continue
        nxt = [e["target"] for e in OUT.get(cur, [])] + [e["source"] for e in IN.get(cur, [])]
        for v in nxt:
            if v not in seen:
                seen.add(v)
                q.append((v, p + [v]))
    return None


class Handler(BaseHTTPRequestHandler):
    def _json(self, obj, code=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _file(self, path):
        if not os.path.isfile(path):
            self.send_error(404)
            return
        ct = {"html": "text/html; charset=utf-8", "js": "application/javascript; charset=utf-8",
              "css": "text/css; charset=utf-8", "json": "application/json; charset=utf-8"}.get(
                  path.rsplit(".", 1)[-1], "application/octet-stream")
        body = open(path, "rb").read()
        self.send_response(200)
        self.send_header("Content-Type", ct)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        p = unquote(u.path)
        if p == "/healthz":
            return self._json({"ok": True})
        ip = self.client_address[0] if hasattr(self, "client_address") else "?"
        now = time.time()
        win = RATE.setdefault(ip, [now, 0])
        if now - win[0] > 60:
            win[0], win[1] = now, 0
        win[1] += 1
        if win[1] > RATE_LIMIT:
            return self._json({"error": "rate limited"}, 429)
        if TOKEN and p.startswith("/api/"):
            qs = parse_qs(u.query)
            supplied = qs.get("token", [""])[0] or self.headers.get("Authorization", "").replace("Bearer ", "")
            if supplied != TOKEN:
                return self._json({"error": "unauthorized"}, 401)
        if p.startswith("/api/"):
            if p == "/api/stats":
                return self._json(stats())
            if p == "/api/search":
                qs = parse_qs(u.query)
                q = qs.get("q", [""])[0]
                kind = qs.get("kind", [None])[0]
                limit = int(qs.get("limit", ["20"])[0])
                offset = int(qs.get("offset", ["0"])[0])
                key = (q, kind, limit, offset)
                now = time.time()
                if key in CACHE and now - CACHE[key][0] < CACHE_TTL:
                    return self._json(CACHE[key][1])
                res = search(q, limit + offset, kind)[offset:]
                payload = {"q": q, "offset": offset, "results": res}
                CACHE[key] = (now, payload)
                if len(CACHE) > 500:
                    CACHE.clear()
                return self._json(payload)
            if p.startswith("/api/node/"):
                d = node_detail(p.split("/")[-1])
                return self._json(d or {"error": "not found"}, 200 if d else 404)
            if p.startswith("/api/neighbors/"):
                d = node_detail(p.split("/")[-1])
                return self._json(d["neighbors"] if d else {"error": "not found"})
            if p == "/api/path":
                qs = parse_qs(u.query)
                a, b = qs.get("from", [""])[0], qs.get("to", [""])[0]
                r = path(a, b)
                return self._json({"from": a, "to": b, "path": r})
            return self._json({"error": "unknown endpoint"}, 404)
        if p in ("/", ""):
            p = "/index.html"
        target = os.path.abspath(os.path.join(WEB, p.lstrip("/")))
        if not target.startswith(os.path.abspath(WEB)):
            return self.send_error(403)
        return self._file(target)

    def log_message(self, fmt, *args):
        return


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--token", default=None, help="可选 Bearer token")
    a = ap.parse_args()
    global TOKEN
    TOKEN = a.token
    print(f"http://{a.host}:{a.port}/  (Ctrl+C to stop)")
    ThreadingHTTPServer((a.host, a.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
