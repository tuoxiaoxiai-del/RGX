#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""RGX-military-entrepreneur · 顶格匹配器
输入：主体身份 + 企业形态 + 所在地 → 输出「可申报清单 + 顶格值 + 退役军人叠加提升」
用法：python match.py --identity veteran --entity 一人公司 --region 龙华 [--json]
"""
import sys, os, json, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import policy_data as pd


def fmt_amount(v):
    if v is None:
        return "（非现金）"
    return f"{v/10000:.1f}万" if v >= 10000 else f"{v}元"


def run(identity="veteran", entity="一人公司", region="龙华", as_json=False):
    matches = pd.match(identity=identity, entity=entity, region=region)
    lines = []
    lines.append("=" * 60)
    lines.append(f"顶格匹配器 · {pd.IDENTITY_TYPES[identity]['label']}")
    lines.append(f"企业形态：{entity} ｜ 所在地：{region}")
    lines.append("=" * 60)

    by_stage = {}
    for m in matches:
        by_stage.setdefault(m["stage"], []).append(m)

    total_vet = 0
    total_gen = 0
    for s in sorted(by_stage):
        lines.append(f"\n## 阶段{pd.STAGES[s]}")
        for m in by_stage[s]:
            get = fmt_amount(m["get_amount"])
            vet = fmt_amount(m["vet_amount"])
            lift = m.get("lift")
            if lift:
                total_vet += m["vet_amount"]
                total_gen += m["get_amount"]
                lines.append(f"  • {m['name']}")
                lines.append(f"      可拿：退役军人 {vet}（普通 {get}，顶格 +{fmt_amount(lift)}）")
            else:
                amt = fmt_amount(m["vet_amount"] if identity == "veteran" else m["get_amount"])
                lines.append(f"  • {m['name']}　{amt}")
            lines.append(f"      向谁报：{m['dept']}")
            lines.append(f"      材料：{'、'.join(m['materials'])}")
            lines.append(f"      窗口：{m['window']}")

    lines.append("\n" + "=" * 60)
    lines.append("汇总")
    lines.append("=" * 60)
    if identity == "veteran" and total_vet:
        lines.append(f"退役军人可量化现金补贴合计（顶格）：约 {fmt_amount(total_vet)}")
        lines.append(f"普通创业者合计：约 {fmt_amount(total_gen)}")
        diff = total_vet - total_gen
        if total_gen:
            lines.append(f"退役军人顶格多拿：约 {fmt_amount(diff)}（{diff/total_gen*100:.0f}%）")
    else:
        lines.append("本配置下无可量化现金补贴差异（多为贷款/资质/场地类）")
    lines.append("\n⚠ 口径为报告值，申报以税务/人社/退役军人事务/承办银行当期答复为准。")

    out = "\n".join(lines)
    if as_json:
        data = {
            "identity": identity, "entity": entity, "region": region,
            "matches": [
                {"name": m["name"], "stage": m["stage"], "dept": m["dept"],
                 "materials": m["materials"], "window": m["window"],
                 "get_amount": m["get_amount"], "vet_amount": m["vet_amount"],
                 "lift": m.get("lift")}
                for m in matches
            ],
            "veteran_cash_total": total_vet if identity == "veteran" else None,
            "general_cash_total": total_gen if identity == "veteran" else None,
        }
        return json.dumps(data, ensure_ascii=False, indent=2)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--identity", default="veteran", choices=["veteran", "general"])
    ap.add_argument("--entity", default="一人公司", choices=pd.ENTITY)
    ap.add_argument("--region", default="龙华", choices=pd.REGION)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    print(run(a.identity, a.entity, a.region, a.json))
