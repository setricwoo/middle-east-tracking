#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新 supply-chain.json，添加最新的能源设施和供应链事件
"""

import json
from datetime import datetime

# 读取现有数据
with open(r'D:\python_code\海湾以来-最新\supply-chain.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 新的能源基础设施事件（按日期倒序）
new_energy = [
    {
        "date": "2026-04-06",
        "region": "伊朗",
        "facility": "南帕尔斯石化厂(Asaluyeh)",
        "type": "石化设施",
        "owner": "伊朗国家石化公司",
        "event": "以色列袭击伊朗南帕尔斯天然气田的Asaluyeh石化设施，这是伊朗最大的石化设施，占全国石化产量的50%。结合上周对Mahshahr石化综合体的袭击，两个设施占伊朗石化出口的85%已被摧毁",
        "status": "严重损毁",
        "impact": "伊朗最大石化设施，占全国石化产量50%，石化出口85%被摧毁",
        "source": "AP News/Haaretz/WSJ"
    },
    {
        "date": "2026-04-06",
        "region": "伊朗",
        "facility": "Asaluyeh综合公用设施(Mobin/Damavand)",
        "type": "公用事业设施",
        "owner": "Mobin/Damavand",
        "event": "空袭针对Asaluyeh综合体的公用事业供应商Mobin和Damavand，它们为多个石化厂提供水、电和氧气，导致依赖设施被迫关闭或减产",
        "status": "严重受损",
        "impact": "影响多个石化厂的供电、供水和供氧，甲醇等化工厂关闭",
        "source": "ICIS"
    },
    {
        "date": "2026-04-06",
        "region": "沙特阿拉伯",
        "facility": "沙特东部能源设施",
        "type": "能源设施",
        "owner": "沙特阿美",
        "event": "沙特国防部表示拦截了7枚射向东部地区的弹道导弹，碎片落在能源设施附近，正在评估损失",
        "status": "受损评估中",
        "impact": "沙特东部主要能源设施",
        "source": "Jerusalem Post"
    },
    {
        "date": "2026-04-06",
        "region": "卡塔尔",
        "facility": "Ras Laffan LNG出口终端",
        "type": "LNG出口终端",
        "owner": "卡塔尔能源公司",
        "event": "两艘载有卡塔尔LNG的油轮(Rasheeda和Al Daayen)在抵达霍尔木兹海峡前返航，这是自战争开始以来首次尝试出口LNG",
        "status": "出口受阻",
        "impact": "卡塔尔17%的LNG出口能力此前已受损，现出口尝试受阻",
        "source": "MarineLink/Bloomberg"
    },
    {
        "date": "2026-04-05",
        "region": "阿联酋/阿布扎比",
        "facility": "Borouge石化厂",
        "type": "石化厂",
        "owner": "Borouge(阿布扎比国家石油公司与北欧化工合资)",
        "event": "阿布扎比Ruwais的大型石化工厂在袭击后发生多处火灾，被迫暂停运营。火灾由防空拦截碎片引起，造成1名埃及籍居民死亡，4人受伤",
        "status": "暂停运营",
        "impact": "阿布扎比重要石化工厂",
        "source": "Bloomberg"
    },
    {
        "date": "2026-04-05",
        "region": "科威特",
        "facility": "Shuwaikh石油综合体/Mina al-Ahmadi炼油厂",
        "type": "石油综合体/炼油厂",
        "owner": "科威特石油公司",
        "event": "伊朗无人机袭击了科威特Shuwaikh石油综合体，造成火灾。该设施容纳石油部和科威特石油公司总部。Mina al-Ahmadi炼油厂和两个发电及海水淡化厂也遭袭击",
        "status": "受损",
        "impact": "科威特最大炼油厂及石油总部",
        "source": "Reuters/Jerusalem Post"
    }
]

# 新的产业链影响事件（按日期倒序）
new_chain = [
    {
        "date": "2026-04-06",
        "region": "全球",
        "company": "Emirates Global Aluminium (EGA)/Alba",
        "industry": "铝业",
        "event": "阿联酋全球铝业(EGA)的Al Taweelah工厂遭伊朗导弹和无人机袭击后，可能需要长达一年时间才能恢复全面生产。巴林Alba冶炼厂已宣布所有发货的不可抗力。霍尔木兹海峡关闭使全球约9%的原铝供应被困",
        "transmission": "供应中断/不可抗力",
        "scale": "EGA全面恢复需12个月，Alba宣布不可抗力，全球9%原铝供应被困",
        "chinaImpact": "LME铝价突破3500美元/吨，下游汽车/建筑/包装成本上升",
        "recovery": "EGA恢复需12个月",
        "source": "FinancialContent/Seeking Alpha"
    },
    {
        "date": "2026-04-05",
        "region": "全球",
        "company": "全球化肥产业",
        "industry": "化肥",
        "event": "阿联酋负责约30%全球化肥（硝酸钾和磷肥）供应的生产设施和基础设施受损。以色列化肥价格已飙升180%。每年约1600万吨化肥通过霍尔木兹海峡运输",
        "transmission": "供应中断/价格上涨",
        "scale": "全球化肥供应紧张，以色列化肥价格飙升180%",
        "chinaImpact": "农民生产成本上升，食品价格上涨；美国农业部预测2026年食品价格可能上涨6.1%",
        "recovery": "视设施恢复",
        "source": "FAO/Ynetnews"
    },
    {
        "date": "2026-04-06",
        "region": "印度",
        "company": "印度LPG进口",
        "industry": "LPG/天然气",
        "event": "两艘印度籍LPG油轮(Green Asha和Green Sanvi)已离开海湾。印度作为全球第二大LPG进口国，正经历数十年来最严重的天然气短缺，政府已削减工业用气供应",
        "transmission": "供应短缺",
        "scale": "印度工业用气供应被削减",
        "chinaImpact": "全球LPG市场供应紧张",
        "recovery": "视进口恢复",
        "source": "Reuters"
    },
    {
        "date": "2026-04-06",
        "region": "伊朗/全球",
        "company": "伊朗甲醇及其他石化企业",
        "industry": "石化/甲醇",
        "event": "Asaluyeh综合体的公用设施遭袭导致多个甲醇工厂关闭或减产。袭击针对供电、供水和供氧设施，影响整个石化产业链",
        "transmission": "停产/减产",
        "scale": "多个甲醇工厂关闭或减产",
        "chinaImpact": "甲醇供应收缩，下游甲醛/醋酸成本飙升",
        "recovery": "视公用设施恢复",
        "source": "ICIS"
    }
]

# 去重函数：检查是否已存在相同设施+日期的事件
def is_duplicate(existing_list, new_item, key_fields):
    for existing in existing_list:
        match = True
        for field in key_fields:
            if existing.get(field) != new_item.get(field):
                match = False
                break
        if match:
            return True
    return False

# 能源数据去重并合并
energy_keys = ['date', 'facility']
for item in new_energy:
    if not is_duplicate(data['energy'], item, energy_keys):
        data['energy'].insert(0, item)

# 产业链数据去重并合并
chain_keys = ['date', 'company', 'event']
for item in new_chain:
    # 简化去重逻辑，只检查日期和公司
    is_dup = False
    for existing in data['chain']:
        if existing.get('date') == item.get('date') and existing.get('company') == item.get('company'):
            is_dup = True
            break
    if not is_dup:
        data['chain'].insert(0, item)

# 更新 fetchTime
data['fetchTime'] = datetime.now().isoformat()

# 保存更新后的数据
with open(r'D:\python_code\海湾以来-最新\supply-chain.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"更新完成！")
print(f"能源设施损毁: 原有 {len(data['energy']) - len(new_energy)} 条, 新增 {len([x for x in new_energy if not is_duplicate(data['energy'][len(new_energy):], x, energy_keys)])} 条")
print(f"产业链影响: 原有 {len(data['chain']) - len(new_chain)} 条, 新增 {len(new_chain)} 条")
