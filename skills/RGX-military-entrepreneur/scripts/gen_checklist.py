#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""RGX-military-entrepreneur · 申报清单生成器（申报智能体产物）
按生命周期五阶段生成「申报清单 + 材料清单 + 进度提醒 + 申报窗口」，
导出 Markdown / HTML。
用法：python gen_checklist.py --identity veteran --entity 一人公司 --region 龙华 [--html]
"""
import sys, os, argparse, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import policy_data as pd


def _money(v):
    if v is None:
        return "—"
    return f"{v/10000:.1f}万" if v >= 10000 else f"{v}元"


def build_md(identity="veteran", entity="一人公司", region="龙华"):
    matches = pd.match(identity=identity, entity=entity, region=region)
    by_stage = {}
    for m in matches:
        by_stage.setdefault(m["stage"], []).append(m)

    today = datetime.date.today().isoformat()
    id_label = pd.IDENTITY_TYPES[identity]["label"]

    L = []
    L.append(f"# 军创申报清单 · {entity} @ {region}")
    L.append("")
    L.append(f"> 身份：{id_label} ｜ 生成日期：{today}")
    L.append("> 口径为报告值，申报以税务/人社/退役军人事务/承办银行当期答复为准。")
    L.append("")

    for s in sorted(by_stage):
        L.append(f"## 阶段{s} ｜ {pd.STAGES[s]}")
        L.append("")
        for m in by_stage[s]:
            get, vet, lift = _money(m["get_amount"]), _money(m["vet_amount"]), m.get("lift")
            L.append(f"### 申报项：{m['name']}")
            L.append(f"- 向谁报：{m['dept']}")
            if lift:
                L.append(f"- 顶格可拿：退役军人 {vet}（普通 {get}，**多拿 {lift/10000:.1f}万**）" if identity == "veteran"
                         else f"- 可拿：{get}")
            elif identity == "veteran" and vet in ("—", None):
                L.append(f"- 属性：{m['note']}")
            else:
                raw = m["vet_amount"] if identity == "veteran" else m["get_amount"]
                L.append(f"- 可拿：{_money(raw)}")
            L.append(f"- 材料：{'、'.join(m['materials'])}")
            L.append(f"- 进度提醒 / 窗口：{m['window']}")
            L.append(f"- 备注：{m['note']}")
            L.append("")

    L.append("---")
    L.append("## 申报顺序建议")
    L.append("")
    L.append("1. 先做 **免反担保资格**（阶段①），给后续贷款铺底；")
    L.append("2. 入驻后立刻报 **一次性创业补贴**（满6个月）+ **场租补贴**；")
    L.append("3. 税务登记即报 **顶格税费扣减**（个体）或 **普惠叠加**（公司/小微）；")
    L.append("4. 经营中申请 **退役军人创业贷 / 创业担保贷款**；")
    L.append("5. 招用员工报 **带岗补贴 + 定额扣减**；")
    L.append("6. 全程投 **全国退役军人创新创业大赛**，获奖解锁后续补贴包。")
    L.append("")
    return "\n".join(L)


def build_html(identity="veteran", entity="一人公司", region="龙华"):
    md = build_md(identity, entity, region)
    try:
        import markdown
        body = markdown.markdown(md, extensions=["tables", "fenced_code"])
    except Exception:
        body = "<pre>" + md + "</pre>"
    css = """
@page { size: A4; margin: 16mm; }
body { font-family:"Microsoft YaHei","PingFang SC",sans-serif; color:#1a1a1a;
       line-height:1.6; font-size:11pt; }
h1 { color:#0b3d2e; border-bottom:3px solid #0b3d2e; padding-bottom:6px; }
h2 { color:#0b3d2e; border-left:5px solid #0b3d2e; padding-left:9px; margin-top:20px; }
h3 { color:#14532d; }
blockquote { border-left:4px solid #d4a373; background:#faf6f0; padding:8px 14px;
             color:#5b4a3a; font-size:10pt; }
table { border-collapse:collapse; width:100%; font-size:9.5pt; }
th,td { border:1px solid #cdd8d0; padding:6px 8px; }
th { background:#0b3d2e; color:#fff; }
tr:nth-child(even) td { background:#f3f7f4; }
li { margin:3px 0; }
strong { color:#0b3d2e; }
"""
    return (f'<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">'
            f"<style>{css}</style></head><body>{body}</body></html>")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--identity", default="veteran", choices=["veteran", "general"])
    ap.add_argument("--entity", default="一人公司", choices=pd.ENTITY)
    ap.add_argument("--region", default="龙华", choices=pd.REGION)
    ap.add_argument("--html", action="store_true")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    content = build_html(a.identity, a.entity, a.region) if a.html else build_md(a.identity, a.entity, a.region)
    if a.out:
        open(a.out, "w", encoding="utf-8").write(content)
        print("written:", a.out)
    else:
        print(content)
