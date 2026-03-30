#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import json
from html import unescape

with open('isw_report_full.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 提取article内容
article_match = re.search(r'<article[^>]*>(.*?)</article>', content, re.DOTALL)
if not article_match:
    print("未找到article")
    exit()

article = article_match.group(1)

# 找到Key Takeaways位置
kt_pos = article.find('Key Takeaways')
if kt_pos < 0:
    print("未找到Key Takeaways")
    exit()

print(f"[找到] Key Takeaways 在article中位置: {kt_pos}")

# 提取Key Takeaways部分（到Toplines之前）
kt_section = article[kt_pos:]
toplines_pos = kt_section.find('Toplines')
if toplines_pos > 0:
    kt_section = kt_section[:toplines_pos]

# 提取所有段落和列表项
texts = []
for match in re.findall(r'<(p|li)[^>]*>(.*?)</\1>', kt_section, re.DOTALL):
    tag, html = match
    # 清理HTML
    text = re.sub(r'<[^>]+>', ' ', html)
    text = unescape(text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 过滤条件
    if len(text) > 80 and not any(x in text for x in ['Skip to', 'Menu', 'Jump to']):
        texts.append(text)

print(f"\n[提取] {len(texts)} 条内容:\n")
for i, t in enumerate(texts, 1):
    print(f"{i}. {t[:400]}...\n")

# 保存
with open('isw_key_takeaways.json', 'w', encoding='utf-8') as f:
    json.dump({'takeaways': texts}, f, ensure_ascii=False, indent=2)

print(f"[保存] 已保存 {len(texts)} 条到 isw_key_takeaways.json")
