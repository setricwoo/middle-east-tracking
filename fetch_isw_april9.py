import requests
from bs4 import BeautifulSoup
import json

url = 'https://www.understandingwar.org/backgrounder/iran-update-special-report-april-9-2026'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

resp = requests.get(url, headers=headers, timeout=30)
resp.encoding = 'utf-8'

soup = BeautifulSoup(resp.text, 'html.parser')

# 提取标题
title = soup.find('h1', class_='page-header')
title_text = title.get_text(strip=True) if title else 'Iran Update Special Report'

# 提取关键要点 (Key Takeaways)
takeaways = []
content_div = soup.find('div', class_='field-name-body')
if content_div:
    # 查找 Key Takeaways 部分
    for elem in content_div.find_all(['h2', 'h3', 'strong']):
        text = elem.get_text(strip=True)
        if 'Key Takeaway' in text or '关键要点' in text:
            # 获取后面的列表
            next_elem = elem.find_parent()
            if next_elem:
                ul = next_elem.find_next('ul')
                if ul:
                    for li in ul.find_all('li'):
                        takeaways.append(li.get_text(strip=True))
            break

# 提取所有图片
images = []
for img in soup.find_all('img'):
    src = img.get('src', '')
    if src and ('understandingwar.org' in src or src.startswith('/')):
        if src.startswith('/'):
            src = 'https://www.understandingwar.org' + src
        images.append({
            'src': src,
            'alt': img.get('alt', '')
        })

# 提取正文内容
paragraphs = []
if content_div:
    for p in content_div.find_all('p'):
        text = p.get_text(strip=True)
        if text and len(text) > 20:
            paragraphs.append(text)

# 保存数据
data = {
    'title': title_text,
    'url': url,
    'date': '2026-04-09',
    'takeaways': takeaways,
    'images': images[:10],  # 限制图片数量
    'paragraphs': paragraphs[:50]  # 限制段落数量
}

with open('isw_april9_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'Title: {title_text}')
print(f'Takeaways found: {len(takeaways)}')
print(f'Images found: {len(images)}')
print(f'Paragraphs found: {len(paragraphs)}')
print('\n--- Key Takeaways ---')
for i, t in enumerate(takeaways[:5], 1):
    print(f'{i}. {t[:200]}...')
