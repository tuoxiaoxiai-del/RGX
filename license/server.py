#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RGX License Server —— 零依赖授权校验服务端（骨架）。

技术：仅用 Python 标准库（http.server），无需 pip 安装，复制即用。
运行：
    python server.py
环境变量：
    PORT          监听端口，默认 8000
    STORE         存储文件路径，默认 ./store/licenses.json
    ADMIN_SECRET  管理员密钥，用于签发/吊销（生产务必改成强随机值！）

接口：
    GET  /healthz                      健康检查
    POST /api/keys                     {admin_secret, email, tier, seats, days} -> {key}
    POST /api/activate                 {key, email, machine_id} -> {status, tier, expire_at}
    POST /api/verify                   {key, machine_id} -> {status, tier, expire_at}
    POST /api/revoke                   {admin_secret, key} -> {ok}
返回状态：valid / invalid / expired / seat_full / mismatch / forbidden

防白嫖要点：
    - 真实 secret 与 admin_secret 只在服务端，客户端只持有随机 key，无法伪造
    - 每个 key 绑定 邮箱 + 设备数(seats) + 有效期，激活时记录 machine_id
    - 超设备数 / 过期 / 被吊销 -> 拒绝
    - store 文件含真实数据，已写入 .gitignore，切勿提交

生产升级建议：
    - 用真正的数据库（SQLite/Postgres）替换 JSON 文件存储
    - 前置 HTTPS + 反向代理（nginx/caddy），加 API 限流
    - 接支付回调（微信/Stripe）自动签发 key，免去人工
    - 增加 IP 风控、key 轮换、用量统计
"""
import json
import os
import secrets
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

STORE_PATH = os.environ.get(
    "STORE", os.path.join(os.path.dirname(__file__), "store", "licenses.json")
)
ADMIN_SECRET = os.environ.get("ADMIN_SECRET", "changeme-admin")
PORT = int(os.environ.get("PORT", "8000"))


def load_store():
    if not os.path.exists(STORE_PATH):
        return {"secret": secrets.token_hex(32), "admin_secret": ADMIN_SECRET, "keys": {}}
    with open(STORE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_store(s):
    os.makedirs(os.path.dirname(STORE_PATH), exist_ok=True)
    tmp = STORE_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, indent=2)
    os.replace(tmp, STORE_PATH)


def _now():
    return int(time.time())


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if urlparse(self.path).path == "/healthz":
            self._send(200, {"ok": True})
        else:
            self._send(404, {"error": "not found"})

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(n) if n else b"{}"
        try:
            data = json.loads(raw or b"{}")
        except Exception:
            return self._send(400, {"error": "bad json"})
        path = urlparse(self.path).path
        store = load_store()
        if path == "/api/keys":
            return self._send(*self.create_key(store, data))
        if path == "/api/activate":
            return self._send(*self.activate(store, data))
        if path == "/api/verify":
            return self._send(*self.verify(store, data))
        if path == "/api/revoke":
            return self._send(*self.revoke(store, data))
        self._send(404, {"error": "not found"})

    def create_key(self, store, data):
        if data.get("admin_secret") != store.get("admin_secret", ADMIN_SECRET):
            return 403, {"status": "forbidden"}
        email = (data.get("email") or "").strip()
        if not email:
            return 400, {"error": "email required"}
        key = "RGX-" + secrets.token_urlsafe(16).upper().replace("_", "").replace("-", "")[:20]
        days = int(data.get("days", 365))
        store["keys"][key] = {
            "email": email,
            "tier": data.get("tier", "personal"),
            "seats": int(data.get("seats", 1)),
            "days": days,
            "expire_at": _now() + days * 86400,
            "created_at": _now(),
            "activations": [],
            "revoked": False,
        }
        save_store(store)
        return 200, {"key": key, "email": email, "expire_at": store["keys"][key]["expire_at"]}

    def activate(self, store, data):
        key = (data.get("key") or "").strip()
        email = (data.get("email") or "").strip()
        mid = data.get("machine_id", "")
        rec = store["keys"].get(key)
        if not rec or rec.get("revoked"):
            return 200, {"status": "invalid"}
        if email and rec["email"] != email:
            return 200, {"status": "mismatch"}
        if _now() > rec["expire_at"]:
            return 200, {"status": "expired"}
        if mid not in rec["activations"]:
            if len(rec["activations"]) >= rec["seats"]:
                return 200, {"status": "seat_full"}
            rec["activations"].append(mid)
            save_store(store)
        return 200, {"status": "valid", "tier": rec["tier"], "expire_at": rec["expire_at"]}

    def verify(self, store, data):
        key = (data.get("key") or "").strip()
        mid = data.get("machine_id", "")
        rec = store["keys"].get(key)
        if not rec or rec.get("revoked"):
            return 200, {"status": "invalid"}
        if _now() > rec["expire_at"]:
            return 200, {"status": "expired"}
        if mid and mid not in rec["activations"]:
            return 200, {"status": "invalid"}
        return 200, {"status": "valid", "tier": rec["tier"], "expire_at": rec["expire_at"]}

    def revoke(self, store, data):
        if data.get("admin_secret") != store.get("admin_secret", ADMIN_SECRET):
            return 403, {"status": "forbidden"}
        key = (data.get("key") or "").strip()
        if key in store["keys"]:
            store["keys"][key]["revoked"] = True
            save_store(store)
            return 200, {"ok": True}
        return 404, {"error": "key not found"}

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    print(f"RGX License Server -> http://0.0.0.0:{PORT}  (store={STORE_PATH})")
    ThreadingHTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
