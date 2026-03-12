#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os

print("=" * 60)
print("Polymarket 数据状态检查")
print("=" * 60)

# 检查现有的iran_events.json
if os.path.exists('iran_events.json'):
    with open('iran_events.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"\n1. iran_events.json:")
    print(f"   更新时间: {data.get('updatedAt', 'Unknown')}")
    print(f"   事件数量: {data.get('totalEvents', 0)}")
    
    # 检查是否有伊朗相关事件
    events = data.get('events', [])
    iran_events = []
    for e in events:
        title = e.get('title', '').lower()
        if any(k in title for k in ['iran', 'hormuz', 'ceasefire', 'crude', 'trump']):
            iran_events.append(e.get('title', 'N/A')[:50])
    
    if iran_events:
        print(f"   伊朗相关事件: {len(iran_events)}个")
        for t in iran_events[:3]:
            print(f"      - {t}")
    else:
        print(f"   警告: 未找到伊朗相关事件（只有体育博彩数据）")
else:
    print("\n1. iran_events.json: 不存在")

# 检查其他数据文件
files = ['polymarket_real_data.json', 'polymarket_merged.json', 'hourly_data_for_web.json']
for fname in files:
    print(f"\n2. {fname}:")
    if os.path.exists(fname):
        with open(fname, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"   状态: 存在 ({len(str(data))} 字符)")
        if 'markets' in data:
            markets = list(data['markets'].keys())
            print(f"   市场: {markets}")
    else:
        print(f"   状态: 不存在")

print("\n" + "=" * 60)
print("结论:")
print("=" * 60)
print("目前网页使用的是 generate_hourly.py 中的模拟数据，")
print("而非从 Polymarket API 获取的真实数据。")
print("\n要获取真实数据，需要:")
print("1. 从 Polymarket 网站找到具体市场的 slug")
print("2. 或者手动从网站复制数据填入脚本")
print("=" * 60)
