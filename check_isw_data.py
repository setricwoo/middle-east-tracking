#!/usr/bin/env python3
import json

with open('isw_translation_manual.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    
print('=== ISW数据检查 ===')
print(f"报告: {data['title']}")
print(f"日期: {data['date']}")
print(f"Key Takeaways: {len(data['takeaways_en'])} 条")
print(f"Charts: {len(data['charts'])} 张")
print()

print('图表列表:')
for i, chart in enumerate(data['charts'], 1):
    print(f"{i}. {chart['title_zh']}")
    print(f"   英文: {chart['title_en'][:50]}...")
    print()
