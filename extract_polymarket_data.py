#!/usr/bin/env python3
"""从next_data.json提取Polymarket市场数据"""
import json
from datetime import datetime, timedelta

# 加载数据
with open('next_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

state = data['props']['pageProps']['dehydratedState']

# 找到事件数据
events = []
for q in state['queries']:
    query_key = q.get("queryKey", [])
    if isinstance(query_key, list) and query_key[0] == 'events':
        event_data = q['state']['data']
        if 'pages' in event_data:
            for page in event_data['pages']:
                if isinstance(page, dict) and 'events' in page:
                    events.extend(page['events'])

print(f"Total events: {len(events)}")

# 提取我们需要的市场数据
markets_data = {}

for event in events:
    slug = event.get('slug', '')
    title = event.get('title', '')
    event_id = event.get('id', '')
    
    if not event.get('markets'):
        continue
    
    for market in event['markets']:
        market_id = market.get('id', '')
        question = market.get('question', '')
        outcome_prices = market.get('outcomePrices', [])
        volume = float(market.get('volume', 0) or 0)
        
        # 计算概率 (Yes概率是第一个价格)
        if outcome_prices and len(outcome_prices) >= 2:
            try:
                yes_prob = float(outcome_prices[0]) * 100
            except:
                yes_prob = 0
        else:
            yes_prob = 0
        
        # 格式化volume
        if volume >= 1_000_000:
            volume_str = f"${volume/1_000_000:.1f}M"
        elif volume >= 1_000:
            volume_str = f"${volume/1_000:.1f}K"
        else:
            volume_str = f"${volume:.0f}"
        
        markets_data[slug] = {
            'event_id': event_id,
            'market_id': market_id,
            'title': title,
            'question': question,
            'current_probability': round(yes_prob, 2),
            'volume': volume_str,
            'raw_volume': volume
        }

# 打印找到的市场
print("\n=== Found Markets ===")
for slug, info in markets_data.items():
    print(f"\n{slug}:")
    print(f"  Title: {info['title'][:60]}...")
    print(f"  Probability: {info['current_probability']}%")
    print(f"  Volume: {info['volume']}")

# 保存完整数据
with open('polymarket_real_data.json', 'w', encoding='utf-8') as f:
    json.dump(markets_data, f, ensure_ascii=False, indent=2)

print(f"\n\nSaved to polymarket_real_data.json")

# 映射到我们需要的5个事件
key_events = {
    'trump_military': ['trump-announces-end-of-military-operations-against-iran-by'],
    'us_iran_ceasefire': ['us-x-iran-ceasefire-by'],
    'hormuz_traffic': ['will-iran-close-the-strait-of-hormuz-by-2027'],
    'oil_march': ['will-crude-oil-cl-hit-by-end-of-march'],
}

print("\n=== Key Events Mapping ===")
for key, slugs in key_events.items():
    found = False
    for slug in slugs:
        if slug in markets_data:
            print(f"{key}: {markets_data[slug]['title'][:50]}... ({markets_data[slug]['current_probability']}%)")
            found = True
            break
    if not found:
        print(f"{key}: NOT FOUND - need to check slugs: {slugs}")
