#!/usr/bin/env python3
import requests
import json
from datetime import datetime

CLOB_API = 'https://clob.polymarket.com'
HEADERS = {'User-Agent': 'Mozilla/5.0'}

# Token IDs from market detail
yes_token = "65139230827417363158752884968303867495725894165574887635816574090175320800482"  # Yes
no_token = "17371217118862125782438074585166210555214661810823929795910191856905580975576"   # No

print("Testing CLOB API with correct token IDs...\n")

url = f'{CLOB_API}/prices-history'

for interval in ['1m', '5m', '15m', '1h', '1d', 'max']:
    params = {'market': yes_token, 'interval': interval}
    resp = requests.get(url, params=params, headers=HEADERS, timeout=30)
    data = resp.json()
    history = data.get('history', [])
    print(f'[{interval}] Status: {resp.status_code}, Points: {len(history)}')
    
    if history:
        print(f'  First: {history[0]}')
        print(f'  Last: {history[-1]}')
        
        # 格式化数据
        formatted = []
        for h in history[-50:]:  # 最近50个点
            ts = h.get('t', 0)
            price = h.get('p', 0)
            dt = datetime.fromtimestamp(ts)
            formatted.append({
                'time': dt.strftime('%m-%d %H:%M'),
                'probability': round(price * 100, 1)
            })
        
        print(f'\n  Recent 5 points:')
        for p in formatted[-5:]:
            print(f'    {p}')
        break
