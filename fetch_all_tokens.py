#!/usr/bin/env python3
"""
获取所有中期选举市场的Token IDs
"""
import requests
import json

GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def get_event_by_slug(slug):
    url = f"{GAMMA_API}/events"
    params = {"slug": slug}
    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=30)
        data = resp.json()
        if data and len(data) > 0:
            return data[0]
    except:
        pass
    return None

def get_market_detail(market_id):
    url = f"{GAMMA_API}/markets/{market_id}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        return resp.json()
    except:
        return None

slugs = [
    "which-party-will-win-the-house-in-2026",
    "which-party-will-win-the-senate-in-2026"
]

all_tokens = {}

for slug in slugs:
    print(f"\n=== {slug} ===")
    event = get_event_by_slug(slug)
    if event:
        print(f"Event: {event.get('title')}")
        for m in event.get('markets', []):
            q = m.get('question', '')
            if 'Republican' in q or 'Democratic' in q:
                print(f"\n  {q}")
                detail = get_market_detail(m['id'])
                if detail:
                    tokens_str = detail.get('clobTokenIds', '[]')
                    tokens = json.loads(tokens_str)
                    print(f"    Tokens: {tokens}")
                    key = f"{slug.split('-')[-3]}_{'republican' if 'Republican' in q else 'democratic'}"
                    all_tokens[key] = tokens[0] if tokens else None

print("\n\n=== All Tokens ===")
for k, v in all_tokens.items():
    print(f"{k}: {v}")
