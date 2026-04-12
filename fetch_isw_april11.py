import requests
from bs4 import BeautifulSoup
import json

url = 'https://www.understandingwar.org/backgrounder/iran-update-special-report-april-11-2026'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
resp = requests.get(url, headers=headers, timeout=30)
soup = BeautifulSoup(resp.text, 'html.parser')

result = {
    'title': 'Iran Update Special Report, April 11, 2026',
    'url': url,
    'date': '2026-04-11',
    'sections': {}
}

# 提取Key Takeaways
for h2 in soup.find_all('h2'):
    text = h2.get_text(strip=True)
    if 'Key Takeaway' in text:
        content = []
        for sibling in h2.find_next_siblings():
            if sibling.name == 'h2':
                break
            if sibling.name in ['p', 'ul', 'ol']:
                t = sibling.get_text(strip=True)
                if t and len(t) > 20:
                    content.append(t)
        result['sections']['Key Takeaways'] = content
        break

# 提取图片
images = []
for img in soup.find_all('img'):
    src = img.get('src', '')
    alt = img.get('alt', '')
    if src and ('2026' in src or 'April' in src or 'Iran' in src or 'Hormuz' in src or 'Lebanon' in src):
        if src.startswith('/'):
            src = 'https://www.understandingwar.org' + src
        if 'understandingwar.org' in src and not src.endswith('.svg'):
            images.append({'src': src, 'alt': alt})

result['images'] = images[:10]

with open('isw_april11_data.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print('Title:', result['title'])
print('Key Takeaways:', len(result['sections'].get('Key Takeaways', [])))
for i, item in enumerate(result['sections'].get('Key Takeaways', [])[:3], 1):
    print(f'{i}. {item[:100]}...')
print('Images:', len(images))
