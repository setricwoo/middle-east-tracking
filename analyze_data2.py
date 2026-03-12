#!/usr/bin/env python3
import json

with open('next_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

state = data['props']['pageProps']['dehydratedState']

# 找到事件查询
for q in state['queries']:
    query_key = q.get("queryKey", [])
    if isinstance(query_key, list) and len(query_key) > 0 and query_key[0] == 'events':
        print("Found events query!")
        print(f"queryKey: {query_key}")
        
        event_data = q['state']['data']
        print(f"\nData keys: {event_data.keys()}")
        
        if 'pages' in event_data:
            pages = event_data['pages']
            print(f"\nPages count: {len(pages)}")
            
            for page_idx, page in enumerate(pages):
                print(f"\n--- Page {page_idx} ---")
                if isinstance(page, dict) and 'events' in page:
                    events = page['events']
                    print(f"Events count: {len(events)}")
                    
                    # 打印前几个事件的详细信息
                    for i, event in enumerate(events[:3]):
                        print(f"\n  Event {i}:")
                        print(f"    title: {event.get('title', 'N/A')}")
                        print(f"    slug: {event.get('slug', 'N/A')}")
                        print(f"    id: {event.get('id', 'N/A')}")
                        
                        # 查找markets
                        if 'markets' in event:
                            markets = event['markets']
                            print(f"    markets count: {len(markets)}")
                            for j, m in enumerate(markets[:2]):
                                print(f"      Market {j}:")
                                print(f"        id: {m.get('id', 'N/A')}")
                                print(f"        question: {m.get('question', 'N/A')[:80]}...")
                                print(f"        outcomePrices: {m.get('outcomePrices', 'N/A')}")
                                print(f"        probability: {m.get('probability', 'N/A')}")
                                print(f"        volume: {m.get('volume', 'N/A')}")
                elif isinstance(page, list):
                    print(f"Page is a list with {len(page)} items")
                    for i, item in enumerate(page[:2]):
                        if isinstance(item, dict):
                            print(f"  Item {i} keys: {list(item.keys())[:5]}")

print("\n\nSearching for all event slugs...")
all_slugs = []
for q in state['queries']:
    if 'state' in q and 'data' in q['state']:
        d = q['state']['data']
        if isinstance(d, dict) and 'pages' in d:
            for page in d['pages']:
                if isinstance(page, dict) and 'events' in page:
                    for event in page['events']:
                        if 'slug' in event:
                            all_slugs.append(event['slug'])

print(f"Found {len(all_slugs)} slugs:")
for slug in all_slugs[:20]:
    print(f"  {slug}")
