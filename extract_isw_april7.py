#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""提取ISW 4月7日报告内容"""

import re
import json
from html import unescape

with open('temp_april7.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 提取标题
title_match = re.search(r'<title>(.*?)</title>', html)
title = title_match.group(1) if title_match else "Iran Update Special Report, April 7, 2026"

print("=== 报告标题 ===")
print(title)
print()

# 提取Key Takeaways - 在<h2>Key Takeaways</h2>后的<ol>或<ul>中
# 使用data-id="key-takeaways"定位
kt_pattern = re.compile(r'data-id="key-takeaways".*?(?:<ol[^>]*>|<ul[^>]*>)(.*?)</(?:ol|ul)>', re.DOTALL | re.IGNORECASE)
kt_match = kt_pattern.search(html)

takeaways = []
if kt_match:
    list_content = kt_match.group(1)
    # 提取列表项
    li_items = re.findall(r'<li[^>]*>(.*?)</li>', list_content, re.DOTALL)
    print(f"=== Key Takeaways ({len(li_items)}项) ===")
    for i, item in enumerate(li_items, 1):
        # 清理HTML标签
        clean_text = re.sub(r'<[^>]+>', ' ', item)
        clean_text = unescape(clean_text).strip()
        # 清理多余空格
        clean_text = re.sub(r'\s+', ' ', clean_text)
        if clean_text:
            takeaways.append(clean_text)
            print(f"{i}. {clean_text[:400]}...")
            print()
else:
    print("未找到Key Takeaways")

# 提取所有图片URL - 只保留1024x768或scaled版本（排除缩略图）
print("=== 图表图片 ===")
all_images = re.findall(r'https://understandingwar\.org/wp-content/uploads/2026/04/[^"\'>\s]+\.webp', html)

# 去重并筛选主要图片（排除小尺寸缩略图）
unique_images = []
seen_base = set()
for url in all_images:
    base = url.replace('-1024x768', '').replace('-768x576', '').replace('-300x225', '').replace('-1536x1152', '').replace('-2048x1536', '').replace('-scaled', '')
    if base not in seen_base:
        seen_base.add(base)
        # 优先使用1024x768版本
        if '-1024x768' in url:
            unique_images.append(url)
        elif '-scaled' in url and not any(x in url for x in ['-300', '-768', '-1536', '-2048']):
            unique_images.append(url)
        elif '-300' not in url and '-768' not in url and '-1536' not in url and '-2048' not in url:
            unique_images.append(url)

# 如果有遗漏的，补充1024x768版本
final_images = []
for url in unique_images:
    if '-scaled' in url:
        # 尝试找对应的1024x768版本
        base = url.replace('-scaled', '')
        found = False
        for u in all_images:
            if base.replace('.webp', '-1024x768.webp') == u:
                final_images.append(u)
                found = True
                break
        if not found:
            final_images.append(url)
    else:
        final_images.append(url)

final_images = list(set(final_images))
final_images.sort()

print(f"找到 {len(final_images)} 张主要图表:")
for i, url in enumerate(final_images, 1):
    filename = url.split('/')[-1]
    print(f"{i}. {filename}")

# 保存结果
result = {
    "title": title,
    "date": "2026-04-07",
    "url": "https://understandingwar.org/research/middle-east/iran-update-special-report-april-7-2026/",
    "takeaways": takeaways,
    "charts": final_images
}

with open('isw_april7_extracted.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"\n已保存到 isw_april7_extracted.json")
print(f"Key Takeaways: {len(takeaways)}项")
print(f"图表: {len(final_images)}张")
