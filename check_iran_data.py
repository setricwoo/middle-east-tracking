#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

with open('iran_events.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=" * 60)
print("检查伊朗相关事件数据")
print("=" * 60)
print(f"\n数据更新时间: {data.get('updatedAt', 'Unknown')}")
print(f"总事件数: {data.get('totalEvents', 0)}")

# 查找包含Iran的事件
keywords = ['iran', 'iranian', 'hormuz', 'ceasefire', 'crude', 'oil', 'trump', 'military']
iran_events = []

for e in data.get('events', []):
    title = e.get('title', '').lower()
    desc = e.get('description', '').lower()
    text = title + ' ' + desc
    if any(k in text for k in keywords):
        iran_events.append(e)

print(f"\n找到 {len(iran_events)} 个相关事件:")
print("-" * 60)

for e in iran_events:
    cat = e.get('category', 'N/A')
    title = e.get('title', 'N/A')
    markets = e.get('totalMarkets', 0)
    print(f"\n[{cat}] {title}")
    print(f"  市场数: {markets}")
    for m in e.get('markets', [])[:3]:
        q = m.get('question', '')
        probs = m.get('probabilities', [])
        yes_prob = next((p.get('probability', 0) for p in probs if p.get('outcome') == 'Yes'), 0)
        print(f"    - {q[:60]}... ({yes_prob}%)")
    if len(e.get('markets', [])) > 3:
        print(f"    ... 还有 {len(e.get('markets')) - 3} 个市场")
