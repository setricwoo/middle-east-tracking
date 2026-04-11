import requests
from bs4 import BeautifulSoup
import json

url = 'https://www.understandingwar.org/backgrounder/iran-update-special-report-april-10-2026'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
resp = requests.get(url, headers=headers, timeout=30)
soup = BeautifulSoup(resp.text, 'html.parser')

# 提取标题
title = soup.find('h1', class_='page-header')
title_text = title.get_text(strip=True) if title else 'Iran Update Special Report'

# 提取所有内容
content_div = soup.find('div', class_='field-name-body') or soup.find('div', {'property': 'content:encoded'})

all_content = []
if content_div:
    for elem in content_div.find_all(['h2', 'h3', 'p', 'ul', 'ol', 'figure']):
        tag_name = elem.name
        if tag_name in ['h2', 'h3']:
            text = elem.get_text(strip=True)
            all_content.append({'type': 'heading', 'level': tag_name, 'text': text})
        elif tag_name == 'p':
            text = elem.get_text(strip=True)
            if text and len(text) > 20:
                all_content.append({'type': 'paragraph', 'text': text})
        elif tag_name in ['ul', 'ol']:
            items = [li.get_text(strip=True) for li in elem.find_all('li') if li.get_text(strip=True)]
            if items:
                all_content.append({'type': 'list', 'items': items})
        elif tag_name == 'figure':
            img = elem.find('img')
            if img:
                src = img.get('src', '')
                if src.startswith('/'):
                    src = 'https://www.understandingwar.org' + src
                caption = elem.find('figcaption')
                caption_text = caption.get_text(strip=True) if caption else ''
                all_content.append({'type': 'image', 'src': src, 'caption': caption_text})

# 提取所有图片
images = []
for img in soup.find_all('img'):
    src = img.get('src', '')
    alt = img.get('alt', '')
    if src and ('2026' in src or 'April' in src or 'Iran' in src or 'Hormuz' in src or 'Lebanon' in src or 'Gulf' in src):
        if src.startswith('/'):
            src = 'https://www.understandingwar.org' + src
        if 'understandingwar.org' in src and not src.endswith('.svg'):
            images.append({'src': src, 'alt': alt})

result = {
    'title': title_text,
    'url': url,
    'date': '2026-04-10',
    'content': all_content,
    'images': images[:15]
}

with open('isw_april10_full.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print('Title:', title_text)
print('Content items:', len(all_content))
print('Images:', len(images))
print('\n=== Content Preview ===')
for item in all_content[:10]:
    if item['type'] == 'heading':
        print(item['level'].upper() + ': ' + item['text'])
    elif item['type'] == 'paragraph':
        print('P: ' + item['text'][:100] + '...')
    elif item['type'] == 'list':
        print('LIST: ' + str(len(item['items'])) + ' items')
