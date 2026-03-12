#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取伊朗相关市场真实数据
"""

import requests
import json
from datetime import datetime

GAMMA_API = "https://gamma-api.polymarket.com"

# 从网页找到的市场slug
IRAN_MARKETS = {
    "hormuz_2027": "will-iran-close-the-strait-of-hormuz-by-2027",
    "iran_strikes": "iran-strikes-israel-on",
}

# 从iran_events.json中已知的其他市场
OTHER_MARKETS = [
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

def get_market(slug):
    """获取市场数据"""
    url = f"{GAMMA_API}/markets/{slug}"
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return None

def get_event(slug):
    """获取事件数据（包含多个市场）"""
    url = f"{GAMMA_API}/events/{slug}"
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return None

def get_price_history(market_id):
    """获取价格历史"""
    url = f"{GAMMA_API}/markets/{market_id}/prices"
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return []

print("=" * 60)
print("获取伊朗相关市场数据")
print("=" * 60)

all_data = {
    "updatedAt": datetime.now().isoformat(),
    "markets": {}
}

# 1. 获取主要事件
for name, slug in IRAN_MARKETS.items():
    print(f"\n获取事件: {name} ({slug})")
    event = get_event(slug)
    
    if event and not event.get("error"):
        print(f"  ✓ 成功: {event.get('title', 'N/A')}")
        print(f"    市场数量: {event.get('totalMarkets', 0)}")
        
        all_data["markets"][name] = {
            "title": event.get("title"),
            "slug": slug,
            "markets": []
        }
        
        # 获取每个子市场的数据
        for market in event.get("markets", []):
            market_id = market.get("id")
            question = market.get("question", "N/A")
            
            print(f"    - {question[:50]}...")
            
            # 获取价格历史
            prices = get_price_history(market_id)
            
            market_data = {
                "id": market_id,
                "question": question,
                "slug": market.get("slug"),
                "outcomes": market.get("outcomes", []),
                "outcomePrices": market.get("outcomePrices", []),
                "volume": market.get("volumeNum", 0),
                "endDate": market.get("endDate"),
                "priceHistory": prices
            }
            
            all_data["markets"][name]["markets"].append(market_data)
    else:
        print(f"  ✗ 未找到")

# 2. 尝试获取其他已知市场
print("\n" + "=" * 60)
print("尝试获取其他市场")
print("=" * 60)

for slug in OTHER_MARKETS:
    print(f"\n尝试: {slug}")
    market = get_market(slug)
    
    if market and not market.get("error"):
        print(f"  ✓ 成功: {market.get('question', 'N/A')[:50]}...")
        
        # 获取价格历史
        prices = get_price_history(market.get("id"))
        
        key = slug.replace("-", "_")
        all_data["markets"][key] = {
            "question": market.get("question"),
            "slug": slug,
            "outcomes": market.get("outcomes", []),
            "outcomePrices": market.get("outcomePrices", []),
            "volume": market.get("volumeNum", 0),
            "endDate": market.get("endDate"),
            "priceHistory": prices
        }
    else:
        print(f"  ✗ 未找到")

# 保存数据
print("\n" + "=" * 60)
print("保存数据")
print("=" * 60)

with open("iran_real_data.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

print(f"已保存到: iran_real_data.json")
print(f"总市场数: {len(all_data['markets'])}")

# 打印摘要
print("\n数据摘要:")
for name, data in all_data["markets"].items():
    if "markets" in data:
        print(f"  - {name}: {len(data['markets'])} 个子市场")
    else:
        print(f"  - {name}: {data.get('question', 'N/A')[:40]}...")
