import requests
from bs4 import BeautifulSoup
import json

url = 'https://www.understandingwar.org/backgrounder/iran-update-special-report-april-9-2026'
resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
soup = BeautifulSoup(resp.text, 'html.parser')

result = {
    'title': 'Iran Update Special Report, April 9, 2026',
    'url': url,
    'date': '2026-04-09',
    'sections': {}
}

# 提取各部分
sections = ['Key Takeaways', 'Toplines', 'US and Israeli Air Campaign', 
            'Iranian Response', 'Israeli Campaign Against Hezbollah and Hezbollah Response',
            'Other Axis of Resistance Response']

for section_name in sections:
    section_data = []
    for h2 in soup.find_all('h2'):
        if h2.get_text(strip=True) == section_name:
            for sibling in h2.find_next_siblings():
                if sibling.name == 'h2':
                    break
                if sibling.name in ['p', 'ul', 'ol', 'div']:
                    text = sibling.get_text(strip=True)
                    if text and len(text) > 10:
                        section_data.append(text)
            break
    result['sections'][section_name] = section_data

# 提取地图/图表图片
map_images = []
for img in soup.find_all('img'):
    src = img.get('src', '')
    alt = img.get('alt', '')
    if src and ('map' in alt.lower() or 'campaign' in alt.lower() or 'strike' in alt.lower() or 
                'hormuz' in alt.lower() or 'iran' in alt.lower() or '2026' in alt.lower()):
        if src.startswith('/'):
            src = 'https://www.understandingwar.org' + src
        if 'understandingwar.org' in src and not src.endswith('.svg'):
            map_images.append({'src': src, 'alt': alt})

result['map_images'] = map_images[:10]

# 保存
with open('isw_april9_final.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

# 打印
print(f'Title: {result["title"]}')
print(f'URL: {result["url"]}')
for name, content in result['sections'].items():
    print(f'\n=== {name} ({len(content)} items) ===')
    for i, item in enumerate(content[:2], 1):
        print(f'{i}. {item[:150]}...')

print(f'\n=== Map Images ({len(map_images)}) ===')
for img in map_images[:5]:
    print(f'- {img["alt"][:50]}... : {img["src"][:60]}...')
