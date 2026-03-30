#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复 ISW 数据编码问题
"""

import json
import re
from pathlib import Path

# 读取人工翻译的数据
with open('isw_translation_manual.json', 'r', encoding='utf-8') as f:
    trans = json.load(f)

# 构建正确的数据结构
new_data = {
    'updated': '2026-03-30T12:00:00',
    'source_url': trans['url'],
    'current_report': {
        'url': trans['url'],
        'title': trans['title'],
        'title_zh': '伊朗局势更新特别报告 - 2026年3月29日',
        'date': trans['date'],
        'takeaways': [
            {'en': en, 'zh': zh} 
            for en, zh in zip(trans['takeaways_en'], trans['takeaways_zh'])
        ],
        'charts': [
            {
                'url': f"https://understandingwar.org/wp-content/uploads/2026/03/chart-{i+1}.webp",
                'title_zh': chart['title_zh'],
                'screenshot': f"isw_screenshots/chart_{trans['date'].replace('-', '')}_{i+1:02d}.png",
                'context': chart['context_zh']
            }
            for i, chart in enumerate(trans['charts'])
        ]
    },
    'history': [
        {'date': trans['date'], 'title_zh': '伊朗局势更新特别报告 - 2026年3月29日', 'url': trans['url']}
    ]
}

# 确保使用 UTF-8 编码
output = json.dumps(new_data, ensure_ascii=False, separators=(',', ':'))

# 验证 JSON 有效性
try:
    json.loads(output)
    print("JSON 验证通过")
except Exception as e:
    print(f"JSON 错误: {e}")
    exit(1)

# 更新 HTML 文件
with open('war-situation.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换 STATIC_ISW_DATA
pattern = r'(let STATIC_ISW_DATA = ).*?(;</script>)'
replacement = r'\1' + output + r'\2'
new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# 写回文件
with open('war-situation.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("[OK] war-situation.html 已更新")
print(f"   - Key Takeaways: {len(new_data['current_report']['takeaways'])} 条")
print(f"   - 图表: {len(new_data['current_report']['charts'])} 张")

# 验证更新
with open('war-situation.html', 'r', encoding='utf-8') as f:
    verify = f.read()
    if '伊朗局势更新特别报告' in verify:
        print("[OK] 中文内容验证通过")
    else:
        print("[警告] 未找到中文内容")
