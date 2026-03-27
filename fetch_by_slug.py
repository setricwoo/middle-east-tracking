#!/usr/bin/env python3
"""
通过slug直接获取Gamma API数据
"""
import requests
import json
import time

GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Origin": "https://polymarket.com",
}

slugs = [
    "which-party-will-win-the-house-in-2026",
    "which-party-will-win-the-senate-in-2026"
]

results = {}

for slug in slugs:
    print(f"\n=== Fetching: {slug} ===")
    
    # 方法1: 通过/events端点带slug参数
    try:
        url = f"{GAMMA_API}/events"
        params = {"slug": slug}
        print(f"  GET {url}?slug={slug}")
        resp = requests.get(url, params=params, headers=HEADERS, timeout=30)
        print(f"  Status: {resp.status_code}")
        
        if resp.status_code == 200:
            data = resp.json()
            if data and len(data) > 0:
                event = data[0]
                print(f"  Found: {event.get('title')}")
                print(f"  ID: {event.get('id')}")
                
                # 保存完整事件数据
                results[slug] = event
                
                # 获取市场详情
                markets = event.get('markets', [])
                for m in markets:
                    if 'Republican' in m.get('question', '') or 'Democratic' in m.get('question', ''):
                        print(f"\n    Market: {m.get('question')}")
                        print(f"    ID: {m.get('id')}")
                        tokens = m.get('clobTokenIds', [])
                        print(f"    Tokens: {len(tokens)}")
                        
                        # 获取分钟级历史数据
                        if tokens:
                            for interval in ["1m", "5m", "15m", "1h"]:
                                try:
                                    hist_url = f"{CLOB_API}/prices-history"
                                    params = {"market": tokens[0], "interval": interval}
                                    hist_resp = requests.get(hist_url, params=params, headers=HEADERS, timeout=30)
                                    hist_data = hist_resp.json()
                                    history = hist_data.get('history', [])
                                    if history:
                                        print(f"    History [{interval}]: {len(history)} points")
                                        print(f"      First: {history[0]}")
                                        print(f"      Last: {history[-1]}")
                                        break
                                except Exception as e:
                                    continue
            else:
                print("  No data returned")
        else:
            print(f"  Error: {resp.text[:200]}")
            
    except Exception as e:
        print(f"  Error: {e}")
    
    time.sleep(1)  # 避免请求过快

# 保存结果
if results:
    with open('midterm_full_data.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n\n=== Saved {len(results)} events ===")
else:
    print("\n\n=== No events found ===")
