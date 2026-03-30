#!/usr/bin/env python3
import json

with open('isw_translation_manual.json', 'r', encoding='utf-8') as f:
    d = json.load(f)

print(f'Key Takeaways: {len(d["takeaways_en"])}')
print(f'Toplines: {len(d["toplines_en"])}')
print(f'Charts: {len(d["charts"])}')

# 列出所有图表
for i, c in enumerate(d['charts'], 1):
    print(f'  {i}. {c["title_zh"]}')
