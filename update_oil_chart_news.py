#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新 oil-chart.html 各国最新动态
添加近72小时的新闻，保留旧新闻，去重，时间由新到早排序
"""

import re
import json

# 近72小时的新新闻（2026年4月2日-4月5日）
NEW_NEWS = {
    "沙特阿拉伯": [
        {
            "date": "2026-04-04",
            "title": "沙特防空系统拦截伊朗导弹和无人机，保护东部省能源设施",
            "content": "4月4日沙特国防部报告，成功拦截多枚伊朗弹道导弹和无人机，保护东部省关键能源设施。伊朗持续对沙特发动攻击，沙特军队保持高度戒备"
        },
        {
            "date": "2026-04-03",
            "title": "沙特探索与亚洲国家建立绕开霍尔木兹的能源合作新机制",
            "content": "4月3日华尔街日报报道，沙特正与亚洲主要石油消费国探讨建立绕过霍尔木兹海峡的长期能源合作机制，包括战略储备共享和替代运输路线投资"
        }
    ],
    "阿联酋": [
        {
            "date": "2026-04-03",
            "title": "阿联酋EGA铝厂遭伊朗导弹和无人机袭击，全面恢复需12个月",
            "content": "4月3日Mining.com报道，阿联酋全球铝业(EGA)Al Taweelah冶炼厂遭伊朗导弹和无人机袭击，全面恢复生产可能需要长达12个月。这是冲突以来阿联酋遭受的最严重工业设施袭击"
        },
        {
            "date": "2026-04-03",
            "title": "阿联酋国防部报告4月3日拦截56架无人机和23枚弹道导弹",
            "content": "4月3日阿联酋国防部报告，成功拦截56架无人机和23枚弹道导弹，创单日拦截纪录。伊朗持续对阿联酋发动大规模攻击，能源设施安全形势严峻"
        }
    ],
    "伊拉克": [
        {
            "date": "2026-04-04",
            "title": "巴士拉外资石油公司储油设施遭无人机袭击起火",
            "content": "4月4日路透社报道，伊拉克南部巴士拉Barjasiyah区外资石油公司储油设施遭无人机袭击起火，消防员已控制火势。这是伊朗对伊拉克能源设施持续攻击的最新事件"
        },
        {
            "date": "2026-04-04",
            "title": "伊拉克关闭与伊朗的沙拉姆切过境点，阻止PMF战士部署",
            "content": "4月4日路透社报道，伊拉克关闭与伊朗边境的沙拉姆切过境点，因有报告称人民动员部队(PMF)战士通过该过境点部署到伊朗胡齐斯坦省的巴斯基基地"
        }
    ],
    "伊朗": [
        {
            "date": "2026-04-04",
            "title": "俄罗斯从布什尔核电站撤离更多人员，仅剩300人留守",
            "content": "4月4日路透社报道，俄罗斯从伊朗布什尔核电站撤离198名工作人员，目前仅剩300人留守。此前3月25日已撤离163人。国际原子能机构(IAEA)报告称弹丸击中核电站附近"
        },
        {
            "date": "2026-04-03",
            "title": "五艘载有导弹燃料化学品的船只从中国抵达伊朗",
            "content": "4月3日每日电讯报报道，五艘可能载有高氯酸钠（固体导弹推进剂关键前体）的船只从中国抵达伊朗。所有船只均属于2021年被美国制裁的伊朗伊斯兰共和国航运集团(IRISL)，可能破坏联军削弱伊朗导弹计划的努力"
        },
        {
            "date": "2026-04-04",
            "title": "美以联军打击伊朗胡齐斯坦导弹基地和德黑兰S-300防空基地",
            "content": "4月4日美以联军出动F-35I战机和战斧导弹，对伊朗胡齐斯坦省阿瓦士附近两处地下导弹基地实施联合打击，摧毁约120枚中程弹道导弹。同时袭击德黑兰省卡赫里扎克的S-300防空导弹防御基地"
        },
        {
            "date": "2026-04-04",
            "title": "伊朗向沙特、阿联酋发射导弹和无人机，回应美以打击",
            "content": "4月4日伊朗向沙特东部达曼附近石油加工设施发射7枚中程弹道导弹和15架无人机，同时向阿联酋发射大量无人机和导弹。沙特和阿联酋防空系统拦截大部分来袭目标"
        },
        {
            "date": "2026-04-04",
            "title": "伊朗对以色列发射装有集束弹药的弹道导弹",
            "content": "4月4日伊朗向以色列发射至少一枚装有集束弹药的弹道导弹，造成以色列中部5人受伤，多栋房屋受损。这是伊朗首次在冲突中使用集束弹药"
        }
    ],
    "科威特": [
        {
            "date": "2026-04-04",
            "title": "科威特石油公司(KPC)总部遭伊朗无人机袭击起火",
            "content": "4月4日彭博社报道，科威特石油公司(KPC)总部遭伊朗无人机袭击起火，大楼被疏散，消防队在现场。此前Mina Al-Ahmadi和Mina Abdullah炼油厂也多次遭袭"
        },
        {
            "date": "2026-04-04",
            "title": "科威特军队保持高度戒备，拦截多架伊朗无人机",
            "content": "4月4日科威特国防部报告，军队保持高度戒备状态，防空系统成功拦截多架伊朗无人机。科威特武装部队报告持续遭受伊朗攻击，能源设施面临严重威胁"
        }
    ],
    "卡塔尔": [
        {
            "date": "2026-04-04",
            "title": "卡塔尔Ras Laffan LNG设施遭袭后续：年产能损失17%，修复需5年",
            "content": "4月4日更新报道，卡塔尔能源Ras Laffan设施遭伊朗袭击后暂停运营，LNG出口能力损失17%，修复可能需要5年，年产能减少1200万吨。意大利等国LNG供应中断"
        },
        {
            "date": "2026-04-03",
            "title": "意大利总理梅洛尼访问卡塔尔，商讨LNG供应中断问题",
            "content": "4月3日路透社报道，意大利总理梅洛尼访问卡塔尔，因霍尔木兹海峡关闭，意大利LNG供应中断10批货物（4月至6月中旬）。卡塔尔表示将尽力保障对友好国家的供应"
        }
    ],
    "巴林": [
        {
            "date": "2026-04-04",
            "title": "巴林国防军报告拦截多架伊朗无人机，呼吁联合国保护海峡航运",
            "content": "4月4日巴林国防军报告，成功拦截多架伊朗无人机。巴林希望联合国安理会就保护霍尔木兹海峡商业航运的决议进行投票，呼吁国际社会采取行动保障航运安全"
        }
    ]
}

# 霍尔木兹海峡相关新闻（作为补充信息存储）
HORMUZ_NEWS = [
    {
        "date": "2026-04-04",
        "title": "霍尔木兹海峡通航量较2月下降95%，日均仅6艘船舶通过",
        "content": "4月4日UNCTAD警告，霍尔木兹海峡日均通行量从2月的129艘降至3月的仅6艘，下降95%。2026年全球商品增长预计降至1.5%-2.5%，全球贸易面临严重冲击"
    },
    {
        "date": "2026-04-04",
        "title": "三艘油轮沿阿曼海岸新航线进入霍尔木兹海峡",
        "content": "4月4日彭博社报道，三艘油轮沿阿曼海岸新航线进入霍尔木兹海峡，避开伊朗水域。这是商船探索替代航线的重要进展"
    },
    {
        "date": "2026-04-03",
        "title": "法国达飞轮船集装箱船成功通过霍尔木兹海峡",
        "content": "4月3日金融时报报道，法国达飞轮船集装箱船成功通过霍尔木兹海峡，伊朗正为特定盟友国家制定'过境协议'，选择性允许部分国家船只通行"
    },
    {
        "date": "2026-04-02",
        "title": "霍尔木兹封锁影响的关键商品：LPG、化肥、铝、氦气供应中断",
        "content": "4月2日OilPrice.com报道，霍尔木兹封锁导致LPG短缺重创印度和中国，化肥供应中断威胁全球农作物产量，铝和氦气基础设施受损。全球供应链面临系统性冲击"
    }
]

def read_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def update_country_updates(html_content, country_name, new_updates):
    """更新指定国家的 updates 数组"""
    # 构建正则表达式模式来查找该国家的 updates 数组
    # 模式：找到国家名称，然后找到 updates: [ ... ]
    
    # 首先找到国家的位置
    country_pattern = rf'name:\s*"{country_name}".*?updates:\s*\['
    match = re.search(country_pattern, html_content, re.DOTALL)
    
    if not match:
        print(f"未找到国家: {country_name}")
        return html_content
    
    # 找到 updates 数组的起始位置
    updates_start = match.end() - 1  # 包含 [
    
    # 找到 updates 数组的结束位置（匹配的 ]）
    bracket_count = 0
    updates_end = updates_start
    for i, char in enumerate(html_content[updates_start:], start=updates_start):
        if char == '[':
            bracket_count += 1
        elif char == ']':
            bracket_count -= 1
            if bracket_count == 0:
                updates_end = i
                break
    
    # 提取现有 updates
    existing_updates_str = html_content[updates_start+1:updates_end]
    
    # 解析现有 updates
    existing_updates = []
    if existing_updates_str.strip():
        # 分割单独的 update 对象
        update_pattern = r'\{[^}]*date:\s*"([^"]+)"[^}]*title:\s*"([^"]+)"[^}]*content:\s*"([^"]+)"[^}]*\}'
        for m in re.finditer(update_pattern, existing_updates_str, re.DOTALL):
            existing_updates.append({
                "date": m.group(1),
                "title": m.group(2),
                "content": m.group(3)
            })
    
    # 合并新新闻和现有新闻，去重
    all_updates = []
    seen_titles = set()
    
    # 先添加新新闻
    for update in new_updates:
        if update["title"] not in seen_titles:
            all_updates.append(update)
            seen_titles.add(update["title"])
    
    # 再添加现有新闻（去重）
    for update in existing_updates:
        # 清理标题中的转义字符
        clean_title = update["title"].replace('\\"', '"')
        if clean_title not in seen_titles:
            all_updates.append(update)
            seen_titles.add(clean_title)
    
    # 按日期排序（新到早）
    all_updates.sort(key=lambda x: x["date"], reverse=True)
    
    # 生成新的 updates 数组字符串
    new_updates_str = ",\n                        ".join([
            f'{{ date: "{u["date"]}", title: "{u["title"]}", content: "{u["content"]}" }}'
            for u in all_updates
        ])
    
    # 替换原内容
    new_content = html_content[:updates_start+1] + "\n                        " + new_updates_str + "\n                    " + html_content[updates_end:]
    
    print(f"更新 {country_name}: 原有 {len(existing_updates)} 条，新增 {len(new_updates)} 条，现在共 {len(all_updates)} 条")
    
    return new_content

def main():
    filepath = r"D:\python_code\海湾以来-最新\oil-chart.html"
    
    print("读取文件...")
    html_content = read_file(filepath)
    
    print("\n开始更新各国新闻...")
    
    # 更新各个国家
    for country_name, news_list in NEW_NEWS.items():
        html_content = update_country_updates(html_content, country_name, news_list)
    
    print("\n保存文件...")
    write_file(filepath, html_content)
    print("更新完成！")

if __name__ == "__main__":
    main()
