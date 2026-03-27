#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
转换 isw_data.json 为 isw_war_data.json
- 使用截图路径替代远程URL
- 优化翻译质量
- 添加中文解读
"""

import json
import re
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

WORKDIR = Path(__file__).parent.resolve()
SOURCE_FILE = WORKDIR / "isw_data.json"
TARGET_FILE = WORKDIR / "isw_war_data.json"
BEIJING_TZ = ZoneInfo("Asia/Shanghai")


def clean_translation(text):
    """清理翻译文本，修复中英混杂问题"""
    if not text:
        return text
    
    # 常见英文术语的中文映射
    term_mapping = {
        r'\bUS\b': '美国',
        r'\bUnited States\b': '美国',
        r'\bIran\b': '伊朗',
        r'\bIranian\b': '伊朗的',
        r'\bIsrael\b': '以色列',
        r'\bIsraeli\b': '以色列的',
        r'\bCENTCOM\b': '中央司令部',
        r'\bIRGC\b': '伊斯兰革命卫队',
        r'\bHezbollah\b': '真主党',
        r'\bHamas\b': '哈马斯',
        r'\bUAE\b': '阿联酋',
        r'\bSaudi Arabia\b': '沙特阿拉伯',
        r'\bKhamenei\b': '哈梅内伊',
        r'\bGhalibaf\b': '加利巴夫',
        r'\bIDF\b': '以色列国防军',
        r'\bwar\b': '战争',
        r'\bdrone\b': '无人机',
        r'\bmissile\b': '导弹',
        r'\bballistic missile\b': '弹道导弹',
        r'\bcruise missile\b': '巡航导弹',
        r'\bstrike\b': '打击',
        r'\battack\b': '攻击',
        r'\btarget\b': '目标',
        r'\blaunch\b': '发射',
        r'\bbase\b': '基地',
        r'\bmilitary\b': '军事',
        r'\bdefense\b': '防御',
        r'\bretaliatory\b': '报复性',
        r'\bnegotiations?\b': '谈判',
        r'\bsanctions?\b': '制裁',
        r'\boil\b': '石油',
        r'\bGulf\b': '海湾',
        r'\bMiddle East\b': '中东',
        r'\bstrait\b': '海峡',
        r'\bHormuz\b': '霍尔木兹',
        r'\bPersian Gulf\b': '波斯湾',
    }
    
    # 应用术语映射
    result = text
    for pattern, replacement in term_mapping.items():
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
    
    # 清理多余空格
    result = re.sub(r'\s+', ' ', result).strip()
    
    return result


def generate_chart_interpretation(chart_info, takeaway_texts):
    """基于图表信息和takeaways生成中文解读"""
    alt_zh = chart_info.get("alt_zh", "")
    description = chart_info.get("description_summary", "")
    
    # 从文件名或alt中提取关键信息
    url = chart_info.get("original_url", "")
    filename = url.split("/")[-1].replace(".webp", "").replace(".png", "").replace("-", " ")
    
    interpretation = []
    
    # 根据图表内容类型添加解读
    if "strike" in filename.lower() or "strike" in alt_zh:
        interpretation.append("军事打击行动示意图")
    if "launch" in filename.lower() or "发射" in alt_zh:
        interpretation.append("导弹/无人机发射轨迹")
    if "map" in filename.lower() or "地图" in alt_zh:
        interpretation.append("战场态势分布")
    if "iranian" in filename.lower() or "伊朗" in alt_zh:
        interpretation.append("伊朗方面行动")
    if "us" in filename.lower() or "israel" in filename.lower() or "美以" in alt_zh:
        interpretation.append("美以联军行动")
    
    # 如果没有提取到具体信息，使用通用标签
    if not interpretation:
        interpretation = ["ISW战略分析", "战场态势图"]
    
    return interpretation[:3]  # 最多返回3个标签


def convert_article(article):
    """转换单篇文章数据"""
    
    # 转换 takeaways
    takeaways_en = article.get("takeaways_en", [])
    takeaways_zh_raw = article.get("takeaways_zh", [])
    
    takeaways = []
    for i, en_text in enumerate(takeaways_en):
        zh_text = takeaways_zh_raw[i] if i < len(takeaways_zh_raw) else ""
        # 清理翻译
        zh_clean = clean_translation(zh_text)
        
        takeaways.append({
            "en": en_text,
            "zh": zh_clean
        })
    
    # 转换图表 - 使用截图路径
    charts = []
    charts_data = article.get("charts", [])
    all_images = article.get("all_images", [])
    
    for chart in charts_data:
        screenshot_path = chart.get("screenshot", "")
        
        # 如果有截图，使用截图路径；否则使用原始URL
        if screenshot_path and Path(WORKDIR / screenshot_path).exists():
            display_url = screenshot_path.replace("\\", "/")
        else:
            display_url = chart.get("original_url", "")
        
        # 生成解读标签
        context = generate_chart_interpretation(chart, takeaways_en)
        
        # 清理标题翻译
        alt_zh = clean_translation(chart.get("alt_zh", ""))
        
        charts.append({
            "url": display_url,
            "title": chart.get("alt_en", ""),
            "title_zh": alt_zh or "战场态势图",
            "context": context
        })
    
    return {
        "url": article.get("url", ""),
        "title": article.get("title", ""),
        "title_zh": clean_translation(article.get("title", "")),
        "date": article.get("date", ""),
        "takeaways": takeaways,
        "charts": charts
    }


def convert_history(articles):
    """转换历史记录"""
    history = []
    for article in articles[1:4]:  # 最多3条历史记录
        history.append({
            "date": article.get("date", ""),
            "title": article.get("title", ""),
            "title_zh": clean_translation(article.get("title", "")),
            "url": article.get("url", "")
        })
    return history


def main():
    # 读取源数据
    if not SOURCE_FILE.exists():
        print(f"[错误] 找不到源文件: {SOURCE_FILE}")
        return
    
    with open(SOURCE_FILE, "r", encoding="utf-8") as f:
        source_data = json.load(f)
    
    articles = source_data.get("articles", [])
    if not articles:
        print("[错误] 没有找到文章数据")
        return
    
    # 转换最新文章
    latest = convert_article(articles[0])
    
    # 转换历史记录
    history = convert_history(articles)
    
    # 构建目标数据结构
    target_data = {
        "updated": datetime.now(BEIJING_TZ).isoformat(),
        "source_url": latest["url"],
        "current_report": latest,
        "history": history
    }
    
    # 保存
    with open(TARGET_FILE, "w", encoding="utf-8") as f:
        json.dump(target_data, f, ensure_ascii=False, indent=2)
    
    print(f"[完成] 已转换 {len(latest['takeaways'])} 条 takeaways, {len(latest['charts'])} 张图表")
    print(f"[保存] {TARGET_FILE}")


if __name__ == "__main__":
    main()
