# RGX License Server · 部署与集成说明

> 这是一套**零依赖**的授权校验骨架，用来防止技能被白嫖复制。纯 Python 标准库，无需 `pip install`，复制即用。

## 目录结构

```
license/
├── server.py              # 授权校验服务端（零依赖 http.server）
├── gen_key.py             # 作者签发 license 的工具
├── verify.py              # 客户端校验示例（演示如何嵌入技能入口）
├── store/
│   ├── licenses.example.json   # 配置模板（占位）
│   └── licenses.json           # 真实数据（已被 .gitignore 忽略，勿提交）
└── LICENSE_SERVER.md      # 本文件
```

## 1. 快速开始（本地试跑）

```bash
cd license
python server.py                 # 默认监听 :8000

# 另开一个终端，签发一个测试 license：
python gen_key.py --email test@x.com --tier team --seats 5 --days 30
# 输出类似：已生成 license：RGX-XXXX...

# 客户端校验演示（先把 SERVER 改成你的地址）：
RGX_LICENSE_SERVER=http://127.0.0.1:8000 python verify.py
```

## 2. 接口说明

| 方法 | 路径 | 入参 | 返回 |
|---|---|---|---|
| GET | `/healthz` | — | `{"ok":true}` |
| POST | `/api/keys` | `admin_secret, email, tier, seats, days` | `{"key":"RGX-..."}` |
| POST | `/api/activate` | `key, email, machine_id` | `{"status":"valid",...}` |
| POST | `/api/verify` | `key, machine_id` | `{"status":"valid",...}` |
| POST | `/api/revoke` | `admin_secret, key` | `{"ok":true}` |

`status` 取值：`valid` / `invalid` / `expired` / `seat_full` / `mismatch` / `forbidden`

## 3. 嵌入技能入口（防白嫖核心）

在 `skills/RGX/SKILL.md` 的「首次对话」流程里加一步：调用 `verify.py` 的 `verify_or_prompt()`。
- 未授权 → 引导用户输入 license key（购买后你发给他）
- 授权成功 → 写 `~/.RGX/license.json`，之后静默校验、离线容忍
- 过期 / 超设备 / 被吊销 → 拦截并提示续费

安装脚本 `install.sh` / `install.ps1` 可顺带把 `verify.py` 复制到技能目录，并在安装末尾提示「输入 license key 完成激活」。

## 4. 部署到公网（让别人能激活）

任选其一：
- **Railway / Render / Fly.io**：上传 `server.py`，设环境变量 `PORT`（平台给的）、`ADMIN_SECRET`（强随机）、`STORE`（用挂载卷，别用临时目录）
- **自有 VPS**：`gunicorn` 或 `nohup python server.py &`，前置 `nginx` + 免费 HTTPS（certbot）

部署后，把 `verify.py` 顶部的 `RGX_LICENSE_SERVER` 默认值改成你的公网地址（或让用户用环境变量覆盖）。

## 5. 安全与防白嫖要点

- ✅ **真实 secret / admin_secret 只在服务端**，客户端只持有随机 `RGX-XXXX` key，无法反推伪造
- ✅ 每个 key 绑定 **邮箱 + 设备数 + 有效期**；激活时登记 `machine_id`，超设备数拒绝
- ✅ 支持**吊销**（用户退款/违规时调用 `/api/revoke`）
- ⚠️ `store/licenses.json` 含全部真实数据，**已写入 .gitignore，切勿提交到公开仓库**
- ⚠️ 生产务必把 `ADMIN_SECRET` 改成强随机值，并加 HTTPS

## 6. 生产升级建议

- 用 SQLite / Postgres 替换 JSON 文件存储（多人并发更稳）
- 接支付回调（微信支付 / Stripe）：用户付款成功自动调用 `/api/keys` 发 key，免去人工
- 加 API 限流、IP 风控、用量统计、key 轮换
- 可加密客户端缓存 `~/.RGX/license.json`，进一步防本地篡改

---
作者：张文昊（昊哥）｜ tuoxiaoxiai-del
