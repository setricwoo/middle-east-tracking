#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新 war-situation.html 的 ISW 数据 - 2026年4月5日报告
"""

import re
import json

# ISW 2026年4月5日特别报告数据
ISW_DATA = {
    "updated": "2026-04-05T14:00:00",
    "source_url": "https://understandingwar.org/research/middle-east/iran-update-special-report-april-5-2026/",
    "current_report": {
        "url": "https://understandingwar.org/research/middle-east/iran-update-special-report-april-5-2026/",
        "title": "Iran Update Special Report, April 5, 2026",
        "title_zh": "伊朗局势更新特别报告 - 2026年4月5日",
        "date": "2026-04-05",
        "takeaways": [
            {
                "en": "US President Donald Trump appears to have extended the deadline for Iran to stop striking shipping through the Strait of Hormuz to 8:00 PM ET on April 7. Iranian Supreme Leader Mojtaba Khamenei has indicated that Iran will continue to strike shipping through the strait.",
                "zh": "【特朗普延长最后期限】美国总统特朗普已将伊朗停止袭击霍尔木兹海峡航运的最后期限延长至美国东部时间4月7日晚8:00。但伊朗最高领袖穆杰塔巴·哈梅内伊表示将继续袭击海峡航运。"
            },
            {
                "en": "US Central Command confirmed that US forces completed the recovery of two F-15E aircrew on April 4 after Iranian air defenses shot down the F-15E on April 2.",
                "zh": "【F-15E机组人员获救】美国中央司令部确认，美军于4月4日完成了对两名F-15E机组人员的救援行动（该机于4月2日被伊朗击落）。武器系统操作员在躲避抓捕36小时后幸存，受重伤，目前正在科威特接受治疗。"
            },
            {
                "en": "US forces successfully established temporary airfields near major Iranian cities, evacuated all personnel, and the combined force continues to strike Iranian targets.",
                "zh": "【美军建立临时机场】美军在伊朗主要城市附近成功建立了临时机场，完成了人员撤离，联合部队继续打击伊朗目标。伊朗政权媒体将此事描述为美国失败，但美军已成功恢复所有人员。"
            },
            {
                "en": "The combined force continued to strike operational components of the missile program including engines, guidance system production facilities, and research and development facilities, including the 1,400 km-range Haj Qassem missile launchers.",
                "zh": "【持续打击伊朗导弹计划】联合部队继续打击导弹计划的运行组件，包括发动机、制导系统生产设施和研发设施，包括射程达1,400公里的Haj Qassem导弹发射器。"
            },
            {
                "en": "The IDF continued to strike tunnel entrances into mountainsides to prevent Iranian forces from using the tunnels to hide missile bases.",
                "zh": "【以军打击隧道入口】以色列国防军继续打击伊朗隧道入口，防止伊朗部队利用隧道隐藏导弹基地。伊朗将重要导弹基地埋在山下和隧道中以隐藏基地，并使空袭难以破坏。"
            },
            {
                "en": "Iran has slightly changed its strike package, incorporating more cruise missiles. It is unclear whether this represents a new tactical experiment, an effort to manage remaining missile stocks, or something else.",
                "zh": "【伊朗改变打击方案】伊朗对海湾国家的打击方案略有改变，增加了更多巡航导弹。尚不清楚这是新战术实验、管理剩余导弹储备的努力还是其他原因。伊朗向科威特发射了四枚巡航导弹，向卡塔尔发射了两枚，向阿联酋和沙特阿拉伯各发射了一枚。"
            },
            {
                "en": "Hezbollah published footage on April 4 and 5 purporting to show FPV drone attacks against Israeli vehicles and two Merkava tanks on March 25.",
                "zh": "【真主党FPV无人机攻击】真主党公布了4月4日和5日的录像，声称显示了3月25日对以色列车辆和两辆梅卡瓦坦克进行的第一人称视角（FPV）无人机攻击。"
            },
            {
                "en": "Hezbollah claimed to have fired an anti-ship cruise missile at an Israeli warship 68 nautical miles from the Lebanese coast on April 5, marking the first time in the war.",
                "zh": "【真主党首次使用反舰巡航导弹】真主党声称于4月5日向距离黎巴嫩海岸68海里的以色列军舰发射了反舰巡航导弹，这是战争开始以来的首次。"
            },
            {
                "en": "The IDF estimates that Hezbollah can attack Israel at a rate of 200 rockets and drones per day for an additional five months.",
                "zh": "【真主党火力评估】以色列国防军估计真主党能够以每天200枚火箭弹和无人机发射的火力向以色列发动攻击，持续额外五个月。但这些攻击似乎未能改变以色列对伊朗进行空袭的决策。"
            },
            {
                "en": "Iranian-backed Iraqi militias attempted to blame Kuwait for attacks on Iraqi oil infrastructure, likely to obfuscate responsibility from domestic Iraqi audiences.",
                "zh": "【伊拉克民兵转移责任】伊朗支持的伊拉克民兵试图将伊拉克石油基础设施袭击归咎于科威特，可能是为了向国内伊拉克观众掩盖责任。"
            }
        ],
        "charts": [
            {
                "url": "https://understandingwar.org/wp-content/uploads/2026/04/NEW-Iranian-Launches-at-KSA-March-1-April-5-FINAL.webp",
                "title_zh": "伊朗对沙特的发射（3月1日-4月5日）",
                "context": [
                    "2026年2月28日至4月5日期间伊朗对沙特发射的所有弹道导弹、巡航导弹和无人机",
                    "红色弹道轨迹、蓝色无人机轨迹、黄色巡航导弹轨迹",
                    "沙特持续遭受伊朗导弹和无人机攻击"
                ],
                "full_analysis": "地图显示2026年2月28日至4月5日期间伊朗对沙特阿拉伯发射的所有弹道导弹、巡航导弹和无人机的轨迹。红色线条表示弹道导弹轨迹，蓝色表示无人机轨迹，黄色表示巡航导弹轨迹。伊朗已略微改变其打击方案，增加了更多巡航导弹的使用。"
            },
            {
                "url": "https://understandingwar.org/wp-content/uploads/2026/04/NEW-Iranian-Launches-at-Bahrain-Feb-28-Apr-5-FINAL.webp",
                "title_zh": "伊朗对巴林的发射（2月28日-4月5日）",
                "context": [
                    "2月28日至4月5日期间伊朗对巴林发射的无人机和导弹",
                    "伊朗无人机击中巴林Sitra的多个GPIC设施和BAPCO储油罐",
                    "巴林持续遭受伊朗攻击"
                ],
                "full_analysis": "地图显示2026年2月28日至4月5日期间伊朗对巴林发射的弹道导弹、巡航导弹和无人机的轨迹。伊朗无人机击中巴林Sitra的多个GPIC（海湾石化工业公司）设施和BAPCO（巴林石油公司）储油罐，引发火灾。"
            },
            {
                "url": "https://understandingwar.org/wp-content/uploads/2026/04/NEW-Iranian-Launches-at-the-UAE-April-5-FINAL.webp",
                "title_zh": "伊朗对阿联酋的发射（4月5日）",
                "context": [
                    "伊朗4月5日对阿联酋发射的无人机和导弹",
                    "拦截碎片在阿联酋al Ruwais的Borouge石化厂引发三起火灾",
                    "伊朗对阿联酋能源基础设施的持续攻击"
                ],
                "full_analysis": "地图显示2026年4月5日伊朗对阿联酋发射的弹道导弹、巡航导弹和无人机的轨迹。拦截碎片在阿联酋al Ruwais的Borouge石化厂引发三起火灾，该设施已暂停运营。"
            },
            {
                "url": "https://understandingwar.org/wp-content/uploads/2026/04/NEW-Iranian-Launches-at-Kuwait-February-28-April-5-FINAL.webp",
                "title_zh": "伊朗对科威特的发射（2月28日-4月5日）",
                "context": [
                    "2月28日至4月5日期间伊朗对科威特发射的无人机和导弹",
                    "伊朗向科威特发射了四枚巡航导弹",
                    "科威特持续遭受伊朗攻击"
                ],
                "full_analysis": "地图显示2026年2月28日至4月5日期间伊朗对科威特发射的弹道导弹、巡航导弹和无人机的轨迹。伊朗已改变打击方案，向科威特发射了四枚巡航导弹，此前没有以这种速率使用巡航导弹。"
            },
            {
                "url": "https://understandingwar.org/wp-content/uploads/2026/04/US-and-Israeli-Strikes-on-Iran-Evening-of-April-5-2026.webp",
                "title_zh": "美以在伊朗的打击（4月5日晚）",
                "context": [
                    "美以联军4月5日晚在伊朗境内的打击目标",
                    "包括Kamyaran和Farashband的导弹发射器",
                    "Ahvaz国际机场、IRGC第14伊玛目侯赛因师等目标"
                ],
                "full_analysis": "地图显示美以联军于2026年4月5日晚间在伊朗境内的打击目标。主要目标包括：Kamyaran（库尔德斯坦省）和Farashband（法尔斯省）的导弹发射器、Ahvaz国际机场、IRGC第14伊玛目侯赛因师、Sepah银行（遭受重大计算机网络中断）等。"
            },
            {
                "url": "https://understandingwar.org/wp-content/uploads/2026/04/Iranian-Retalitory-Strikes-April-4-2026-to-April-5-2026-scaled.webp",
                "title_zh": "伊朗报复性打击（4月4日-4月5日）",
                "context": [
                    "2026年4月4日至4月5日伊朗对以色列的报复性打击",
                    "伊朗弹道导弹击中以色列Neot Hovav工业区",
                    "伊朗导弹直接击中海法一栋住宅楼"
                ],
                "full_analysis": "地图显示2026年4月4日至4月5日期间伊朗对以色列的报复性打击。伊朗自4月4日以来至少向以色列发射了五枚导弹，包括击中以色列Neot Hovav工业区开阔地带的导弹，以及直接击中海法一栋住宅楼、造成严重损坏的导弹。"
            },
            {
                "url": "https://understandingwar.org/wp-content/uploads/2026/04/Hezbollah-Claimed-Attacks-in-Northern-Israel-Total-March-1-April-4-FINAL-1.webp",
                "title_zh": "真主党对以色列北部声称袭击总数（3月1日-4月4日）",
                "context": [
                    "真主党3月1日至4月4日期间声称的对以色列北部的攻击总数",
                    "真主党能够以每天200次发射的火力持续攻击",
                    "IDF承认高估了2024年秋季冲突中对真主党的削弱程度"
                ],
                "full_analysis": "地图汇总显示真主党在2026年3月1日至4月4日期间对以色列北部城镇和社区的总攻击次数。以色列国防军估计真主党能够以每天200枚火箭弹和无人机发射的火力向以色列发动攻击，持续额外五个月。以色列媒体称IDF承认高估了2024年秋季冲突中对真主党的削弱程度，真主党准备进行长期战役。"
            },
            {
                "url": "https://understandingwar.org/wp-content/uploads/2026/04/Hezbollah-Attacks-in-Israel-and-Lebanon-Evening-of-April-5-2026.webp",
                "title_zh": "真主党在以色列和黎巴嫩的攻击（4月5日晚）",
                "context": [
                    "真主党4月5日对以色列和黎巴嫩的攻击",
                    "真主党首次使用反舰巡航导弹攻击以色列军舰",
                    "真主党在黎巴嫩南部多次使用FPV无人机进行攻击"
                ],
                "full_analysis": "地图显示2026年4月5日真主党对以色列和黎巴嫩的攻击情况。真主党声称于4月5日向距离黎巴嫩海岸68海里的以色列军舰发射了反舰巡航导弹，这是战争开始以来的首次。真主党还公布了FPV无人机攻击以色列车辆和梅卡瓦坦克的录像。"
            },
            {
                "url": "https://understandingwar.org/wp-content/uploads/2026/04/Hezbollah-Claimed-Attacks-March-1-April-4-FINAL.webp",
                "title_zh": "真主党声称的攻击（3月1日-4月4日）",
                "context": [
                    "真主党3月1日至4月4日期间声称的攻击",
                    "包括反坦克导弹、迫击炮和火箭弹攻击",
                    "真主党在黎巴嫩南部的军事行动"
                ],
                "full_analysis": "地图显示真主党在2026年3月1日至4月4日期间声称的对黎巴嫩南部以色列部队的攻击位置。真主党声称在此期间进行了多次攻击，主要使用反坦克导弹、迫击炮和火箭弹。IDF继续对黎巴嫩境内的真主党基础设施进行空袭和地面行动。"
            }
        ]
    },
    "history": [
        {
            "date": "2026-04-05",
            "title": "Iran Update Special Report, April 5, 2026",
            "url": "https://understandingwar.org/research/middle-east/iran-update-special-report-april-5-2026/"
        },
        {
            "date": "2026-04-04",
            "title": "Iran Update Special Report, April 4, 2026",
            "url": "https://understandingwar.org/research/middle-east/iran-update-special-report-april-4-2026/"
        },
        {
            "date": "2026-04-03",
            "title": "Iran Update Special Report, April 3, 2026",
            "url": "https://understandingwar.org/research/middle-east/iran-update-special-report-april-3-2026/"
        },
        {
            "date": "2026-04-02",
            "title": "Iran Update Special Report, April 2, 2026",
            "url": "https://understandingwar.org/research/middle-east/iran-update-special-report-april-2-2026/"
        },
        {
            "date": "2026-04-01",
            "title": "Iran Update Special Report, April 1, 2026",
            "url": "https://understandingwar.org/research/middle-east/iran-update-special-report-april-1-2026/"
        }
    ]
}

def read_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def replace_static_data(html_content, new_data):
    """替换 STATIC_ISW_DATA 对象"""
    pattern = r'(let STATIC_ISW_DATA = )\{[^}]*\}[^;]*;'
    new_data_str = json.dumps(new_data, ensure_ascii=False, indent=2)
    replacement = r'\1' + new_data_str + ';'
    new_content = re.sub(pattern, replacement, html_content, flags=re.DOTALL)
    return new_content

def main():
    filepath = r"D:\python_code\海湾以来-最新\war-situation.html"
    
    print("读取文件...")
    html_content = read_file(filepath)
    
    print("更新 STATIC_ISW_DATA...")
    new_content = replace_static_data(html_content, ISW_DATA)
    
    print("保存文件...")
    write_file(filepath, new_content)
    print("更新完成！")

if __name__ == "__main__":
    main()
