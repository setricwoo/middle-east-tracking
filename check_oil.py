#!/usr/bin/env python3
import json
with open('polymarket_real_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 查看原油市场的详细信息
for slug, info in data.items():
    if 'oil' in slug or 'crude' in slug:
        print(f'{slug}:')
        print(f"  Title: {info['title']}")
        print(f"  Probability: {info['current_probability']}%")
        print(f"  Volume: {info['volume']}")
        print()
