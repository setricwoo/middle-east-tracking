#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
按章节提取ISW报告内容
"""
import re
import json
from html import unescape

with open('isw_report_full.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 移除script和style
content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)

# 文章主体
article_match = re.search(r'<article[^>]*>(.*?)</article>', content, re.DOTALL)
if not article_match:
    print("未找到article")
    exit()

article = article_match.group(1)

# 提取所有文本元素
elements = []
for match in re.findall(r'<(h[234]|p|li)[^>]*>(.*?)</\1>', article, re.DOTALL):
    tag, html = match
    text = re.sub(r'<[^>]+>', ' ', html)
    text = unescape(text).strip()
    text = re.sub(r'\s+', ' ', text)
    if text:
        elements.append((tag, text))

# 查找各个章节
sections = {
    'key_takeaways': [],
    'toplines': [],
    'us_israeli_air_campaign': [],
    'iranian_response': [],
    'israeli_hezbollah': []
}

current_section = None
for tag, text in elements:
    # 检测章节标题
    if 'Key Takeaways' in text:
        current_section = 'key_takeaways'
        continue
    elif 'Toplines' in text and len(text) < 50:
        current_section = 'toplines'
        continue
    elif ('US and Israeli Air Campaign' in text or 'US-Israeli Air Campaign' in text) and len(text) < 100:
        current_section = 'us_israeli_air_campaign'
        continue
    elif 'Iranian Response' in text and len(text) < 50:
        current_section = 'iranian_response'
        continue
    elif ('Israeli Campaign Against Hezbollah' in text or 'Hezbollah Response' in text) and len(text) < 100:
        current_section = 'israeli_hezbollah'
        continue
    elif any(x in text for x in ['Other Axis', 'Other Activity', 'Endnotes']) and len(text) < 50:
        current_section = None
        continue
    
    # 收集内容
    if current_section and tag in ('p', 'li') and len(text) > 50:
        sections[current_section].append(text)

# 输出结果
print("="*60)
print("ISW报告内容提取")
print("="*60)

for section_name, items in sections.items():
    print(f"\n【{section_name.upper()}】 - {len(items)} 条")
    for i, item in enumerate(items[:5], 1):  # 显示前5条
        print(f"{i}. {item[:200]}...")
    if len(items) > 5:
        print(f"... 还有 {len(items)-5} 条")

# 合并所有Key Takeaways
all_takeaways = []
for section_name, items in sections.items():
    if items:  # 只添加非空章节
        all_takeaways.extend(items)

print(f"\n\n总计: {len(all_takeaways)} 条内容")

# 保存
with open('isw_all_content.json', 'w', encoding='utf-8') as f:
    json.dump(sections, f, ensure_ascii=False, indent=2)

print("已保存到 isw_all_content.json")
