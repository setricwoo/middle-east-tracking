#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
尝试从Polymarket伊朗页面获取数据
"""

import requests
import json

GAMMA_API = "https://gamma-api.polymarket.com"

def get_event_by_slug(slug):
    """通过slug获取事件"""
    url = f"{GAMMA_API}/events/{slug}"
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

def search_events(search_term, limit=50):
    """搜索事件"""
    url = f"{GAMMA_API}/events"
    params = {
        "search": search_term,
        "limit": limit,
        "active": "true",
        "order": "volume",
        "sort": "desc"
    }
    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

print("=" * 60)
print("尝试获取Polymarket伊朗页面数据")
print("=" * 60)

# 1. 尝试获取事件 /events/iran
print("\n1. 尝试 GET /events/iran")
result = get_event_by_slug("iran")
print(json.dumps(result, indent=2)[:2000] if not result.get("error") else f"Error: {result['error']}")

# 2. 搜索包含iran的事件
print("\n2. 搜索 'iran' 事件")
results = search_events("iran", 20)
if isinstance(results, list):
    print(f"找到 {len(results)} 个事件")
    for e in results[:5]:
        print(f"\n  - {e.get('title', 'N/A')}")
        print(f"    Slug: {e.get('slug', 'N/A')}")
        print(f"    ID: {e.get('id', 'N/A')}")
        print(f"    Markets: {e.get('totalMarkets', 0)}")
else:
    print(f"Error: {results.get('error', 'Unknown')}")

# 3. 尝试其他可能的事件slug
print("\n3. 尝试其他可能的事件slug")
slugs_to_try = [
    "iran-conflict",
    "iran-israel-conflict",
    "us-iran-conflict",
    "middle-east-conflict",
    "gaza-israel-conflict",
]

for slug in slugs_to_try:
    result = get_event_by_slug(slug)
    if not result.get("error"):
        print(f"\n  ✓ {slug}: {result.get('title', 'N/A')}")
        print(f"    Markets: {result.get('totalMarkets', 0)}")
        # 保存找到的数据
        with open(f"event_{slug}.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"    已保存到 event_{slug}.json")
    else:
        print(f"  ✗ {slug}: Not found")
