# -*- coding: utf-8 -*-
"""
RGX-military-entrepreneur · 政策数据层
数据源：《退役军人就业创业促进条例》(国务院令第840号, 2026-08-01施行)、
退役军人部发〔2022〕77号、财税2023-14号、深圳《支持军创企业高质量发展实施办法》等。
口径均为报告口径，申报以税务/人社/退役军人事务/承办银行当期答复为准。

本层是匹配引擎的数据源。字段说明：
  name        政策/补贴名称
  stage       生命周期阶段 (1开办入驻/2税务首年/3融资扩能力/4带岗规模化/5品牌大赛)
  identity    适的身份: ['veteran'] 或 ['veteran','general']
  entity      适的企业形态: ['个体','一人公司','小微']
  region      适的地域: ['龙华','福田','全市','全国']
  dept        申报部门
  amount_general   普通创业者可拿额度/顶格值（元，None=无现金/不适用）
  amount_veteran   退役军人可拿额度/顶格值（元，None=无现金/不适用）
  materials      申报材料
  window       申报窗口/期限
  note       备注

单位：元（人民币）。amount 为 None 表示该项非现金补贴（如贷款、资质、场地）。
"""

POLICY = [
    # ── 阶段① 开办·入驻 ───────────────────────────────────────────
    {
        "name": "一次性创业补贴",
        "stage": 1,
        "identity": ["veteran", "general"],
        "entity": ["个体", "一人公司", "小微"],
        "region": ["全市", "龙华", "福田"],
        "dept": "人社部门",
        "amount_general": 10000,
        "amount_veteran": 15000,
        "materials": ["退役证/转业证", "营业执照", "正常经营满6个月佐证"],
        "window": "经营满6个月后申报",
        "note": "退役军人顶格最高1.5万（普适0.5–1万）；首次创办；1.5万可覆盖新智洗车智能体车体成本约1万。",
    },
    {
        "name": "创业场租补贴（军创孵化载体）",
        "stage": 1,
        "identity": ["veteran", "general"],
        "entity": ["个体", "一人公司", "小微"],
        "region": ["龙华", "福田", "全市"],
        "dept": "退役军人事务部门 / 园区运营方",
        "amount_general": None,
        "amount_veteran": None,
        "materials": ["退役证", "入驻孵化载体证明", "场地租赁合同"],
        "window": "入驻即享，最长3年；福田场租补贴最高1560元/月",
        "note": "近零成本卡位；市、区两级载体优先军创；福田顶格1560/月。",
    },
    {
        "name": "OPC 创业工位补贴（按月·3年）",
        "stage": 1,
        "identity": ["veteran", "general"],
        "entity": ["个体", "一人公司", "小微"],
        "region": ["全国", "全市", "龙华", "福田"],
        "dept": "所在街道/园区 OPC 基地",
        "amount_general": 30000,
        "amount_veteran": 36600,
        "materials": ["OPC 入驻协议", "退职证件", "每月一次考勤打卡记录"],
        "window": "每月发放，3年；军人/大学生 1560/1200/900，普通 1200/900/700",
        "note": "退役军人/大学生 3 年合计 72000 元（1560/1200/900 × 各12月），普通 3 年合计 30000 元（1200/900/700）。车辆本身可认定为 OPC 创业工位。",
    },
    {
        "name": "免反担保资格（贷款铺底）",
        "stage": 1,
        "identity": ["veteran"],
        "entity": ["个体", "一人公司", "小微"],
        "region": ["全国", "全市", "龙华", "福田"],
        "dept": "退役军人事务部门 + 承办银行",
        "amount_general": None,
        "amount_veteran": None,
        "materials": ["退役证", "创业项目说明"],
        "window": "身份审核通过后名单推送承办银行",
        "note": "退役军人专属，普通创业者无此项。",
    },

    # ── 阶段② 税务·首年 ───────────────────────────────────────────
    {
        "name": "个体经营顶格税费扣减（财税2023-14）",
        "stage": 2,
        "identity": ["veteran", "general"],
        "entity": ["个体"],
        "region": ["全国", "全市", "龙华", "福田"],
        "dept": "主管税务机关",
        "amount_general": 20000,   # 每户每年限额（基础）
        "amount_veteran": 24000,   # 顶格上浮20%后，粤/沪/豫均顶格执行
        "materials": ["退役证/转业证", "税务登记信息"],
        "window": "自个体工商户登记当月起 3年(36个月)内；政策至2027年底",
        "note": "依次扣减增值税/城建税/教育附加/地方教育附加/个税；扣不完不结转；退役军人可顶格2.4万/年。",
    },
    {
        "name": "普惠叠加（研发加计/小微减免/留抵退税）",
        "stage": 2,
        "identity": ["veteran", "general"],
        "entity": ["个体", "一人公司", "小微"],
        "region": ["全国", "全市", "龙华", "福田"],
        "dept": "主管税务机关",
        "amount_general": None,
        "amount_veteran": None,
        "materials": ["研发费用凭证", "小微企业认定材料"],
        "window": "年度汇算/留抵退税周期",
        "note": "与专项可叠加；一人公司/小微走此通道，不占个体限额。",
    },
    {
        "name": "自主择业军转干部个体经营免税",
        "stage": 2,
        "identity": ["veteran"],
        "entity": ["个体"],
        "region": ["全国", "全市", "龙华", "福田"],
        "dept": "主管税务机关",
        "amount_general": None,
        "amount_veteran": None,
        "materials": ["转业证"],
        "window": "自领取税务登记证起3年内免征增值税和个税",
        "note": "仅限自主择业军转干部身份。",
    },

    # ── 阶段③ 融资·扩能力 ─────────────────────────────────────────
    {
        "name": "退役军人创业贷",
        "stage": 3,
        "identity": ["veteran"],
        "entity": ["个体", "一人公司", "小微"],
        "region": ["全国", "全市", "龙华", "福田"],
        "dept": "承办银行（金融监管总局×退役军人事务部口径）",
        "amount_general": None,
        "amount_veteran": None,
        "materials": ["退役证", "军功荣誉证明（倾斜额度/期限）", "用款需求说明"],
        "window": "经营中随时；利率原则上不高于该行普惠均值",
        "note": "退役军人专属低息贷；军功可倾斜额度期限。",
    },
    {
        "name": "创业担保贷款（贴息·可多次）",
        "stage": 3,
        "identity": ["veteran", "general"],
        "entity": ["个体", "一人公司", "小微"],
        "region": ["全国", "全市", "龙华", "福田"],
        "dept": "人社部门 + 经办银行",
        "amount_general": 300000,
        "amount_veteran": 500000,
        "materials": ["身份证明", "退役证件", "创业项目说明"],
        "window": "个人顶格50万（普通30万起）；小微可至400万；按期还款可累计≤3次；退役军人免反担保+贴息",
        "note": "退役军人免反担保、贴息、多次申请。",
    },
    {
        "name": "地方专属产品（深军贷等）",
        "stage": 3,
        "identity": ["veteran"],
        "entity": ["个体", "一人公司", "小微"],
        "region": ["全市", "龙华", "福田"],
        "dept": "承办银行",
        "amount_general": None,
        "amount_veteran": None,
        "materials": ["退役证", "军创企业认定"],
        "window": "经营中；深圳「深军贷」军创企业版",
        "note": "深圳专属；优化征信画像模型。",
    },

    # ── 阶段④ 带岗·规模化 ─────────────────────────────────────────
    {
        "name": "企业招用退役士兵定额税费扣减",
        "stage": 4,
        "identity": ["veteran", "general"],
        "entity": ["一人公司", "小微"],
        "region": ["全国", "全市", "龙华", "福田"],
        "dept": "主管税务机关",
        "amount_general": None,
        "amount_veteran": None,
        "materials": ["招用退役士兵劳动合同", "社保缴费凭证"],
        "window": "3年内按实际招用人数定额依次扣减",
        "note": "企业招用自主就业退役士兵适用。",
    },
    {
        "name": "创业带动就业补贴",
        "stage": 4,
        "identity": ["veteran", "general"],
        "entity": ["个体", "一人公司", "小微"],
        "region": ["全市", "龙华", "福田"],
        "dept": "人社部门",
        "amount_general": None,
        "amount_veteran": 30000,
        "materials": ["吸纳就业名单", "社保缴费记录"],
        "window": "吸纳就业并缴社保后申请；按带动人数定档",
        "note": "深圳顶格3万。",
    },

    # ── 阶段⑤ 品牌·大赛 ───────────────────────────────────────────
    {
        "name": "全国退役军人创新创业大赛",
        "stage": 5,
        "identity": ["veteran"],
        "entity": ["个体", "一人公司", "小微"],
        "region": ["全国", "全市", "龙华", "福田"],
        "dept": "退役军人事务部门",
        "amount_general": None,
        "amount_veteran": None,
        "materials": ["军创企业申报书", "项目材料"],
        "window": "面向全国定期举办",
        "note": "获奖军创企业优先享多项政府扶持；一赛解锁后续补贴包。",
    },
]

# 身份类别（决定适哪条专属条款）
IDENTITY_TYPES = {
    "veteran": {
        "label": "退役军人（叠加顶格）",
        "sub": [
            ("自主就业退役士兵", "个体走14号限额；带岗走定额扣减"),
            ("自主择业军转干部", "个体经营3年免增值税+个税"),
            ("其他军创认定退役军人", "专属贷/大赛/免反担保"),
        ],
    },
    "general": {
        "label": "普通创业者（仅普惠层）",
        "sub": [],
    },
}

STAGES = {
    1: "开办·入驻（0–3个月）",
    2: "税务·首年（取得税务登记即享）",
    3: "融资·扩能力（经营中）",
    4: "带岗·规模化（招用阶段）",
    5: "品牌·大赛（全程可投）",
}

ENTITY = ["个体", "一人公司", "小微"]
REGION = ["龙华", "福田", "全市"]


def match(identity="veteran", entity="一人公司", region="龙华", only_available=True):
    """返回匹配的政策清单，并计算退役军人相对普通创业者的顶格提升。"""
    results = []
    for p in POLICY:
        if entity not in p["entity"]:
            continue
        if region not in p["region"]:
            continue
        if identity not in p["identity"]:
            continue
        entry = dict(p)
        entry["get_amount"] = p["amount_general"]
        entry["vet_amount"] = p["amount_veteran"]
        # 顶格提升（仅当身份=veteran 时才有意义）
        entry["lift"] = None
        if identity == "veteran" and p["amount_general"] and p["amount_veteran"] \
                and p["amount_general"] != p["amount_veteran"]:
            entry["lift"] = p["amount_veteran"] - p["amount_general"]
        results.append(entry)
    return results


def veteran_total_boost(entity="一人公司", region="龙华"):
    """可量化顶格提升合计（仅含现金型且退役军人>普通者）。"""
    total = 0
    for p in match(identity="veteran", entity=entity, region=region):
        if p["lift"]:
            total += p["lift"]
    return total
