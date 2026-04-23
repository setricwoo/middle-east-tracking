import requests
from bs4 import BeautifulSoup
import re
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Cache-Control': 'max-age=0',
}

def fetch_url(url):
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        print(f"URL: {url}")
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            return resp.text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
    return None

def extract_info(html, url):
    soup = BeautifulSoup(html, 'html.parser')
    
    # Title
    title_tag = soup.find('h1', class_=re.compile('page-title|title|headline')) or soup.find('h1')
    title = title_tag.get_text(strip=True) if title_tag else 'N/A'
    
    # Date
    date_tag = soup.find('div', class_=re.compile('date|published|field--name-field-date')) or soup.find('time')
    date = date_tag.get_text(strip=True) if date_tag else 'N/A'
    if date == 'N/A':
        # Try meta tags
        meta_date = soup.find('meta', property='article:published_time') or soup.find('meta', attrs={'name': 'date'})
        if meta_date:
            date = meta_date.get('content', 'N/A')
    
    # Key Takeaways
    key_takeaways = []
    # Look for Key Takeaways section
    for heading in soup.find_all(['h2', 'h3', 'strong', 'b']):
        text = heading.get_text(strip=True).lower()
        if 'key takeaway' in text or 'key findings' in text:
            # Get the next ul or list of paragraphs
            next_sibling = heading.find_next_sibling()
            while next_sibling and next_sibling.name not in ['ul', 'ol', 'div']:
                if next_sibling.name == 'p':
                    key_takeaways.append(next_sibling.get_text(strip=True))
                next_sibling = next_sibling.find_next_sibling()
            if next_sibling and next_sibling.name in ['ul', 'ol']:
                for li in next_sibling.find_all('li'):
                    key_takeaways.append(li.get_text(strip=True))
            break
    
    # Images
    images = []
    for img in soup.find_all('img'):
        src = img.get('src')
        if src:
            if src.startswith('//'):
                src = 'https:' + src
            elif src.startswith('/'):
                src = 'https://understandingwar.org' + src
            images.append(src)
    
    # Body text summary
    body = soup.find('div', class_=re.compile('content|body|main-content|field--name-body')) or soup.find('article') or soup.find('main')
    body_text = ""
    if body:
        paragraphs = body.find_all('p')
        body_text = '\n\n'.join([p.get_text(strip=True) for p in paragraphs[:20]])
    
    return {
        'url': url,
        'title': title,
        'date': date,
        'key_takeaways': key_takeaways,
        'images': images,
        'body_summary': body_text[:3000] if body_text else ""
    }

# Try direct URL first
url = 'https://understandingwar.org/research/middle-east/iran-update-special-report-april-22-2026/'
html = fetch_url(url)

if not html:
    # Try without trailing slash
    url = 'https://understandingwar.org/research/middle-east/iran-update-special-report-april-22-2026'
    html = fetch_url(url)

if html:
    info = extract_info(html, url)
    print("\n" + "="*60)
    print("TITLE:", info['title'])
    print("DATE:", info['date'])
    print("URL:", info['url'])
    print("\nKEY TAKEAWAYS:")
    for i, kt in enumerate(info['key_takeaways'], 1):
        print(f"{i}. {kt}")
    print("\nIMAGES:")
    for img in info['images']:
        print(img)
    print("\nBODY SUMMARY:")
    print(info['body_summary'])
    print("="*60)
else:
    print("Failed to fetch the page. Trying homepage search...")
    home_html = fetch_url('https://understandingwar.org/')
    if home_html:
        soup = BeautifulSoup(home_html, 'html.parser')
        # Look for links to Iran Update Special Report
        links = []
        for a in soup.find_all('a', href=True):
            text = a.get_text(strip=True).lower()
            href = a['href']
            if 'iran update' in text and 'special report' in text and 'april 22' in text:
                if href.startswith('/'):
                    href = 'https://understandingwar.org' + href
                links.append((text, href))
        print(f"Found {len(links)} matching links on homepage")
        for text, href in links[:5]:
            print(f"  {text}: {href}")
