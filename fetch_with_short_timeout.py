#!/usr/bin/env python3
import requests
import json
from datetime import datetime

GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}

# 直接尝试通过slug参数获取
def get_event_by_slug(slug):
    try:
        url = f"{GAMMA_API}/events"
        params = {"slug": slug}
        resp = requests.get(url, params=params, headers=HEADERS, timeout=5)
        data = resp.json()
        if data and len(data) > 0:
            return data[0]
    except Exception as e:
        print(f"Error: {e}")
    return None

# 获取CLOB历史
def get_history(token_id):
    try:
        url = f"{CLOB_API}/prices-history"
        for interval in ["1m", "5m", "15m", "1h", "1d"]:
            params = {"market": token_id, "interval": interval}
            resp = requests.get(url, params=params, headers=HEADERS, timeout=8)
            data = resp.json()
            history = data.get('history', [])
            if history:
                return interval, history
    except:
        pass
    return None, []

# 尝试两个事件
slugs = [
    "which-party-will-win-the-house-in-2026",
    "which-party-will-win-the-senate-in-2026"
]

results = {}

for slug in slugs:
    print(f"\n=== {slug} ===")
    event = get_event_by_slug(slug)
    
    if event:
        print(f"Found: {event.get('title')}")
        print(f"ID: {event.get('id')}")
        
        markets_data = []
        for m in event.get('markets', []):
            market_info = {
                'question': m.get('question'),
                'outcomes': m.get('outcomes', []),
                'outcomePrices': m.get('outcomePrices', []),
            }
            
            # 获取历史数据
            tokens = m.get('clobTokenIds', [])
            if tokens:
                interval, history = get_history(tokens[0])
                market_info['interval'] = interval
                market_info['history_count'] = len(history)
                if history:
                    market_info['history_sample'] = history[:3]
                    market_info['history_last'] = history[-1:]
                    print(f"  History: {len(history)} points (interval: {interval})")
            
            markets_data.append(market_info)
        
        results[slug] = {
            'title': event.get('title'),
            'id': event.get('id'),
            'markets': markets_data
        }
    else:
        print("Not found")

# 保存
if results:
    with open('midterm_minute_data.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n\nSaved {len(results)} events")
else:
    print("\n\nNo events found via Gamma API")
