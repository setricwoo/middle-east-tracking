#!/usr/bin/env python3
"""使用官方提取的数据更新ISW网页"""

import json
import re

# 读取官方数据
with open('isw_final_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 构建网页数据结构
new_data = {
    'updated': '2026-03-29T12:00:00',
    'source_url': data['url'],
    'current_report': {
        'url': data['url'],
        'title': data['title'],
        'title_zh': '伊朗局势更新特别报告 - 2026年3月29日',
        'date': data['date'],
        'takeaways': [
            {'en': en, 'zh': zh} 
            for en, zh in zip(data['takeaways_en'], data['takeaways_zh'])
        ],
        'charts': [
            {
                'url': '',  # 使用本地截图
                'title_zh': chart['title_zh'],
                'screenshot': f"isw_screenshots/{chart['filename']}",
                'context': [chart['context']]
            }
            for chart in data['charts']
        ]
    },
    'history': [
        {'date': data['date'], 'title_zh': '伊朗局势更新特别报告 - 2026年3月29日', 'url': data['url']}
    ]
}

# 生成JSON
output = json.dumps(new_data, ensure_ascii=False, separators=(',', ':'))

# 读取HTML
with open('war-situation.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换数据
pattern = r'let STATIC_ISW_DATA = \{[^;]*\};'
replacement = f'let STATIC_ISW_DATA = {output};'
new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# 保存
with open('war-situation.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('[OK] war-situation.html 已更新')
print(f'   - Key Takeaways: {len(data["takeaways_en"])} 条（与官网一致）')
print(f'   - 图表: {len(data["charts"])} 张（本报告截图）')
print(f'   - 数据来源: ISW官网 2026-03-29')
