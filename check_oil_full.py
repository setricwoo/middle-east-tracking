#!/usr/bin/env python3
import json

with open('next_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

state = data['props']['pageProps']['dehydratedState']

# 找到事件数据
for q in state['queries']:
    query_key = q.get("queryKey", [])
    if isinstance(query_key, list) and query_key[0] == 'events':
        event_data = q['state']['data']
        if 'pages' in event_data:
            for page in event_data['pages']:
                if isinstance(page, dict) and 'events' in page:
                    for event in page['events']:
                        slug = event.get('slug', '')
                        if 'crude-oil' in slug and 'march' in slug:
                            print(f"Event: {slug}")
                            print(f"Title: {event.get('title', '')}")
                            print(f"\nMarkets ({len(event.get('markets', []))}):")
                            for i, m in enumerate(event.get('markets', [])):
                                print(f"\n  Market {i}:")
                                print(f"    ID: {m.get('id', '')}")
                                print(f"    Question: {m.get('question', '')}")
                                print(f"    Outcome Prices: {m.get('outcomePrices', [])}")
                                print(f"    Volume: {m.get('volume', 0)}")
                                print(f"    Description: {m.get('description', '')[:100]}...")
