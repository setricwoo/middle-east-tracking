#!/usr/bin/env python3
"""
直接尝试获取中期选举事件数据
"""
import requests
import json

GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Origin": "https://polymarket.com",
    "Referer": "https://polymarket.com/",
}

def try_get_event(event_id):
    """尝试通过ID获取事件"""
    url = f"{GAMMA_API}/events/{event_id}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except:
        pass
    return None

def try_get_by_slug(slug):
    """尝试通过slug搜索"""
    url = f"{GAMMA_API}/events"
    params = {"slug": slug, "limit": 5}
    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=10)
        data = resp.json()
        for event in data:
            if slug in event.get('slug', ''):
                return event
    except:
        pass
    return None

def get_clob_history(token_id, interval="1m"):
    """获取CLOB分钟级历史数据"""
    url = f"{CLOB_API}/prices-history"
    params = {"market": token_id, "interval": interval}
    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

# 尝试的事件ID（常见格式）
slugs_to_try = [
    "which-party-will-win-the-senate-in-2026",
    "which-party-will-win-the-house-in-2026",
    "which-party-will-win-senate-2026",
    "which-party-will-win-house-2026",
]

results = {}

print("=== 尝试获取事件数据 ===\n")

for slug in slugs_to_try:
    print(f"尝试: {slug}")
    
    # 方法1: 通过slug搜索
    event = try_get_by_slug(slug)
    if event:
        print(f"  成功找到!")
        print(f"  Title: {event.get('title')}")
        print(f"  ID: {event.get('id')}")
        
        # 获取市场数据
        markets = event.get('markets', [])
        for m in markets:
            print(f"\n  Market: {m.get('question')}")
            outcomes = m.get('outcomes', [])
            prices = m.get('outcomePrices', [])
            print(f"    Outcomes: {outcomes}")
            print(f"    Prices: {prices}")
            
            # 获取CLOB历史数据
            clob_tokens = m.get('clobTokenIds', [])
            if clob_tokens:
                print(f"    CLOB Tokens: {clob_tokens}")
                for i, token in enumerate(clob_tokens):
                    print(f"\n    获取 Token {i+1} 历史数据...")
                    for interval in ["1m", "5m", "1h", "1d"]:
                        history = get_clob_history(token, interval)
                        hist_data = history.get('history', [])
                        if hist_data:
                            print(f"      [{interval}] {len(hist_data)} points")
                            if hist_data:
                                print(f"        Sample: {hist_data[0]} -> {hist_data[-1]}")
                            break
        
        results[slug] = event
    else:
        print(f"  未找到\n")

# 保存结果
if results:
    with open('midterm_direct_fetch.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n已保存 {len(results)} 个事件到 midterm_direct_fetch.json")
else:
    print("\n未找到任何事件")
