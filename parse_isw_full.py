#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import json
from html import unescape

with open('isw_report_full.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 移除script和style
content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
content = re.sub(r'<style[^>]*>.*?</style>', '', content, flags=re.DOTALL)

# 提取所有段落和列表项
texts = []
for match in re.findall(r'<(p|li)[^>]*>(.*?)</\1>', content, re.DOTALL):
    tag_type, html_content = match
    text = re.sub(r'<[^>]+>', ' ', html_content)
    text = unescape(text)
    text = re.sub(r'\s+', ' ', text).strip()
    if text and len(text) > 20:
        texts.append(text)

# 找到Key Takeaways的起始位置
start_idx = -1
for i, t in enumerate(texts):
    if 'Key Takeaways' in t:
        start_idx = i
        break

# 找到Toplines或下一节的结束位置
end_idx = len(texts)
for i, t in enumerate(texts[start_idx+1:], start_idx+1):
    if any(x in t for x in ['Toplines', 'US and Israeli Air Campaign', 'Iranian Response', 'Iranian Campaign Against Hezbollah']):
        if len(t) < 100:  # 节标题通常较短
            end_idx = i
            break

print(f"Key Takeaways范围: {start_idx} 到 {end_idx}")
print(f"\n共 {end_idx - start_idx - 1} 条内容\n")

# 提取Key Takeaways
takeaways = []
for t in texts[start_idx+1:end_idx]:
    # 过滤掉太短的和看起来不像Key Takeaway的内容
    if len(t) > 100 and not t.startswith('Note:') and 'institute for the study of war' not in t.lower():
        takeaways.append(t)

print(f"筛选后: {len(takeaways)} 条Key Takeaways\n")
for i, tk in enumerate(takeaways, 1):
    print(f"{i}. {tk[:300]}...\n")

# 保存
with open('isw_takeaways_raw.txt', 'w', encoding='utf-8') as f:
    for i, tk in enumerate(takeaways, 1):
        f.write(f"{i}. {tk}\n\n")

print(f"\n已保存到 isw_takeaways_raw.txt")
