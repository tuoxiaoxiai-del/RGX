#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""RGX 客户端 license 校验示例 —— 演示如何嵌入技能入口。

集成方式：
    在 RGX 总入口 SKILL.md 的「首次对话」流程里调用 verify_or_prompt()，
    未授权时引导用户输入 key；授权后写 ~/.RGX/license.json，之后静默校验。

环境变量：
    RGX_LICENSE_SERVER  授权服务端地址（部署后替换占位值）

说明：
    - 离线容忍：本地已有缓存且服务器连不上时，放行并标记 cached
    - machine_id 跨平台取稳定指纹（Windows MachineGuid / macOS IOPlatformUUID / 否则 hostname）
"""
import json
import os
import platform
import subprocess
import sys
import urllib.error
import urllib.request

SERVER = os.environ.get("RGX_LICENSE_SERVER", "https://your-server.example.com")
CACHE = os.path.expanduser("~/.RGX/license.json")


def machine_id():
    if sys.platform == "win32":
        try:
            import winreg

            with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography"
            ) as k:
                return winreg.QueryValueEx(k, "MachineGuid")[0]
        except Exception:
            pass
    if sys.platform == "darwin":
        try:
            out = subprocess.check_output(
                ["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"]
            ).decode()
            for line in out.splitlines():
                if "IOPlatformUUID" in line:
                    return line.split('"')[3]
        except Exception:
            pass
    return platform.node()


def _post(path, payload, timeout=10):
    req = urllib.request.Request(
        SERVER + path,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def verify_or_prompt(email=None, interactive=True):
    mid = machine_id()

    # 1) 已有缓存 -> 静默校验（断网容忍）
    if os.path.exists(CACHE):
        try:
            c = json.load(open(CACHE, encoding="utf-8"))
            res = _post("/api/verify", {"key": c["key"], "machine_id": mid})
            if res.get("status") == "valid":
                return res
        except (urllib.error.URLError, Exception):
            return {"status": "valid", "cached": True}

    if not interactive:
        raise SystemExit("未授权：缺少有效 license")

    # 2) 引导输入 key
    key = input("请输入你的 RGX License Key：").strip()
    if not key:
        raise SystemExit("未授权：未提供 key")
    if email is None:
        email = input("注册邮箱：").strip()
    try:
        res = _post("/api/activate", {"key": key, "email": email, "machine_id": mid})
    except urllib.error.URLError:
        raise SystemExit("无法连接授权服务器，请检查网络")
    if res.get("status") == "valid":
        os.makedirs(os.path.dirname(CACHE), exist_ok=True)
        json.dump({"key": key, "machine_id": mid}, open(CACHE, "w", encoding="utf-8"))
        return res
    raise SystemExit("许可证无效：" + res.get("status", "unknown"))


if __name__ == "__main__":
    print(verify_or_prompt())
