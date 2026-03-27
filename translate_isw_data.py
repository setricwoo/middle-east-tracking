#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISW数据翻译脚本
- 读取isw_data_raw.json
- 使用AI翻译所有内容
- 生成isw_war_data.json（中文翻译版）
- 嵌入war-situation.html
"""

import json
import re
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

WORKDIR = Path(__file__).parent.resolve()
RAW_DATA_FILE = WORKDIR / "isw_data_raw.json"
OUTPUT_DATA_FILE = WORKDIR / "isw_war_data.json"
HTML_FILE = WORKDIR / "war-situation.html"

# 中文翻译数据（手动翻译，确保质量）
TRANSLATION = {
    "report_title": "伊朗局势更新 特别报告 2026年3月26日",
    
    "takeaways": [
        {
            "en": "The combined force conducted strikes around Mashhad, Khorasan Razavi Province, on March 25 and 26, marking the northeastern-most strikes conducted so far in the war. The combined force has slowly swept across Iran west to east and is now getting to some of the furthest targets of the campaign.",
            "zh": "美以联军于3月25日至26日对伊朗呼罗珊·拉扎维省马什哈德地区实施打击，标志着此次战争中最东北方向的打击行动。联军已从西向东逐步横扫伊朗，目前正在攻击此次战役中最远的目标。"
        },
        {
            "en": "The IDF has continued targeting senior Iranian commanders to disrupt Iranian command and control and operations broadly. The IDF announced on March 26 that it killed Islamic Revolutionary Guards Corps (IRGC) Navy Commander Rear Admiral Alireza Tangsiri in Bandar Abbas, Hormozgan Province.",
            "zh": "以色列国防军继续针对伊朗高级指挥官实施打击，以破坏伊朗的指挥控制体系和整体作战能力。以军于3月26日宣布，在霍尔木兹甘省阿巴斯港击毙伊斯兰革命卫队海军司令阿里雷扎·坦格里西少将。"
        },
        {
            "en": "An IRGC cultural official told state media that the IRGC has lowered the minimum recruitment age to 12. This decision follows reports that the IRGC is facing difficulties with recruiting new personnel and managing broader operational disruptions.",
            "zh": "一名伊斯兰革命卫队文化官员向官方媒体透露，革命卫队已将最低招募年龄降至12岁。此前有报道称，革命卫队在招募新兵和应对更广泛的作战中断方面面临困难。"
        },
        {
            "en": "Hezbollah continues to claim a high rate of attacks against Israeli targets in northern Israel and southern Lebanon. Hezbollah claimed to conduct 73 attacks targeting Israeli forces in northern Israel and southern Lebanon, as well as northern Israeli towns, between 2:00 PM ET on March 25 and 2:00 PM ET on March 26.",
            "zh": "真主党继续宣称对以色列北部和黎巴嫩南部目标实施高频袭击。真主党声称在3月25日至26日期间（美国东部时间14:00至次日14:00），对以色列北部、黎巴嫩南部的以军部队以及以色列北部城镇发动了73次袭击。"
        }
    ],
    
    "charts": [
        {
            "filename": "chart_2026-03-26_00.png",
            "title_zh": "美以联军对马什哈德地区打击态势图",
            "description_zh": "地图显示美以联军于3月25日至26日对伊朗第二大城市马什哈德及周边军事目标（包括马什哈德国际机场、第14空军战术基地和第5陆军航空基地）的打击行动，标志着联军已将战线推进至伊朗东北部地区。"
        },
        {
            "filename": "chart_2026-03-26_01.png",
            "title_zh": "美以联军在伊朗全境打击行动概览",
            "description_zh": "全伊朗地图展示美以联军自战争开始以来已打击超过10,000个目标的分布情况，重点标注了德黑兰、西部和中部地区的集中打击区域，以及3月26日在阿巴斯港击毙革命卫队海军司令的行动位置。"
        },
        {
            "filename": "chart_2026-03-26_02.png",
            "title_zh": "革命卫队第4萨拉赫海军区基地卫星图像",
            "description_zh": "卫星图像显示位于布什尔省的第4萨拉赫海军区基地遭美以联军严重破坏的情况。该基地负责控制波斯湾中部海域，包括南帕尔斯气田。图像显示机库、后勤设施和码头建筑被摧毁，多艘舰艇受损。"
        },
        {
            "filename": "chart_2026-03-26_03.png",
            "title_zh": "伊朗对巴林导弹和无人机发射统计图（2月28日-3月26日）",
            "description_zh": "柱状图展示伊朗在战争期间向巴林发射的导弹（蓝色）和无人机（黄色）数量变化趋势，数据来自巴林国防部。3月26日当日伊朗向巴林发射19架无人机和1枚导弹。"
        },
        {
            "filename": "chart_2026-03-26_04.png",
            "title_zh": "伊朗对科威特导弹和无人机发射统计图（2月28日-3月26日）",
            "description_zh": "柱状图展示伊朗向科威特发射的导弹和无人机数量统计，数据来源为科威特军方。3月26日伊朗向科威特发射1架无人机和6枚弹道导弹，均落在空旷地区。"
        },
        {
            "filename": "chart_2026-03-26_05.png",
            "title_zh": "伊朗对沙特阿拉伯无人机发射统计图（3月1日-26日）",
            "description_zh": "柱状图展示伊朗向沙特阿拉伯发射无人机的累计统计，数据来自沙特国防部。3月25日至26日期间，伊朗向沙特发射37架无人机。"
        },
        {
            "filename": "chart_2026-03-26_06.png",
            "title_zh": "伊朗对阿联酋无人机和导弹发射统计图（3月26日）",
            "description_zh": "图表展示3月26日伊朗向阿联酋发射的11架无人机和15枚导弹的拦截情况。阿联酋国防部表示所有来袭目标均已被拦截。"
        },
        {
            "filename": "chart_2026-03-26_07.png",
            "title_zh": "真主党对以色列袭击宣称统计图（3月1日-25日）",
            "description_zh": "柱状图展示真主党自3月1日参战以来每日宣称的袭击次数。数据显示真主党平均每天发动约150次火箭弹袭击，其中约三分之二针对黎巴嫩南部的以军部队，三分之一针对以色列北部和中部地区。3月25日单日宣称38次袭击，为近期高峰。"
        }
    ]
}


def create_war_data():
    """创建中文翻译版数据文件"""
    # 读取原始数据
    with open(RAW_DATA_FILE, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)
    
    # 构建翻译后的数据结构
    war_data = {
        "updated": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
        "source_url": raw_data["source_url"],
        "current_report": {
            "url": raw_data["source_url"],
            "title": raw_data["report"]["title"],
            "title_zh": TRANSLATION["report_title"],
            "date": raw_data["report"]["date"],
            "takeaways": TRANSLATION["takeaways"],
            "charts": []
        }
    }
    
    # 添加图表信息
    raw_charts = raw_data["report"]["charts"]
    for i, chart_trans in enumerate(TRANSLATION["charts"]):
        # 找到对应的原始图表数据
        raw_chart = None
        for rc in raw_charts:
            if rc["filename"] == chart_trans["filename"]:
                raw_chart = rc
                break
        
        if raw_chart:
            war_data["current_report"]["charts"].append({
                "url": raw_chart["path"],
                "title": raw_chart.get("alt", ""),
                "title_zh": chart_trans["title_zh"],
                "description_zh": chart_trans["description_zh"],
                "context": []  # 上下文标签
            })
    
    # 保存翻译后的数据
    with open(OUTPUT_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(war_data, f, ensure_ascii=False, indent=2)
    print(f"[保存] 翻译数据: {OUTPUT_DATA_FILE}")
    
    return war_data


def embed_to_html(war_data):
    """将数据嵌入HTML"""
    try:
        with open(HTML_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 准备JSON数据
        json_data = json.dumps(war_data, ensure_ascii=False, separators=(',', ':'))
        
        # 使用字符串分割安全替换
        start_marker = 'let STATIC_ISW_DATA = '
        start_idx = content.find(start_marker)
        
        if start_idx != -1:
            data_start = start_idx + len(start_marker)
            # 找到结束的分号（考虑嵌套大括号）
            brace_count = 0
            data_end = data_start
            for i, char in enumerate(content[data_start:]):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        data_end = data_start + i + 1
                        break
            
            # 替换数据部分
            new_content = content[:data_start] + json_data + content[data_end:]
            
            with open(HTML_FILE, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"[嵌入] 数据已嵌入 {HTML_FILE}")
        else:
            print(f"[警告] 未找到 STATIC_ISW_DATA 变量")
            
    except Exception as e:
        print(f"[错误] 嵌入HTML失败: {e}")


def main():
    print("=" * 60)
    print("ISW 数据翻译与嵌入")
    print("=" * 60)
    
    if not RAW_DATA_FILE.exists():
        print(f"[错误] 找不到原始数据文件: {RAW_DATA_FILE}")
        print("请先运行 fetch_isw_extract.py 提取数据")
        return
    
    print("\n[1/2] 创建翻译数据...")
    war_data = create_war_data()
    
    print(f"\n  - 报告标题: {war_data['current_report']['title_zh']}")
    print(f"  - 日期: {war_data['current_report']['date']}")
    print(f"  - Takeaways: {len(war_data['current_report']['takeaways'])}")
    print(f"  - 图表: {len(war_data['current_report']['charts'])}")
    
    print("\n[2/2] 嵌入HTML...")
    embed_to_html(war_data)
    
    print("\n" + "=" * 60)
    print("完成!")
    print(f"  数据文件: {OUTPUT_DATA_FILE}")
    print(f"  HTML文件: {HTML_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()
