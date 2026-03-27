#!/usr/bin/env python3
"""
获取中期选举分钟级历史数据
"""
import requests
import json
from datetime import datetime

GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}

# 事件信息
events = {
    "house": {
        "event_id": "32225",
        "slug": "which-party-will-win-the-house-in-2026",
        "markets": {
            "democratic": {"market_id": "562802"},
            "republican": {"market_id": "562803"}
        }
    },
    "senate": {
        "event_id": "32224", 
        "slug": "which-party-will-win-the-senate-in-2026",
        "markets": {
            "democratic": {"market_id": "562793"},
            "republican": {"market_id": "562794"}
        }
    }
}

def get_market_detail(market_id):
    """获取市场详情包括token ID"""
    url = f"{GAMMA_API}/markets/{market_id}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        return resp.json()
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_price_history(token_id, interval="1m"):
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

for name, info in events.items():
    print(f"\n=== {name.upper()} ===")
    print(f"Event ID: {info['event_id']}")
    
    market_data = {}
    
    for party, m_info in info['markets'].items():
        market_id = m_info['market_id']
        print(f"\n  {party}: market_id={market_id}")
        
        # 获取市场详情
        detail = get_market_detail(market_id)
        if detail:
            tokens = detail.get('clobTokenIds', [])
            print(f"    Tokens: {len(tokens)}")
            
            if tokens:
                # 尝试获取分钟级历史
                for interval in ["1m", "5m", "15m", "1h", "1d"]:
                    history = get_price_history(tokens[0], interval)
                    if history:
                        print(f"    History [{interval}]: {len(history)} points")
                        
                        # 格式化历史数据
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
                        
                        market_data[party] = {
                            'market_id': market_id,
                            'token_id': tokens[0],
                            'interval': interval,
                            'history': formatted,
                            'current_probability': formatted[-1]['probability'] if formatted else 0
                        }
                        break
    
    results[name] = market_data

# 保存
with open('midterm_minute_history.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\n\n=== Done ===")
for name, data in results.items():
    print(f"\n{name}:")
    for party, info in data.items():
        print(f"  {party}: {info.get('current_probability')}% ({len(info.get('history', []))} points)")
