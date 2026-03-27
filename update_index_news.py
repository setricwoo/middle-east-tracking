#!/usr/bin/env python3
"""
更新海湾原油图谱网页(index.html)的各国最新动态
添加最新新闻，保留旧新闻，避免重复
"""

import re
import json
from datetime import datetime
from pathlib import Path

WORKDIR = Path(__file__).parent.resolve()

# 定义要添加的新新闻（按国家分类）
# 注意：只添加3月20日及以后的新闻（3月19日及之前的已存在）
NEW_NEWS = {
    "沙特阿拉伯": [
        {"date": "2026-03-23", "title": "全球最大财险公司安达保险或将承保霍尔木兹海峡航运保险", "content": "3月23日新浪财经报道，全球最大财险公司安达保险(Chubb)作为DFC 200亿美元航运保险计划的首席承保方，可能为霍尔木兹海峡航运重启提供关键保险支撑，为海峡通航带来一线希望"},
        {"date": "2026-03-22", "title": "从海运保险看霍尔木兹海峡封锁：国际保险市场启动'软封锁'", "content": "3月22日华西证券报告显示，国际主流海事保险体系对波斯湾/霍尔木兹海峡启动'集体撤保+拒保'，保险费率从战前0.25%飙升至5%，从保险精算层面构成对海峡的'软封锁'"},
        {"date": "2026-03-21", "title": "特朗普称美国将不再守卫霍尔木兹海峡", "content": "3月21日北京日报报道，特朗普称美国将不再承担霍尔木兹海峡守卫责任，应由使用国家承担。国际海事组织秘书长表示军事协助'既非长久之计，也不是可持续的解决之道'"},
        {"date": "2026-03-20", "title": "沙特Ras Tanura炼油厂在袭击后恢复运营", "content": "3月20日IndexBox报道，沙特Ras Tanura炼油厂在3月无人机袭击后已恢复运营。该炼油厂日处理能力55万桶，是沙特最大炼油厂，约占全国炼油产能的16%"},
    ],
    "阿联酋": [
        {"date": "2026-03-23", "title": "海湾各国多个能源设施遇袭，阿联酋Habshan和巴布油田成目标", "content": "3月21日财联社梳理报道，阿联酋Habshan天然气厂和巴布油田成为伊朗袭击目标，已暂时关闭。Ruwais炼油厂（世界第四大单点炼油厂）此前已因无人机袭击附近区域预防性关闭"},
        {"date": "2026-03-20", "title": "道达尔能源停止阿联酋近海生产，影响全球产量15%", "content": "3月22日Kansas Reflector报道，法国道达尔能源公司停止阿联酋近海的部分石油和天然气生产，预计影响其全球油气总产量的15%"},
    ],
    "伊拉克": [
        {"date": "2026-03-20", "title": "伊拉克计划将日产量从440万桶增至550万桶", "content": "3月20日相关报道显示，伊拉克2025年全国石油产量增加约12万桶/日，计划将日产量从440万桶增至550万桶（2025年底）"},
    ],
    "伊朗": [
        {"date": "2026-03-23", "title": "伊朗警告若美威胁兑现将'完全关闭'霍尔木兹海峡", "content": "3月23日CBS News报道，伊朗军方称若美国攻击其发电厂，将完全关闭霍尔木兹海峡直至设施重建。伊朗被曝向部分油轮收取200万美元过境费"},
        {"date": "2026-03-23", "title": "伊朗被曝向部分油轮收取200万美元过境费", "content": "3月23日Fox News报道，伊朗议员称已开始向部分通过海峡的船只收取200万美元过境费，此举被视为伊朗试图在封锁中寻求经济利益"},
        {"date": "2026-03-21", "title": "伊朗武装部队称正在霍尔木兹海峡采取'重大行动'", "content": "3月21日新浪财经报道，伊朗武装部队发言人表示正在霍尔木兹海峡采取重大行动，具体细节不明。此前伊朗外长表示海峡实际开放，仅对'伊朗的敌人'关闭"},
        {"date": "2026-03-20", "title": "22国联合声明谴责伊朗袭击商船行为", "content": "3月21日Naval News报道，6国联合声明谴责伊朗，表示愿参与确保海峡安全通行。美国正组建'霍尔木兹联盟'但多方遇冷，迄今没有一个国家承诺派军舰前往"},
    ],
    "科威特": [
        {"date": "2026-03-20", "title": "科威特Mina Al Ahmadi炼油厂遭袭后起火", "content": "3月19日财联社报道，科威特最大炼油厂之一Mina Al Ahmadi遭无人机袭击起火。科威特是中东和非洲最大的LNG进口国，计划2025年10月将石油产量提高至255.9万桶/日"},
    ],
    "卡塔尔": [
        {"date": "2026-03-23", "title": "卡塔尔能源遇袭致LNG出口下降17%，年收入损失约200亿美元", "content": "3月20日财新网报道，拉斯拉凡LNG设施遭伊朗导弹袭击，设施损坏需3-5年修复，修复费用预估260亿美元。2025年卡塔尔LNG出口约8220万吨，占全球约20%，袭击导致出口能力下降17%"},
        {"date": "2026-03-20", "title": "卡塔尔能源CEO：战争若持续将影响全球GDP增长", "content": "3月15日卡塔尔能源CEO萨阿德·卡阿比警告，美伊战争可能'拖垮全球经济'，预计所有海湾地区的能源出口国将在数周内被迫停产，推升油价飙升至150美元/桶"},
    ],
    "阿曼": [
        {"date": "2026-03-20", "title": "阿曼作为唯一完全绕过霍尔木兹的主要产油国维持出口", "content": "3月18日相关报道，阿曼通过法哈尔港和杜库姆港直接出阿曼湾，完全绕过霍尔木兹海峡，是封锁期间唯一不受影响的主要产油国"},
    ],
    "巴林": [
        # 巴林暂无重大新新闻
    ],
}


def update_country_news(html_content, country_name, new_updates):
    """更新特定国家的新闻"""
    if not new_updates:
        return html_content
    
    # 构建国家名称的正则表达式（支持中文和英文）
    country_pattern = re.escape(country_name)
    
    # 查找该国家的updates数组
    # 模式：name: "国家名" ... updates: [...]
    pattern = rf'(name:\s*"{country_pattern}"[^}}]+?updates:\s*\[)(\s*\])'
    
    match = re.search(pattern, html_content, re.DOTALL)
    if not match:
        print(f"  未找到 {country_name} 的updates数组")
        return html_content
    
    # 获取现有的新闻
    updates_start = match.start(2)
    updates_end = match.end(2)
    
    # 查找updates数组的实际内容（包括已有的新闻）
    # 重新匹配以获取完整的updates数组
    full_pattern = rf'(name:\s*"{country_pattern}"[^}}]+?updates:\s*\[)([\s\S]*?)(\s*\][^\]]*\])'
    full_match = re.search(full_pattern, html_content, re.DOTALL)
    
    if not full_match:
        print(f"  无法解析 {country_name} 的updates数组")
        return html_content
    
    existing_content = full_match.group(2)
    
    # 解析现有的新闻标题（用于去重）
    existing_titles = set()
    title_matches = re.findall(r'title:\s*"([^"]+)"', existing_content)
    existing_titles.update(title_matches)
    
    # 过滤掉已存在的新闻
    unique_new_updates = []
    for update in new_updates:
        if update["title"] not in existing_titles:
            unique_new_updates.append(update)
            existing_titles.add(update["title"])
        else:
            print(f"  跳过重复新闻: {update['title'][:40]}...")
    
    if not unique_new_updates:
        print(f"  {country_name}: 没有新新闻需要添加")
        return html_content
    
    # 构建新的updates数组内容
    # 将新新闻添加到最前面（按时间倒序）
    new_entries = []
    for update in unique_new_updates:
        entry = f'''\n                        {{ date: "{update['date']}", title: "{update['title']}", content: "{update['content']}" }},'''
        new_entries.append(entry)
    
    # 组合新内容
    new_content = ''.join(new_entries) + existing_content
    
    # 替换原内容
    new_html = html_content[:full_match.start(2)] + new_content + html_content[full_match.end(2):]
    
    print(f"  {country_name}: 添加了 {len(unique_new_updates)} 条新新闻")
    return new_html


def main():
    print("=" * 60)
    print("更新海湾原油图谱网页 - 各国最新动态")
    print("=" * 60)
    
    # 读取现有HTML
    html_file = WORKDIR / "index.html"
    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()
    
    print(f"\n已读取文件: {html_file}")
    print(f"文件大小: {len(html_content)} 字符\n")
    
    # 更新每个国家的新闻
    updated_content = html_content
    total_added = 0
    
    for country, news_list in NEW_NEWS.items():
        print(f"正在更新 {country}...")
        updated_content = update_country_news(updated_content, country, news_list)
    
    # 保存更新后的文件
    backup_file = WORKDIR / f"index.html.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    with open(backup_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"\n已创建备份: {backup_file}")
    
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(updated_content)
    print(f"已保存更新: {html_file}")
    
    print("\n" + "=" * 60)
    print("更新完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
