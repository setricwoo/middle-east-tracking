#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取当前活跃的Polymarket市场
"""

import requests
import json

GAMMA_API = "https://gamma-api.polymarket.com"

def get_active_markets(limit=100):
    """获取当前活跃市场"""
    url = f"{GAMMA_API}/markets"
    params = {
        "active": "true",
        "closed": "false",
        "limit": limit,
        "order": "volume",
        "sort": "desc"
    }
    
    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"Error: {e}")
        return []

print("=" * 60)
print("获取当前活跃市场 (按交易量排序)")
print("=" * 60)

markets = get_active_markets(50)

print(f"\n找到 {len(markets)} 个活跃市场\n")

# 过滤可能相关的市场
keywords = ['war', 'military', 'trump', 'oil', 'crude', 'iran', 'israel', 'gaza', 'ukraine', 'ceasefire', 'peace']

relevant = []
for m in markets:
    question = m.get('question', '').lower()
    if any(k in question for k in keywords):
        relevant.append(m)

print(f"可能相关的市场 ({len(relevant)}个):")
print("-" * 60)

for m in relevant:
    print(f"\n问题: {m.get('question', 'N/A')}")
    print(f"Slug: {m.get('slug', 'N/A')}")
    print(f"ID: {m.get('id', 'N/A')}")
    print(f"价格: {m.get('outcomePrices', 'N/A')}")
    print(f"交易量: {m.get('volume', 'N/A')}")
    print("-" * 60)

# 保存所有市场
with open("active_markets.json", "w", encoding="utf-8") as f:
    json.dump(markets, f, ensure_ascii=False, indent=2)

print(f"\n已保存所有市场到 active_markets.json")
