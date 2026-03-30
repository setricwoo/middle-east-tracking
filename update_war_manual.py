#!/usr/bin/env python3
"""人工翻译后的ISW数据更新到网页"""

import json
import re
from pathlib import Path

WORKDIR = Path(__file__).parent.resolve()

# 读取人工翻译的数据
with open('isw_translation_manual.json', 'r', encoding='utf-8') as f:
    trans = json.load(f)

# 构建网页数据结构
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
                'url': f"https://understandingwar.org/wp-content/uploads/2026/03/{chart['title_en'].replace(' ', '-').replace('/', '-')}.webp",
                'title_zh': chart['title_zh'],
                'screenshot': f"isw_screenshots/chart_20260330_{i+1:02d}.png",
                'context': chart['context_zh']
            }
            for i, chart in enumerate(trans['charts'])
        ]
    },
    'history': [
        {'date': trans['date'], 'title_zh': '伊朗局势更新特别报告 - 2026年3月29日', 'url': trans['url']}
    ]
}

# 保存JSON
output = json.dumps(new_data, ensure_ascii=False, separators=(',', ':'))

# 更新 HTML
with open('war-situation.html', 'r', encoding='utf-8') as f:
    content = f.read()

pattern = r'(let STATIC_ISW_DATA = ).*?(;</script>)'
replacement = r'\1' + output + r'\2'
new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open('war-situation.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('[OK] war-situation.html 已更新')
print(f'   - Key Takeaways: {len(new_data["current_report"]["takeaways"])} 条')
print(f'   - 图表: {len(new_data["current_report"]["charts"])} 张')
print(f'   - 已人工翻译')
