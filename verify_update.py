#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import re

with open('war-situation.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 使用正则提取JSON数据
match = re.search(r'let STATIC_ISW_DATA = (\{[\s\S]*?\n\};)', html)
if match:
    json_str = match.group(1).rstrip(';')
    data = json.loads(json_str)
    
    print('=== Report Info ===')
    print('Title:', data['current_report']['title'])
    print('Title ZH:', data['current_report'].get('title_zh', 'N/A'))
    print('Date:', data['current_report']['date'])
    print()
    print('=== Key Takeaways (%d items) ===' % len(data['current_report']['takeaways']))
    for i, t in enumerate(data['current_report']['takeaways'], 1):
        zh = t.get('zh', '')[:80]
        print('%d. %s...' % (i, zh))
    print()
    print('=== Charts (%d items) ===' % len(data['current_report']['charts']))
    for i, c in enumerate(data['current_report']['charts'], 1):
        title = c.get('title_zh', c.get('url', '').split('/')[-1])[:50]
        print('%d. %s' % (i, title))
else:
    print('Could not find STATIC_ISW_DATA')
