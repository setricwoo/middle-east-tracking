#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISW 报告翻译脚本
翻译内容：Key Takeaways + 图表标题 + 图表对应的正文
"""

import json
import re
from pathlib import Path

WORKDIR = Path(__file__).parent.resolve()
DATA_FILE = WORKDIR / "isw_data_extracted.json"
OUTPUT_FILE = WORKDIR / "isw_data_translated.json"

# 简单的关键词翻译映射
TRANSLATIONS = {
    # 军事设施
    "Military Complex": "军事综合体",
    "Missile Base": "导弹基地",
    "Missile Complex": "导弹综合体",
    "missile production": "导弹生产",
    "ballistic missile": "弹道导弹",
    "solid fuel": "固体燃料",
    "liquid fuel": "液体燃料",
    "planetary mixer": "行星混合器",
    "warhead": "弹头",
    "launch pad": "发射台",
    "tunnel": "隧道",
    "bunker": "地堡",
    
    # 组织机构
    "IDF": "以色列国防军",
    "IRGC": "伊斯兰革命卫队",
    "IRGC Aerospace": "伊斯兰革命卫队航空航天部队",
    "IRGC Ground Forces": "伊斯兰革命卫队地面部队",
    "SPND": "国防创新研究组织",
    "PMF": "人民动员力量",
    "Hezbollah": "真主党",
    "Houthis": "胡塞武装",
    
    # 地名
    "Tehran": "德黑兰",
    "Tehran Province": "德黑兰省",
    "Semnan Province": "塞姆南省",
    "Hormozgan Province": "霍尔木兹甘省",
    "Lorestan Province": "洛雷斯坦省",
    "Khuzestan Province": "胡齐斯坦省",
    "Esfahan": "伊斯法罕",
    "Esfahan Province": "伊斯法罕省",
    "Yazd": "亚兹德",
    "Yazd Province": "亚兹德省",
    "Karaj": "卡拉季",
    "Alborz Province": "阿尔博兹省",
    "Dezful": "迪兹富勒",
    "Khojir": "霍吉尔",
    "Shahroud": "沙赫鲁德",
    "Parchin": "帕尔钦",
    "Hakimiyeh": "哈基米耶",
    "Khorgu": "霍尔古",
    "Imam Ali": "伊玛目阿里",
    "Borujerd": "博鲁杰尔德",
    "South Pars": "南帕尔斯",
    "Ras Laffan": "拉斯拉凡",
    
    # 国家/地区
    "Iran": "伊朗",
    "Israel": "以色列",
    "United States": "美国",
    "Saudi Arabia": "沙特阿拉伯",
    "UAE": "阿联酋",
    "Qatar": "卡塔尔",
    "Kuwait": "科威特",
    "Bahrain": "巴林",
    "Lebanon": "黎巴嫩",
    "Syria": "叙利亚",
    "Iraq": "伊拉克",
    "Yemen": "也门",
    "Russia": "俄罗斯",
    "Turkey": "土耳其",
    "Pakistan": "巴基斯坦",
    
    # 动作/事件
    "strike": "打击",
    "airstrike": "空袭",
    "attack": "攻击",
    "destroyed": "摧毁",
    "damaged": "损坏",
    "intercepted": "拦截",
    "launched": "发射",
    "targeted": "瞄准",
    "hit": "击中",
    
    # 其他
    "satellite imagery": "卫星图像",
    "combined force": "联合部队",
    "Axis of Resistance": "抵抗轴心",
    "ceasefire": "停火",
    "evacuation": "撤离",
}


def translate_text(text):
    """简单的文本翻译"""
    if not text:
        return ""
    
    result = text
    for en, zh in TRANSLATIONS.items():
        result = result.replace(en, zh)
    
    return result


def find_context_for_image(image_title, body_texts):
    """为图片查找相关的正文内容"""
    # 提取图片标题中的关键词
    keywords = []
    
    # 常见关键词映射
    keyword_patterns = {
        "UAE": ["UAE", "United Arab Emirates", "阿联酋"],
        "Kuwait": ["Kuwait", "科威特"],
        "KSA": ["KSA", "Saudi Arabia", "沙特"],
        "Bahrain": ["Bahrain", "巴林"],
        "Hezbollah": ["Hezbollah", "真主党"],
        "Khojir": ["Khojir", "霍吉尔"],
        "Shahroud": ["Shahroud", "沙赫鲁德"],
        "Parchin": ["Parchin", "帕尔钦"],
        "Hakimiyeh": ["Hakimiyeh", "哈基米耶"],
        "Khorgu": ["Khorgu", "霍尔古"],
        "Imam Ali": ["Imam Ali", "伊玛目阿里"],
    }
    
    # 从图片标题中提取关键词
    for key, patterns in keyword_patterns.items():
        for pattern in patterns:
            if pattern.lower() in image_title.lower():
                keywords.append(key)
                break
    
    if not keywords:
        return []
    
    # 查找包含这些关键词的正文段落
    relevant_paragraphs = []
    for para in body_texts:
        for keyword in keywords:
            if keyword.lower() in para.lower():
                relevant_paragraphs.append(para)
                break
    
    # 返回最相关的2-3段
    return relevant_paragraphs[:3]


def translate_isw_data():
    """翻译ISW数据"""
    print("=" * 70)
    print("ISW 报告翻译")
    print("=" * 70)
    
    # 读取提取的数据
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    print(f"\n[信息] 报告日期: {data['date']}")
    print(f"[信息] 报告标题: {data['title']}")
    print(f"[信息] Key Takeaways: {len(data['takeaways_en'])} 条")
    print(f"[信息] 图片: {len(data['images'])} 张")
    
    # 翻译 Key Takeaways
    print("\n[翻译] Key Takeaways...")
    takeaways_zh = []
    for i, takeaway in enumerate(data['takeaways_en'], 1):
        zh = translate_text(takeaway)
        takeaways_zh.append(zh)
        print(f"  {i}/6 完成")
    
    # 处理图片
    print("\n[处理] 图片信息...")
    images_processed = []
    for i, img in enumerate(data['images'], 1):
        # 翻译标题
        title_zh = translate_text(img['title'])
        
        # 查找相关正文
        context = find_context_for_image(img['title'], data['body_text'])
        context_zh = [translate_text(c) for c in context]
        
        images_processed.append({
            "src": img['src'],
            "alt": img['alt'],
            "title_en": img['title'],
            "title_zh": title_zh,
            "screenshot": img.get('screenshot', ''),
            "context_en": context,
            "context_zh": context_zh
        })
        print(f"  {i}/{len(data['images'])}: {title_zh[:40]}...")
    
    # 构建输出数据
    output = {
        "url": data['url'],
        "title": data['title'],
        "date": data['date'],
        "takeaways_en": data['takeaways_en'],
        "takeaways_zh": takeaways_zh,
        "images": images_processed,
        "body_text": data['body_text'],
        "fetched": data['fetched'],
        "translated": "2026-03-30"
    }
    
    # 保存
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"\n[保存] 翻译完成: {OUTPUT_FILE}")
    print("=" * 70)
    
    return output


if __name__ == "__main__":
    translate_isw_data()
