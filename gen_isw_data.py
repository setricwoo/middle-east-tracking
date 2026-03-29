import json

# 读取最新的ISW数据
with open('isw_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 获取最新文章
latest = data['articles'][0]

# 构建新的数据结构
new_data = {
    'updated': data.get('updated', ''),
    'source_url': latest['url'],
    'current_report': {
        'url': latest['url'],
        'title': latest['title'],
        'title_zh': latest['title'],
        'date': latest['date'],
        'takeaways': [
            {'en': en, 'zh': zh} 
            for en, zh in zip(latest['takeaways_en'], latest['takeaways_zh'])
        ],
        'charts': [
            {
                'url': c['original_url'],
                'title_zh': c['alt_zh'] or '图表',
                'screenshot': c.get('screenshot', '').replace('\\', '/'),
                'context': [ctx.get('text_zh', '') for ctx in c.get('context', []) if ctx.get('text_zh')]
            }
            for c in latest.get('charts', [])
        ]
    },
    'history': [
        {'date': a['date'], 'title_zh': a.get('title_zh', a['title']), 'url': a['url']}
        for a in data['articles'][:5]
    ]
}

# 输出为JSON字符串
output = json.dumps(new_data, ensure_ascii=False, separators=(',', ':'))
with open('new_isw_data.json', 'w', encoding='utf-8') as f:
    f.write(output)

print('Data saved to new_isw_data.json')
print(f"Charts count: {len(new_data['current_report']['charts'])}")
