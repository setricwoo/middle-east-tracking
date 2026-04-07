#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
更新 oil-chart.html 各国最新动态 - 第二轮更新
添加近72小时（4月5日-4月7日）的新闻，保留旧新闻，去重，时间排序
"""

import re
import json

# 近72小时的新新闻（2026年4月5日-4月7日）
NEW_NEWS = {
    "沙特阿拉伯": [
        {
            "date": "2026-04-06",
            "title": "沙特拦截7枚伊朗弹道导弹，碎片落入东部省能源设施附近",
            "content": "4月6日沙特国防部表示，防空系统拦截并摧毁了7枚射向东部地区的弹道导弹，碎片落在能源设施附近。自美以对伊朗开战以来，沙特已遭受数百枚伊朗导弹和无人机袭击。沙特2026年5月目标产量为1022.8万桶/日，将提供计划总产量增量的60%以上"
        },
        {
            "date": "2026-04-06", 
            "title": "沙特与俄罗斯将主导5月OPEC+增产计划",
            "content": "4月6日ET EnergyWorld报道，沙特和俄罗斯将提供2026年5月计划总产量增量的60%以上。OPEC+八个国家决定实施总计20.6万桶/日的产量调整，沙特2026年5月目标产量为1022.8万桶/日"
        }
    ],
    "阿联酋": [
        {
            "date": "2026-04-05",
            "title": "阿布扎比Borouge石化工厂因袭击引发火灾停产",
            "content": "4月5日彭博社报道，阿联酋阿布扎比Ruwais的大型石化工厂Borouge因袭击引发多起火灾而停产。阿布扎比政府媒体办公室表示，火灾由防空拦截坠落碎片引起，暂无人员伤亡报告"
        }
    ],
    "伊朗": [
        {
            "date": "2026-04-06",
            "title": "美以空袭布什尔核电站附近仅75米，IAEA确认袭击",
            "content": "4月6日DW报道，国际原子能机构(IAEA)确认美以空袭袭击了伊朗布什尔核电站附近，其中一次袭击距离核电站边界仅75米。沿海城市阿萨卢耶（伊朗天然气工业中心）的炼油厂附近发生一系列爆炸"
        },
        {
            "date": "2026-04-06",
            "title": "以色列袭击伊朗South Pars天然气工厂，超过25人丧生",
            "content": "4月6日Yahoo News报道，以色列表示袭击了South Pars天然气工厂，美以战争导致伊朗多个城市超过25人在空袭中丧生。特朗普加强对伊朗的威胁，称将从周二开始轰炸伊朗发电厂"
        },
        {
            "date": "2026-04-06",
            "title": "伊朗称被炸毁的导弹掩体正在数小时内恢复",
            "content": "4月6日Times of Israel报道，伊朗表示被炸毁的导弹掩体正在数小时内恢复。伊朗弹道导弹袭击以色列中部地区，造成4人轻伤。伊朗对以色列的持续导弹袭击仍在继续"
        }
    ],
    "科威特": [
        {
            "date": "2026-04-05",
            "title": "伊朗无人机损坏科威特炼油厂，Al Jahra变电站恢复运行",
            "content": "4月5日Jerusalem Post报道，阿联酋、巴林、科威特和沙特继续面临伊朗导弹和无人机袭击。伊朗无人机损坏了科威特炼油厂。科威特电力、水和可再生能源部表示技术团队已恢复Al Jahra主变电站运行"
        }
    ],
    "卡塔尔": [
        {
            "date": "2026-04-06",
            "title": "卡塔尔Golden Pass LNG美国工厂首次生产液化天然气",
            "content": "4月6日Marine News报道，Golden Pass LNG（卡塔尔能源70%/埃克森美孚30%合资企业）在得州Sabine Pass出口设施的首条生产线首次生产液化天然气，总产能为每年1800万吨。预计2026年第二季度开始出口"
        }
    ],
    "伊拉克": [
        {
            "date": "2026-04-06",
            "title": "伊拉克作为OPEC+成员参与5月增产计划",
            "content": "4月6日相关报道，伊拉克作为OPEC+八个成员国之一，将参与5月总计20.6万桶/日的产量调整计划。伊拉克此前已通过库尔德管道恢复部分出口"
        }
    ]
}

def read_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def update_country_updates(html_content, country_name, new_updates):
    """更新指定国家的 updates 数组"""
    # 构建正则表达式模式来查找该国家的 updates 数组
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
        # 检查是否已存在类似标题（简单去重）
        is_duplicate = False
        for seen_title in seen_titles:
            # 如果标题相似度超过70%，认为是重复
            if update["title"] in seen_title or seen_title in update["title"]:
                is_duplicate = True
                break
        
        if not is_duplicate:
            all_updates.append(update)
            seen_titles.add(update["title"])
    
    # 再添加现有新闻（去重）
    for update in existing_updates:
        clean_title = update["title"].replace('\\"', '"')
        is_duplicate = False
        for seen_title in seen_titles:
            if clean_title in seen_title or seen_title in clean_title:
                is_duplicate = True
                break
        
        if not is_duplicate:
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
    
    print(f"更新 {country_name}: 原有 {len(existing_updates)} 条，新增 {len(new_updates)} 条，合并后共 {len(all_updates)} 条")
    
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
