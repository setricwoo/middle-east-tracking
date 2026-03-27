#!/usr/bin/env python3
"""
获取中期选举最近三周的小时数据
"""
import requests
import json
from datetime import datetime, timedelta

GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"

HEADERS = {"User-Agent": "Mozilla/5.0"}

# Token IDs
tokens = {
    "house_republican": "65139230827417363158752884968303867495725894165574887635816574090175320800482",
    "house_democratic": "83247781037352156539390391020957003253684756353330498622712686615394189337989",
    "senate_republican": "51939490109676186832431648150817642764713757269942680045369108749350437937569",
    "senate_democratic": "113287701564209339917476684182594869857163944899755684653484577837343960810736"
}

def get_history(token_id, interval="1h"):
    """获取价格历史"""
    url = f"{CLOB_API}/prices-history"
    params = {"market": token_id, "interval": interval}
    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=30)
        data = resp.json()
        return data.get('history', [])
    except Exception as e:
        print(f"Error: {e}")
        return []

results = {}

for name, token in tokens.items():
    print(f"\nFetching {name}...")
    
    history = get_history(token, '1h')
    print(f"  Got {len(history)} hourly points")
    
    if history:
        # 格式化为图表数据
        formatted = []
        for h in history:
            ts = h.get('t', 0)
            price = h.get('p', 0)
            dt = datetime.fromtimestamp(ts)
            formatted.append({
                'time': dt.strftime('%m-%d %H:%M'),
                'timestamp': ts,
                'probability': round(price * 100, 2)
            })
        
        results[name] = {
            'name': name,
            'current': formatted[-1]['probability'] if formatted else 0,
            'history': formatted
        }
        
        print(f"  Current: {results[name]['current']}%")
        print(f"  Time range: {formatted[0]['time']} -> {formatted[-1]['time']}")

# 保存
with open('midterm_3weeks_data.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\n\n=== Saved to midterm_3weeks_data.json ===")
