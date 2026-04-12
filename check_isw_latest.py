import requests
from bs4 import BeautifulSoup
import json

def check_report(date_str):
    url = f'https://www.understandingwar.org/backgrounder/iran-update-special-report-april-{date_str}-2026'
    try:
        resp = requests.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}, timeout=30)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            title = soup.find('h1', class_='page-header')
            if title:
                return {'found': True, 'title': title.get_text(strip=True), 'url': url}
    except Exception as e:
        return {'found': False, 'error': str(e)}
    return {'found': False}

# 检查4月10、11、12日
for day in ['10', '11', '12']:
    result = check_report(day)
    print(f'April {day}: {result}')
