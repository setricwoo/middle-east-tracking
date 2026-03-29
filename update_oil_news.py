#!/usr/bin/env python3
"""
更新oil-chart.html中的最新动态
添加新的能源新闻，避免重复
"""

import re
from datetime import datetime

# 新收集的新闻数据
new_updates = {
    "沙特阿拉伯": [
        { "date": "2026-03-29", "title": "沙特军队保持全面戒备，防御伊朗持续袭击", "content": "3月29日沙特国防部表示，军队保持全面戒备状态，防空系统24小时运作。过去一周沙特拦截了超过200架伊朗无人机和数十枚弹道导弹，成功保护了Ras Tanura、Yanbu等关键能源设施" },
        { "date": "2026-03-28", "title": "沙特通过红海延布港出口创纪录", "content": "3月28日数据显示，沙特每日通过红海延布港出口的石油装载量已超400万桶，目标是每天500万桶（战前出口量的70%）。东西管道满负荷运行，成为绕开霍尔木兹海峡的生命线" },
        { "date": "2026-03-19", "title": "沙特Samref炼油厂遭伊朗无人机袭击起火", "content": "3月19日沙特国防部确认，伊朗无人机袭击了位于延布的Samref炼油厂（沙特阿美与埃克森美孚合资），无人机碎片坠落引发火灾。该炼油厂日产能40万桶，已被列入伊朗报复目标清单" },
        { "date": "2026-03-07", "title": "沙特防空系统拦截16架针对Shaybah油田的无人机", "content": "3月7日沙特国防部报告，防空系统在Empty Quarter拦截了16架针对Shaybah油田的伊朗无人机，分四波来袭。Shaybah油田是沙特最重要的'超巨型'油田之一，日产原油85万桶" },
        { "date": "2026-03-02", "title": "沙特Ras Tanura炼油厂遭袭后关闭，布伦特原油飙升10%", "content": "3月2日沙特阿美关闭Ras Tanura炼油厂（日产能55万桶），此前伊朗无人机袭击导致设施起火。该炼油厂是中东最大炼油厂之一，也是全球最大石油出口港。布伦特原油期货应声飙升约10%" },
    ],
    "伊拉克": [
        { "date": "2026-03-25", "title": "伊拉克南部产量骤降至90万桶/日，寻求库尔德管道替代出口", "content": "3月20日伊拉克石油部长宣布，南部巴士拉省产量已从330万桶/日骤降至90万桶/日，总产量降至140万桶/日。伊拉克正加速谈判，希望通过库尔德地区的伊拉克-土耳其管道恢复出口" },
        { "date": "2026-03-18", "title": "伊拉克恢复通过库尔德管道向土耳其出口原油", "content": "3月18日在美国斡旋下，伊拉克联邦政府与库尔德地区政府达成协议，恢复通过伊拉克-土耳其管道向杰伊汉港出口原油。首批约20万桶/日原油已开始流动，为霍尔木兹封锁提供替代出路" },
    ],
    "伊朗": [
        { "date": "2026-03-21", "title": "伊朗导弹袭击以色列海法炼油厂，回应以方袭击伊能源设施", "content": "3月8日伊朗伊斯兰革命卫队使用Kheibar Shekan固体燃料弹道导弹袭击以色列海法Bazan集团炼油厂。伊朗官员称此举回应以色列对伊朗石油储存设施的袭击。该炼油厂是以色列最大炼油厂，与印度有合作关系" },
        { "date": "2026-03-19", "title": "以色列袭击伊朗South Pars气田，伊朗威胁打击海湾能源设施", "content": "3月18日以色列无人机袭击伊朗South Pars气田（与卡塔尔共享的世界最大天然气田）和Asaluyeh天然气处理厂，损坏四座处理平台。伊朗随后发出警告，将打击沙特、阿联酋和卡塔尔的五处关键能源设施作为报复" },
        { "date": "2026-03-19", "title": "伊朗石油部长致信联合国：美以袭击等于对伊朗发动全面战争", "content": "3月19日伊朗石油部长致信联合国秘书长，谴责美以袭击伊朗能源基础设施，称这'等同于对伊朗能源安全与经济发动全面战争'。伊朗要求国际社会谴责这种'国家恐怖主义'行为" },
    ],
    "卡塔尔": [
        { "date": "2026-03-29", "title": "卡塔尔Ras Laffan天然气设施修复需3-5年，损失超260亿美元", "content": "3月29日卡塔尔能源公司评估，Ras Laffan工业城遭伊朗导弹袭击造成的损坏修复需要3-5年时间，修复费用预估260亿美元。17%的LNG产能受损，可能导致每年数百亿美元收入损失" },
        { "date": "2026-03-19", "title": "卡塔尔Ras Laffan遭伊朗导弹袭击，Shell的Pearl GTL设施受损", "content": "3月19日伊朗对卡塔尔Ras Laffan工业城发动导弹袭击，造成'广泛破坏'。卡塔尔能源公司证实多个LNG设施被击中起火，Shell运营的Pearl气转液设施受损。这是卡塔尔自3月2日停产以来首次遭遇直接军事打击" },
        { "date": "2026-03-19", "title": "卡塔尔驱逐伊朗军事外交官，强烈谴责袭击", "content": "3月19日卡塔尔外交部下令伊朗军事和安全武官及其 staff 在24小时内离境。卡塔尔强烈谴责伊朗对Ras Laffan的袭击，称这是'对卡塔尔国家安全的直接威胁'，保留采取进一步措施的权利" },
    ],
    "阿联酋": [
        { "date": "2026-03-29", "title": "阿联酋Habshan天然气设施重启评估中，ADNOC启动应急预案", "content": "3月29日阿联酋ADNOC表示，Habshan天然气处理设施（日处理能力61亿标准立方英尺）在3月19日遭袭后仍处于关闭状态，正在进行全面安全评估。ADNOC已启动应急预案，确保国内天然气供应" },
        { "date": "2026-03-19", "title": "阿联酋Habshan天然气设施和Bab油田遭导弹碎片击中，设施关闭", "content": "3月19日阿联酋当局报告，Habshan天然气设施和Bab油田因拦截导弹的碎片坠落而受损，已关闭相关设施。Habshan是世界最大天然气处理设施之一，由ADNOC运营。阿联酋表示无人员伤亡" },
    ],
    "科威特": [
        { "date": "2026-03-19", "title": "科威特两座炼油厂遭伊朗无人机袭击起火，KPC宣布部分停产", "content": "3月19日科威特石油公司(KPC)报告，Mina al-Ahmadi炼油厂（日产能34.6万桶）和Mina Abdullah炼油厂（日产能45.4万桶）遭伊朗无人机袭击，两个运营单元起火。KPC宣布部分停产，成品油出口受限" },
        { "date": "2026-03-06", "title": "科威特宣布因储油饱和将停产，海峡封锁导致无法出口", "content": "3月6日科威特宣布因原油储存设施即将饱和，将被迫停产。由于霍尔木兹海峡封锁，科威特无法出口原油，储罐预计在两周内填满。这是海湾国家首次因储存能力限制而宣布停产" },
    ],
    "巴林": [
        { "date": "2026-03-29", "title": "巴林Sitra炼油厂部分恢复运营，仍处不可抗力状态", "content": "3月29日巴林石油公司(Bapco)表示，Sitra炼油厂在3月9日遭伊朗袭击后，经过紧急检修，部分生产单元已恢复运营，日处理能力恢复至约15万桶/日，但仍处于不可抗力状态，成品油出口暂停" },
        { "date": "2026-03-19", "title": "巴林铝业减产扩大至35%，部分生产线完全停产", "content": "3月19日巴林铝业公司(Alba)宣布减产幅度已从19%扩大至35%，部分生产线完全停产。霍尔木兹海峡封锁导致氧化铝和电力供应均受到影响。Alba是全球最大铝冶炼厂之一，年产量约150万吨" },
    ],
    "阿曼": [
        { "date": "2026-03-29", "title": "阿曼杜库姆港成为替代出口通道，吞吐量增加40%", "content": "3月29日阿曼港务局报告，杜库姆港(Duqm)作为绕过霍尔木兹海峡的替代出口通道，过去两周吞吐量增加40%。多艘油轮改道至杜库姆港装载原油，再通过陆路运输至港口出口" },
    ],
}

def read_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def update_country_news(content, country, updates):
    """更新特定国家的新闻"""
    # 构建正则表达式来查找该国家的updates数组
    # 模式：找到国家名称后的updates: [ ... ]
    pattern = rf'(name:\s*"{re.escape(country)}".*?updates:\s*\[)(.*?)(\])'
    
    match = re.search(pattern, content, re.DOTALL)
    if not match:
        print(f"  未找到 {country} 的updates")
        return content
    
    existing_content = match.group(2)
    
    # 检查重复（基于日期和标题）
    existing_entries = []
    for u in updates:
        # 检查是否已存在相同日期和标题的新闻
        date_title = f'"{u["date"]}"'
        title = u['title'][:30]  # 取前30个字符比较
        if date_title in existing_content and title in existing_content:
            print(f"    跳过重复: {u['date']} - {u['title'][:30]}")
            continue
        existing_entries.append(u)
    
    if not existing_entries:
        print(f"  {country}: 没有新新闻需要添加")
        return content
    
    # 构建新的updates条目
    new_entries_str = ""
    for u in existing_entries:
        new_entries_str += f'\n                        {{ date: "{u["date"]}", title: "{u["title"]}", content: "{u["content"]}" }},'
    
    # 在数组开头插入新条目（保持时间倒序）
    updated_content = match.group(1) + new_entries_str + match.group(2) + match.group(3)
    
    # 替换原内容
    new_full_content = content[:match.start()] + updated_content + content[match.end():]
    
    print(f"  {country}: 添加 {len(existing_entries)} 条新闻")
    return new_full_content

def main():
    filepath = "oil-chart.html"
    content = read_file(filepath)
    
    print("开始更新各国能源新闻...\n")
    
    for country, updates in new_updates.items():
        content = update_country_news(content, country, updates)
    
    write_file(filepath, content)
    print("\n更新完成!")

if __name__ == "__main__":
    main()
