#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接从Gamma API获取伊朗相关Polymarket数据
"""

import requests
import json
from datetime import datetime

GAMMA_API = "https://gamma-api.polymarket.com"

def try_endpoint(endpoint, params=None):
    """尝试访问API端点"""
    url = f"{GAMMA_API}{endpoint}"
    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

# 1. 搜索活跃市场
print("=" * 60)
print("1. 搜索 'iran' 关键词")
print("=" * 60)

# 尝试不同的搜索参数
searches = [
    {"search": "iran", "active": "true", "limit": 20},
    {"search": "iran ceasefire", "active": "true", "limit": 20},
    {"search": "hormuz", "active": "true", "limit": 20},
    {"search": "trump iran", "active": "true", "limit": 20},
    {"search": "crude oil", "active": "true", "limit": 20},
]

all_markets = []

for params in searches:
    print(f"\n搜索: {params['search']}")
    result = try_endpoint("/markets", params)
    
    if isinstance(result, list):
        print(f"  找到 {len(result)} 个市场")
        for m in result[:5]:  # 只显示前5个
            print(f"    - {m.get('question', 'N/A')[:60]}...")
            print(f"      ID: {m.get('id')}, Prob: {m.get('outcomePrices')}")
            all_markets.append(m)
    else:
        print(f"  错误: {result.get('error', 'Unknown')}")

# 2. 搜索事件
print("\n" + "=" * 60)
print("2. 搜索事件 (events)")
print("=" * 60)

event_searches = [
    {"search": "iran", "limit": 20},
    {"search": "middle east", "limit": 20},
]

for params in event_searches:
    print(f"\n搜索: {params['search']}")
    result = try_endpoint("/events", params)
    
    if isinstance(result, list):
        print(f"  找到 {len(result)} 个事件")
        for e in result[:3]:
            print(f"    - {e.get('title', 'N/A')[:60]}...")
            print(f"      ID: {e.get('id')}, Markets: {e.get('totalMarkets')}")
    else:
        print(f"  错误: {result.get('error', 'Unknown')}")

# 3. 尝试获取特定市场（如果知道ID）
print("\n" + "=" * 60)
print("3. 尝试获取已知的伊朗相关市场")
print("=" * 60)

# 一些可能的市场ID（需要验证）
known_slugs = [
    "us-x-iran-ceasefire-by-march-31",
    "us-x-iran-ceasefire-by-april-30",
    "will-iran-close-the-strait-of-hormuz-by-2027",
    "will-crude-oil-cl-hit-by-end-of-march",
]

for slug in known_slugs:
    print(f"\n尝试: {slug}")
    result = try_endpoint(f"/markets/{slug}")
    if "error" not in result:
        print(f"  成功!")
        print(f"    问题: {result.get('question', 'N/A')}")
        print(f"    价格: {result.get('outcomePrices')}")
    else:
        print(f"  未找到或错误")

# 4. 保存所有找到的市场
print("\n" + "=" * 60)
print("4. 保存结果")
print("=" * 60)

if all_markets:
    with open("found_markets.json", "w", encoding="utf-8") as f:
        json.dump(all_markets, f, ensure_ascii=False, indent=2)
    print(f"已保存 {len(all_markets)} 个市场到 found_markets.json")
else:
    print("未找到任何市场")

print("\n" + "=" * 60)
print("完成")
print("=" * 60)
