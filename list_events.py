#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json

with open('iran_events.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("Total events:", data['totalEvents'])
print()

for i, e in enumerate(data['events'][:20]):  # 只显示前20个
    print(f"{i+1}. [{e['category']}] {e['title']}")
    print(f"   ID: {e['id']}, Markets: {e['totalMarkets']}")
    print()
