import json
import re

# 读取翻译后的数据
with open('isw_data_translated.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 生成新的数据结构
new_data = {
    'updated': data['fetched'],
    'source_url': data['url'],
    'current_report': {
        'url': data['url'],
        'title': data['title'],
        'title_zh': '伊朗局势更新特别报告 - 2026年3月29日',
        'date': data['date'],
        'takeaways': [{'en': en, 'zh': zh} for en, zh in zip(data['takeaways_en'], data['takeaways_zh'])],
        'charts': [
            {
                'url': img['src'],
                'title_zh': img['title_zh'],
                'screenshot': img.get('screenshot', '').replace('\\', '/'),
                'context': img.get('context_zh', [])
            }
            for img in data['images'] if img.get('screenshot')
        ]
    },
    'history': [
        {'date': data['date'], 'title_zh': '伊朗局势更新特别报告 - 2026年3月29日', 'url': data['url']}
    ]
}

# 输出JSON
output = json.dumps(new_data, ensure_ascii=False, separators=(',', ':'))
with open('new_isw_data.json', 'w', encoding='utf-8') as f:
    f.write(output)

print('数据已保存到 new_isw_data.json')
print(f"Key Takeaways: {len(new_data['current_report']['takeaways'])} 条")
print(f"Charts: {len(new_data['current_report']['charts'])} 张")

# 更新 war-situation.html
with open('war-situation.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换 STATIC_ISW_DATA
pattern = r'(let STATIC_ISW_DATA = ).*?(;\s*</script>)'
replacement = r'\1' + output + r'\2'
new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open('war-situation.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('\nwar-situation.html 已更新')
