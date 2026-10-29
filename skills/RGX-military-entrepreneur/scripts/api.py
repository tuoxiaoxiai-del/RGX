#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""RGX-military-entrepreneur · SaaS 数据 API
零依赖：把匹配引擎的 JSON 结果输出，供前端/后端对接。
  python api.py --serve  → 起一个只读 HTTP 服务（GET /api/match?identity=&entity=&region=）
  python api.py --identity veteran --entity 一人公司 --region 龙华  → 直接打印 JSON
"""
import sys, os, json, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import policy_data as pd
from match import run

def api(identity="veteran", entity="一人公司", region="龙华"):
    return run(identity=identity, entity=entity, region=region, as_json=True)

def serve(host="127.0.0.1", port=8777):
    from http.server import BaseHTTPRequestHandler, HTTPServer
    from urllib.parse import urlparse, parse_qs
    class H(BaseHTTPRequestHandler):
        def _send(self, code, body):
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body.encode("utf-8"))
        def do_GET(self):
            u = urlparse(self.path)
            if u.path == "/healthz":
                return self._send(200, json.dumps({"ok": True}, ensure_ascii=False))
            if u.path != "/api/match":
                return self._send(404, json.dumps({"error": "not found"}, ensure_ascii=False))
            q = parse_qs(u.query)
            identity = q.get("identity", ["veteran"])[0]
            entity = q.get("entity", ["一人公司"])[0]
            region = q.get("region", ["龙华"])[0]
            if identity not in ("veteran", "general"):
                return self._send(400, json.dumps({"error": "bad identity"}, ensure_ascii=False))
            if entity not in pd.ENTITY:
                return self._send(400, json.dumps({"error": "bad entity", "allowed": pd.ENTITY}, ensure_ascii=False))
            if region not in pd.REGION:
                return self._send(400, json.dumps({"error": "bad region", "allowed": pd.REGION}, ensure_ascii=False))
            return self._send(200, api(identity, entity, region))
        def do_OPTIONS(self):
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "*")
            self.end_headers()
        def log_message(self, *a):
            pass
    HTTPServer((host, port), H).serve_forever()

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--identity", default="veteran", choices=["veteran", "general"])
    ap.add_argument("--entity", default="一人公司", choices=pd.ENTITY)
    ap.add_argument("--region", default="龙华", choices=pd.REGION)
    ap.add_argument("--serve", action="store_true")
    ap.add_argument("--port", type=int, default=8777)
    a = ap.parse_args()
    if a.serve:
        print("serving on http://127.0.0.1:%d/api/match" % a.port)
        serve(port=a.port)
    else:
        print(api(a.identity, a.entity, a.region))
