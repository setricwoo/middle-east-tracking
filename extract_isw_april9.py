import requests
from bs4 import BeautifulSoup
import json

url = 'https://www.understandingwar.org/backgrounder/iran-update-special-report-april-9-2026'
resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
soup = BeautifulSoup(resp.text, 'html.parser')

# 提取所有h2标题和后续内容
result = {}
current_section = None
current_content = []

for elem in soup.find_all(['h2', 'p', 'ul', 'figure', 'img']):
    if elem.name == 'h2':
        if current_section and current_content:
            result[current_section] = current_content
        current_section = elem.get_text(strip=True)
        current_content = []
    elif current_section:
        if elem.name == 'p':
            text = elem.get_text(strip=True)
            if text:
                current_content.append({'type': 'p', 'text': text})
        elif elem.name == 'ul':
            items = [li.get_text(strip=True) for li in elem.find_all('li')]
            current_content.append({'type': 'ul', 'items': items})
        elif elem.name == 'figure':
            img = elem.find('img')
            if img:
                src = img.get('src', '')
                if src.startswith('/'):
                    src = 'https://www.understandingwar.org' + src
                caption = elem.find('figcaption')
                caption_text = caption.get_text(strip=True) if caption else ''
                current_content.append({'type': 'img', 'src': src, 'caption': caption_text})
        elif elem.name == 'img':
            src = elem.get('src', '')
            if src.startswith('/'):
                src = 'https://www.understandingwar.org' + src
            alt = elem.get('alt', '')
            current_content.append({'type': 'img', 'src': src, 'caption': alt})

if current_section and current_content:
    result[current_section] = current_content

# 保存
with open('isw_april9_extracted.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

# 打印关键要点
print('Sections found:', list(result.keys()))
if 'Key Takeaways' in result:
    print('\n=== Key Takeaways ===')
    for item in result['Key Takeaways']:
        if item['type'] == 'p':
            text = item['text'][:150]
            print(f'P: {text}...')
        elif item['type'] == 'ul':
            for li in item['items']:
                li_text = li[:150]
                print(f'  - {li_text}...')
