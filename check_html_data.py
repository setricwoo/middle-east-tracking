#!/usr/bin/env python3
import re, json

with open('war-situation.html', 'r', encoding='utf-8') as f:
    content = f.read()

match = re.search(r'let STATIC_ISW_DATA = (.+?);</script>', content, re.DOTALL)
if match:
    data = json.loads(match.group(1))
    print(f"Takeaways: {len(data['current_report']['takeaways'])}")
    print(f"Charts: {len(data['current_report']['charts'])}")
    print("\n图表列表:")
    for i, c in enumerate(data['current_report']['charts'], 1):
        print(f"  {i}. {c['title_zh']}")
