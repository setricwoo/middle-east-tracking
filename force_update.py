#!/usr/bin/env python3
import json
import re

# 读取翻译数据
with open('isw_translation_manual.json', 'r', encoding='utf-8') as f:
    trans = json.load(f)

# 构建15条takeaways
all_takeaways = []
for en, zh in zip(trans['takeaways_en'], trans['takeaways_zh']):
    all_takeaways.append({'en': en, 'zh': zh})
for en, zh in zip(trans['toplines_en'], trans['toplines_zh']):
    all_takeaways.append({'en': en, 'zh': zh})

# 构建数据
new_data = {
    'updated': '2026-03-30T12:00:00',
    'source_url': trans['url'],
    'current_report': {
        'url': trans['url'],
        'title': trans['title'],
        'title_zh': '伊朗局势更新特别报告 - 2026年3月29日',
        'date': trans['date'],
        'takeaways': all_takeaways,
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
    'history': [{'date': trans['date'], 'title_zh': '伊朗局势更新特别报告 - 2026年3月29日', 'url': trans['url']}]
}

# 生成JSON
output = json.dumps(new_data, ensure_ascii=False, separators=(',', ':'))

# 读取HTML
with open('war-situation.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换
pattern = r'let STATIC_ISW_DATA = \{[^;]*\};'
replacement = f'let STATIC_ISW_DATA = {output};'
new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# 保存
with open('war-situation.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print(f'[OK] 已更新: {len(all_takeaways)}条内容, {len(new_data["current_report"]["charts"])}张图表')
