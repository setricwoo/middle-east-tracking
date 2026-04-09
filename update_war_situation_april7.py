#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""更新war-situation.html为4月7日报告"""

import json
import re

# 4月7日报告数据
report_data = {
    "title": "Iran Update Special Report, April 7, 2026",
    "title_zh": "伊朗局势更新特别报告 - 2026年4月7日",
    "date": "2026-04-07",
    "url": "https://understandingwar.org/research/middle-east/iran-update-special-report-april-7-2026/",
    "takeaways": [
        {
            "en": "The United States and Iran agreed to a two-week ceasefire brokered by Pakistan on April 7 and will begin negotiations in Islamabad, Pakistan, on April 11. The Iranian Supreme National Security Council announced that the regime agreed to the ceasefire on April 7, several hours after US President Donald Trump announced that he had agreed to the ceasefire on the condition that Iran reopen the Strait of Hormuz.",
            "zh": "【美伊达成两周停火协议】美国和伊朗于4月7日在巴基斯坦斡旋下达成两周停火协议，将于4月11日在巴基斯坦伊斯兰堡开始谈判。伊朗最高国家安全委员会宣布，该政权于4月7日同意停火。伊朗外交部长阿巴斯·阿拉格齐确认伊朗接受停火，并表示伊朗将在两周内允许船只'安全通行'霍尔木兹海峡。"
        },
        {
            "en": "Israel has reportedly agreed to cease operations against Iran and Hezbollah if Iran halts its operations in the Strait of Hormuz. Pakistani Prime Minister Shehbaz Sharif posted on X on April 7 that Iran and the United States' allies have agreed to an immediate ceasefire 'everywhere, including [in] Lebanon and elsewhere.'",
            "zh": "【以色列同意停火条件】据报道，如果伊朗停止在霍尔木兹海峡的行动，以色列已同意停止针对伊朗和真主党的行动。巴基斯坦总理谢赫巴兹·谢里夫4月7日在X平台上发帖称，伊朗和美国的盟友已同意'立即在所有地方停火，包括黎巴嫩和其他地方'。"
        },
        {
            "en": "Combined force strikes on Iranian railways and roads may have cut off several Iranian lines of transportation to move weapons, including missiles and missile launchers or components, across Iran. The IDF struck eight rail bridges and road segments that the Iranian regime uses to move weapons and other military equipment.",
            "zh": "【联军打击伊朗交通线】联军对伊朗铁路和公路的打击可能切断了伊朗用于运输武器（包括导弹和导弹发射器或部件）的多条交通线。以色列国防军打击了伊朗政权用于运输武器和其他军事设备的八座铁路桥和公路路段。"
        },
        {
            "en": "Russia may be helping Iran conduct attacks on international shipping in the Strait of Hormuz by providing Iran with satellite imagery of the strait. Reuters reported on April 7 that Russian satellites are 'actively surveying' the Strait of Hormuz, according to Ukrainian intelligence.",
            "zh": "【俄罗斯协助伊朗】俄罗斯可能通过向伊朗提供霍尔木兹海峡的卫星图像，帮助伊朗对国际航运进行攻击。据路透社4月7日报道，根据乌克兰情报，俄罗斯卫星正在'积极勘测'霍尔木兹海峡。自战争开始以来，俄罗斯已向伊朗提供了美国、海湾国家和土耳其在中东军事资产的卫星图像，以帮助伊朗实施攻击。"
        },
        {
            "en": "Islamic Revolutionary Guards Corps (IRGC) Commander Brigadier General Ahmad Vahidi and Khatam ol Anbia Central Headquarters Commander Ali Abdollahi Aliabadi are reportedly driving decisions related to Iran's kinetic response to the US and Israeli air campaign.",
            "zh": "【伊朗军方决策者】据4月7日反政权媒体报道，伊斯兰革命卫队(IRGC)司令艾哈迈德·瓦希迪准将和哈塔姆·奥尔·安比亚中央总部司令阿里·阿卜杜拉希·阿里阿巴迪正在主导伊朗对美国和以色列空中战役的动能反应相关决策。"
        }
    ],
    "charts": [
        {
            "url": "https://understandingwar.org/wp-content/uploads/2026/04/US-and-Israeli-Strikes-on-Iran-Evening-April-7-2026-scaled.webp",
            "title_zh": "美以联军在伊朗的打击（4月7日晚）",
            "context": [
                "美以联军4月7日晚间在伊朗境内的打击目标",
                "打击伊朗铁路和公路基础设施",
                "切断伊朗武器运输线路"
            ]
        },
        {
            "url": "https://understandingwar.org/wp-content/uploads/2026/04/Iranian-Retalitory-Strikes-in-the-Middle-East-April-7-2026-scaled.webp",
            "title_zh": "伊朗在中东的报复性打击（4月7日）",
            "context": [
                "2026年4月7日伊朗对中东地区的报复性打击",
                "伊朗导弹和无人机攻击",
                "针对美国盟友的打击"
            ]
        },
        {
            "url": "https://understandingwar.org/wp-content/uploads/2026/04/Israeli-Strikes-in-Iran-Targeting-Railway-Infrastructure-April-7-2026.webp",
            "title_zh": "以军打击伊朗铁路基础设施（4月7日）",
            "context": [
                "以色列国防军打击伊朗铁路桥",
                "切断伊朗武器运输线路",
                "八座铁路桥成为目标"
            ]
        },
        {
            "url": "https://understandingwar.org/wp-content/uploads/2026/04/Israeli-Strikes-in-Iran-Targeting-Road-Infrastructure-April-7-2026.webp",
            "title_zh": "以军打击伊朗公路基础设施（4月7日）",
            "context": [
                "以色列国防军打击伊朗公路路段",
                "阻断军事装备运输",
                "战略交通线成为目标"
            ]
        },
        {
            "url": "https://understandingwar.org/wp-content/uploads/2026/04/NEW-Iranian-Launches-at-KSA-March-1-April-7-FINAL-1024x768.webp",
            "title_zh": "伊朗对沙特的发射（3月1日-4月7日）",
            "context": [
                "2026年3月1日至4月7日期间伊朗对沙特发射",
                "弹道导弹、巡航导弹和无人机",
                "沙特持续遭受伊朗攻击"
            ]
        },
        {
            "url": "https://understandingwar.org/wp-content/uploads/2026/04/NEW-Iranian-Launches-at-Kuwait-February-28-April-7-FINAL-1024x768.webp",
            "title_zh": "伊朗对科威特的发射（2月28日-4月7日）",
            "context": [
                "2月28日至4月7日期间伊朗对科威特发射",
                "伊朗向科威特发射多枚巡航导弹",
                "科威特持续遭受伊朗攻击"
            ]
        },
        {
            "url": "https://understandingwar.org/wp-content/uploads/2026/04/NEW-Iranian-Launches-at-Bahrain-Feb-28-Apr-7-FINAL-1024x768.webp",
            "title_zh": "伊朗对巴林的发射（2月28日-4月7日）",
            "context": [
                "2月28日至4月7日期间伊朗对巴林发射",
                "伊朗无人机击中巴林多个设施",
                "巴林持续遭受伊朗攻击"
            ]
        },
        {
            "url": "https://understandingwar.org/wp-content/uploads/2026/04/NEW-Iranian-Launches-at-the-UAE-April-7-FINAL-1024x768.webp",
            "title_zh": "伊朗对阿联酋的发射（4月7日）",
            "context": [
                "伊朗4月7日对阿联酋发射",
                "针对阿联酋能源基础设施",
                "拦截碎片引发火灾"
            ]
        },
        {
            "url": "https://understandingwar.org/wp-content/uploads/2026/04/Lebanon-CoT-LH-Attacks-April-7-2026.webp",
            "title_zh": "黎巴嫩冲突态势 - 真主党攻击（4月7日）",
            "context": [
                "真主党在黎巴嫩南部的军事行动",
                "4月7日真主党对以色列的攻击",
                "黎巴嫩战线最新态势"
            ]
        },
        {
            "url": "https://understandingwar.org/wp-content/uploads/2026/04/Hezbollah-Claimed-Attacks-in-Northern-Israel-Total-March-3-April-6-FINAL-1024x768.webp",
            "title_zh": "真主党对以色列北部声称袭击总数（3月3日-4月6日）",
            "context": [
                "真主党3月3日至4月6日对以色列北部攻击总数",
                "火箭弹、无人机和导弹攻击",
                "真主党持续攻击以色列北部"
            ]
        },
        {
            "url": "https://understandingwar.org/wp-content/uploads/2026/04/Hezbollah-Claimed-Attacks-by-Type-March-3-April-6-FINAL-1024x768.webp",
            "title_zh": "真主党声称攻击按类型统计（3月3日-4月6日）",
            "context": [
                "真主党攻击类型分类统计",
                "包括反坦克导弹、火箭弹、无人机等",
                "攻击手段多样化"
            ]
        }
    ],
    "history": [
        {"date": "2026-04-07", "title": "Iran Update Special Report, April 7, 2026", "url": "https://understandingwar.org/research/middle-east/iran-update-special-report-april-7-2026/"},
        {"date": "2026-04-05", "title": "Iran Update Special Report, April 5, 2026", "url": "https://understandingwar.org/research/middle-east/iran-update-special-report-april-5-2026/"},
        {"date": "2026-04-04", "title": "Iran Update Special Report, April 4, 2026", "url": "https://understandingwar.org/research/middle-east/iran-update-special-report-april-4-2026/"},
        {"date": "2026-04-03", "title": "Iran Update Special Report, April 3, 2026", "url": "https://understandingwar.org/research/middle-east/iran-update-special-report-april-3-2026/"},
        {"date": "2026-04-02", "title": "Iran Update Special Report, April 2, 2026", "url": "https://understandingwar.org/research/middle-east/iran-update-special-report-april-2-2026/"}
    ]
}

# 读取现有HTML
with open('war-situation.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 更新日期
html = re.sub(
    r'date": "2026-04-05"',
    f'date": "2026-04-07"',
    html
)

# 更新标题
html = re.sub(
    r'"title": "Iran Update Special Report, April 5, 2026"',
    f'"title": "{report_data["title"]}"',
    html
)

# 更新title_zh
html = re.sub(
    r'"title_zh": "伊朗局势更新特别报告 - 2026年4月5日"',
    f'"title_zh": "{report_data["title_zh"]}"',
    html
)

# 替换Key Takeaways
import json
new_takeaways_json = json.dumps(report_data["takeaways"], ensure_ascii=False, indent=4)
html = re.sub(
    r'"takeaways": \[[\s\S]*?\],\s*"charts"',
    f'"takeaways": {new_takeaways_json},\n    "charts"',
    html
)

# 替换图表
new_charts_json = json.dumps(report_data["charts"], ensure_ascii=False, indent=4)
html = re.sub(
    r'"charts": \[[\s\S]*?\]\s*},\s*"history"',
    f'"charts": {new_charts_json}\n  }},\n  "history"',
    html
)

# 替换历史记录
new_history_json = json.dumps(report_data["history"], ensure_ascii=False, indent=2)
html = re.sub(
    r'"history": \[[\s\S]*?\]\s*};',
    f'"history": {new_history_json}\n}};',
    html
)

# 更新updated时间
html = re.sub(
    r'"updated": "2026-04-05[\d:T]+"',
    f'"updated": "2026-04-08T01:00:00"',
    html
)

# 保存更新后的HTML
with open('war-situation.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("war-situation.html updated to April 7 report")
print("Date: 2026-04-07")
print(f"Key Takeaways: {len(report_data['takeaways'])}")
print(f"Charts: {len(report_data['charts'])}")
