#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import requests
import json
from datetime import datetime

GAMMA_API = "https://gamma-api.polymarket.com"

# 从Polymarket网页找到的市场slug
MARKET_SLUGS = [
    "will-iran-close-the-strait-of-hormuz-by-2027",
    "iran-strikes-israel-on",
    "us-x-iran-ceasefire-by-march-31",
    "us-x-iran-ceasefire-by-april-30", 
    "us-x-iran-ceasefire-by-may-31",
    "us-x-iran-ceasefire-by-june-30",
    "will-crude-oil-cl-hit-by-end-of-march",
    "will-crude-oil-cl-hit-by-end-of-june",
    "us-forces-enter-iran-by-march-31",
    "will-the-iranian-regime-fall-by-march-31",
    "will-the-iranian-regime-fall-by-june-30",
]

def get_event(slug):
    url = f"{GAMMA_API}/events/{slug}"
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except:
        return None

def get_market(slug):
    url = f"{GAMMA_API}/markets/{slug}"
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except:
        return None

def get_prices(market_id):
    url = f"{GAMMA_API}/markets/{market_id}/prices"
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except:
        return []

print("=" * 60)
print("获取伊朗市场数据")
print("=" * 60)

results = {}

for slug in MARKET_SLUGS:
    print(f"\n尝试: {slug}")
    
    # 先尝试作为事件获取
    data = get_event(slug)
    if data:
        print(f"  [OK] 事件: {data.get('title', 'N/A')[:50]}")
        results[slug] = data
        
        # 获取每个市场的价格历史
        for m in data.get("markets", []):
            m_id = m.get("id")
            prices = get_prices(m_id)
            m["priceHistory"] = prices
            print(f"    - {m.get('question', 'N/A')[:40]}... ({len(prices)} price points)")
    else:
        # 尝试作为单个市场获取
        data = get_market(slug)
        if data:
            print(f"  [OK] 市场: {data.get('question', 'N/A')[:50]}")
            prices = get_prices(data.get("id"))
            data["priceHistory"] = prices
            results[slug] = data
            print(f"    ({len(prices)} price points)")
        else:
            print(f"  [NOT FOUND]")

# 保存
output = {
    "updatedAt": datetime.now().isoformat(),
    "count": len(results),
    "data": results
}

with open("iran_market_data.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print("\n" + "=" * 60)
print(f"完成! 找到 {len(results)} 个市场/事件")
print("保存到: iran_market_data.json")
print("=" * 60)
