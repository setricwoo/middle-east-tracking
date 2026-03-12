#!/usr/bin/env python3
import re
import json

with open('iran_page.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 查找所有的市场slug
slugs = set(re.findall(r'[\'"](/event/[^/\'"\s\?]+)', html))
print('找到的事件slug:')
for s in sorted(slugs)[:30]:
    print(f'  {s}')

# 查找JSON数据
json_matches = re.findall(r'window\.__APP_DATA__\s*=\s*({.+?});', html, re.DOTALL)
if json_matches:
    print(f'\n找到 {len(json_matches)} 个JSON数据块')
    # 尝试解析
    try:
        data = json.loads(json_matches[0])
        print(f'JSON大小: {len(str(data))} 字符')
        
        # 保存完整数据
        with open('page_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print('已保存到 page_data.json')
    except:
        print('JSON解析失败')
else:
    print('未找到JSON数据')
