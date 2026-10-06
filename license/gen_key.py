#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RGX License 生成工具（仅作者 / admin 使用）。

用法：
    python gen_key.py --email buyer@x.com --tier team --seats 5 --days 365

可选：
    --admin-secret XXX   管理员密钥（必须与服务端 ADMIN_SECRET 一致）
    --store PATH         指定 store 文件路径

结果写入 store/licenses.json（该文件已被 .gitignore 忽略，切勿提交真实数据）。
"""
import argparse
import json
import os
import secrets
import time

DEFAULT_STORE = os.path.join(os.path.dirname(__file__), "store", "licenses.json")
TIERS = ("personal", "team", "enterprise", "lifetime")


def load(path):
    if os.path.exists(path):
        return json.load(open(path, encoding="utf-8"))
    return {"secret": secrets.token_hex(32), "admin_secret": "changeme-admin", "keys": {}}


def save(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    json.dump(data, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--email", required=True, help="购买者邮箱")
    ap.add_argument("--tier", default="personal", choices=TIERS)
    ap.add_argument("--seats", type=int, default=1, help="允许设备数")
    ap.add_argument("--days", type=int, default=365, help="有效期(天)")
    ap.add_argument("--admin-secret", default="changeme-admin")
    ap.add_argument("--store", default=DEFAULT_STORE)
    a = ap.parse_args()

    store = load(a.store)
    if a.admin_secret != store.get("admin_secret", "changeme-admin"):
        print("错误：管理员密钥不匹配")
        return

    key = "RGX-" + secrets.token_urlsafe(16).upper().replace("_", "").replace("-", "")[:20]
    store["keys"][key] = {
        "email": a.email.strip(),
        "tier": a.tier,
        "seats": a.seats,
        "days": a.days,
        "expire_at": int(time.time()) + a.days * 86400,
        "created_at": int(time.time()),
        "activations": [],
        "revoked": False,
    }
    save(a.store, store)
    print(f"已生成 license：{key}")
    print(f"  邮箱：{a.email}  套餐：{a.tier}  设备数：{a.seats}  有效期：{a.days} 天")


if __name__ == "__main__":
    main()
