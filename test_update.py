#!/usr/bin/env python3
import json
import re
from pathlib import Path

WORKDIR = Path(__file__).parent.resolve()

# 读取人工翻译的数据
with open('isw_translation_manual.json', 'r', encoding='utf-8') as f:
    trans = json.load(f)

# 构建takeaways（Key Takeaways 4条 + Toplines 11条）
all_takeaways = []

# 添加Key Takeaways
for en, zh in zip(trans['takeaways_en'], trans['takeaways_zh']):
    all_takeaways.append({'en': en, 'zh': zh, 'type': 'key'})

# 添加Toplines
for en, zh in zip(trans['toplines_en'], trans['toplines_zh']):
    all_takeaways.append({'en': en, 'zh': zh, 'type': 'topline'})

print(f'总takeaways: {len(all_takeaways)}')
for i, t in enumerate(all_takeaways, 1):
    print(f'{i}. [{t["type"]}] {t["zh"][:50]}...')
