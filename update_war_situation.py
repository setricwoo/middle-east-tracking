#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新 war-situation.html 的 ISW 数据
使用 2026年4月4日特别报告的内容
"""

import re
import json

# ISW 2026年4月4日特别报告数据
ISW_DATA = {
    "updated": "2026-04-04T14:00:00",
    "source_url": "https://understandingwar.org/research/middle-east/iran-update-special-report-april-4-2026/",
    "current_report": {
        "url": "https://understandingwar.org/research/middle-east/iran-update-special-report-april-4-2026/",
        "title": "Iran Update Special Report, April 4, 2026",
        "title_zh": "伊朗局势更新特别报告 - 2026年4月4日",
        "date": "2026-04-04",
        "takeaways": [
            {
                "en": "The loss of two US aircraft does not mean that the combined force is losing air superiority over Iran. Friendly forces maintain air superiority even in the face of enemy shoot-down attempts so long as enemy air defenses do not seriously impede friendly operations. Iranian attempts to challenge US-Israeli air superiority have not seriously impeded the combined force's ability to conduct operations into Iran.",
                "zh": "【美军损失两架飞机不意味着失去空中优势】美军失去两架飞机并不意味着联合部队正在失去对伊朗的空中优势。友军即使面对敌方击落企图，只要敌方防空系统不严重阻碍友军行动，就能保持空中优势。伊朗挑战美以空中优势的尝试并未严重阻碍联合部队在伊朗境内开展行动的能力。"
            },
            {
                "en": "Chinese assistance to Iran in rebuilding its ballistic missile program could undermine efforts by the combined force to degrade or destroy the supporting elements of that missile program. Five ships carrying sodium perchlorate—a key precursor for solid missile propellant—reportedly arrived in Iran from China.",
                "zh": "【中国协助伊朗重建弹道导弹计划】中国协助伊朗重建弹道导弹计划可能破坏联合部队削弱或摧毁弹道导弹计划支持要素的努力。据报道，五艘载有固体导弹推进剂关键前体（高氯酸钠）的船只从中国抵达伊朗。"
            },
            {
                "en": "The combined force targeted the Shalamcheh crossing on the Iran-Iraq border after reports that Popular Mobilization Forces fighters deployed via the crossing to Basij bases in Khuzestan Province.",
                "zh": "【联合部队打击伊朗-伊拉克边境沙拉姆切过境点】联合部队针对伊朗-伊拉克边境的沙拉姆切过境点发动打击，因为有报告称人民动员部队（PMF）战士通过该过境点部署到胡齐斯坦省的巴斯基基地。"
            }
        ],
        "charts": [
            {
                "url": "https://understandingwar.org/wp-content/uploads/2026/04/Chinese-Shipments-of-Solid-Missile-Propellant-Precursor-to-Iran-Evening-of-April-2-2026.webp",
                "title_zh": "中国向伊朗运送固体导弹推进剂前体（4月2日晚）",
                "context": [
                    "五艘载有高氯酸钠（固体导弹推进剂关键前体）的船只从中国抵达伊朗",
                    "所有船只均属于2021年被美国制裁的伊朗伊斯兰共和国航运集团(IRISL)",
                    "中国援助可能破坏联合部队削弱伊朗导弹计划的努力"
                ],
                "full_analysis": "图表显示五艘可能载有高氯酸钠（固体导弹推进剂关键前体）的船只从中国抵达伊朗的航线。这些船只均属于2021年被美国制裁的伊朗伊斯兰共和国航运集团(IRISL)。高氯酸钠是制造固体燃料弹道导弹的关键化学品。中国此举可能破坏联合部队削弱或摧毁伊朗弹道导弹计划支持要素的努力。"
            },
            {
                "url": "https://understandingwar.org/wp-content/uploads/2026/04/US-and-Israeli-Strikes-on-Iran-Evening-April-4-2026.webp",
                "title_zh": "美以在伊朗的打击（4月4日晚）",
                "context": [
                    "美以联军4月4日晚在伊朗境内的打击目标分布",
                    "包括胡齐斯坦省沙拉姆切过境点、德黑兰S-300防空基地",
                    "班达里马姆霍梅尼石化设施等目标"
                ],
                "full_analysis": "地图显示美以联军于2026年4月4日晚间在伊朗境内的打击目标。主要目标包括：胡齐斯坦省沙拉姆切过境点（伊朗-伊拉克边境）、德黑兰省卡赫里扎克的S-300防空导弹防御基地、胡齐斯坦省班达里马姆霍梅尼的石化设施。这些打击旨在削弱伊朗的防空能力、导弹运输通道和军事工业基础。"
            },
            {
                "url": "https://understandingwar.org/wp-content/uploads/2026/04/NEW-Iranian-Launches-at-KSA-March-1-April-4-FINAL.webp",
                "title_zh": "伊朗对沙特的发射（3月1日-4月4日）",
                "context": [
                    "2月28日至4月4日期间伊朗对沙特发射的所有无人机和导弹",
                    "红色弹道轨迹、蓝色无人机轨迹、黄色巡航导弹轨迹",
                    "沙特持续遭受伊朗导弹和无人机攻击"
                ],
                "full_analysis": "地图显示2026年2月28日至4月4日期间伊朗对沙特阿拉伯发射的所有弹道导弹、巡航导弹和无人机的轨迹。红色线条表示弹道导弹轨迹，蓝色表示无人机轨迹，黄色表示巡航导弹轨迹。图表显示伊朗持续对沙特能源设施和军事目标发动攻击，沙特防空系统拦截了大部分来袭目标。"
            },
            {
                "url": "https://understandingwar.org/wp-content/uploads/2026/04/NEW-Iranian-Launches-at-the-UAE-April-4-FINAL.webp",
                "title_zh": "伊朗对阿联酋的发射（4月4日）",
                "context": [
                    "伊朗4月4日对阿联酋发射的无人机和导弹位置",
                    "阿联酋拦截56架无人机和23枚弹道导弹",
                    "伊朗对阿联酋的攻击规模超过对以色列的攻击"
                ],
                "full_analysis": "地图显示2026年4月4日伊朗对阿联酋发射的无人机和导弹的轨迹。阿联酋国防部报告拦截了56架无人机和23枚弹道导弹。值得注意的是，伊朗向阿联酋发射的导弹和无人机数量超过任何其他国家，包括以色列，表明阿联酋是伊朗的主要攻击目标之一。"
            },
            {
                "url": "https://understandingwar.org/wp-content/uploads/2026/04/NEW-Iranian-Launches-at-Kuwait-February-28-April-4-FINAL.webp",
                "title_zh": "伊朗对科威特的发射（2月28日-4月4日）",
                "context": [
                    "2月28日至4月4日期间伊朗对科威特发射的无人机和导弹",
                    "科威特4月4日拦截多架无人机和导弹",
                    "科威特武装部队报告持续遭受伊朗攻击"
                ],
                "full_analysis": "地图显示2026年2月28日至4月4日期间伊朗对科威特发射的无人机和导弹的轨迹。科威特石油公司(KPC)总部于4月4日遭伊朗无人机袭击起火。科威特武装部队报告持续遭受伊朗攻击，防空系统保持高度戒备。"
            },
            {
                "url": "https://understandingwar.org/wp-content/uploads/2026/04/NEW-Iranian-Launches-at-Bahrain-Feb-28-Apr-4-FINAL.webp",
                "title_zh": "伊朗对巴林的发射（2月28日-4月4日）",
                "context": [
                    "2月28日至4月4日期间伊朗对巴林发射的无人机和导弹",
                    "巴林4月4日拦截多架无人机",
                    "巴林呼吁联合国安理会就保护海峡航运投票"
                ],
                "full_analysis": "地图显示2026年2月28日至4月4日期间伊朗对巴林发射的无人机和导弹的轨迹。巴林国防军报告拦截多架伊朗无人机。巴林希望联合国安理会就保护霍尔木兹海峡商业航运的决议进行投票，呼吁国际社会采取行动保障航运安全。"
            },
            {
                "url": "https://understandingwar.org/wp-content/uploads/2026/04/Hezbollah-Claimed-Attacks-March-1-April-3-FINAL.webp",
                "title_zh": "真主党声称的袭击（3月1日-4月3日）",
                "context": [
                    "真主党3月1日至4月3日期间声称的对黎巴嫩南部以色列部队的攻击",
                    "包括反坦克导弹、迫击炮和火箭弹攻击",
                    "真主党可能在逾越节期间增加对以色列的火力"
                ],
                "full_analysis": "地图显示真主党在2026年3月1日至4月3日期间声称的对黎巴嫩南部以色列部队的攻击位置。真主党声称在此期间进行了超过100次攻击，主要使用反坦克导弹、迫击炮和火箭弹。以色列国防部长卡茨表示，真主党总书记纳伊姆·卡西姆将为'在以色列人庆祝逾越节期间加强对以色列平民的火力'付出'非常沉重的代价'。"
            },
            {
                "url": "https://understandingwar.org/wp-content/uploads/2026/04/Hezbollah-Claimed-Attacks-in-Northern-Israel-Total-March-1-April-3-FINAL.webp",
                "title_zh": "真主党对以色列北部声称袭击总数（3月1日-4月3日）",
                "context": [
                    "真主党对以色列北部城镇和社区的总攻击次数统计",
                    "包括Krayot、Kiryat Shmona、Shlomi、Metula和Nahariya等目标",
                    "真主党对以色列北部基础设施和社区进行23次袭击"
                ],
                "full_analysis": "地图汇总显示真主党在2026年3月1日至4月3日期间对以色列北部城镇和社区的总攻击次数。主要目标包括Krayot、Kiryat Shmona、Shlomi、Metula和Nahariya等。真主党对以色列北部基础设施和社区进行了23次袭击，旨在对以色列平民造成心理影响。"
            },
            {
                "url": "https://understandingwar.org/wp-content/uploads/2026/04/Lebanon-LH-and-Iranian-Attacks-April-4-2026.webp",
                "title_zh": "黎巴嫩和伊朗袭击（2026年4月4日）",
                "context": [
                    "真主党4月4日声称的对黎巴嫩南部以色列部队的攻击",
                    "伊朗对以色列的导弹袭击",
                    "黎巴嫩南部冲突态势"
                ],
                "full_analysis": "地图显示2026年4月4日黎巴嫩真主党和伊朗对以色列的袭击情况。包括真主党声称的袭击位置以及伊朗向以色列发射的导弹轨迹。真主党声称在4月3日至4月4日期间对黎巴嫩南部以色列军队进行19次袭击。伊朗则向以色列中部和南部发射带有集束弹头的弹道导弹和无人机。"
            },
            {
                "url": "https://understandingwar.org/wp-content/uploads/2026/04/US-and-Israeli-Strikes-on-Iran-Evening-April-3-2026.webp",
                "title_zh": "美以在伊朗的打击（4月3日晚）",
                "context": [
                    "美以联军4月3日晚在伊朗境内的打击目标",
                    "包括布什尔核电站附近区域",
                    "国际原子能机构(IAEA)报告称弹丸击中核电站附近"
                ],
                "full_analysis": "地图显示美以联军于2026年4月3日晚间在伊朗境内的打击目标。国际原子能机构(IAEA)报告称其监测站检测到弹丸击中布什尔核电站附近区域。俄罗斯已从布什尔核电站撤离更多人员，目前仅剩300人留守。"
            }
        ]
    },
    "history": [
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
        },
        {
            "date": "2026-03-30",
            "title": "Iran Update Special Report, March 30, 2026",
            "url": "https://understandingwar.org/research/middle-east/iran-update-special-report-march-30-2026/"
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
    # 找到 STATIC_ISW_DATA = { 的位置
    pattern = r'(let STATIC_ISW_DATA = )\{[^}]*\}[^;]*;'
    
    # 将新数据转换为 JSON 字符串
    new_data_str = json.dumps(new_data, ensure_ascii=False, indent=2)
    
    # 替换
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
