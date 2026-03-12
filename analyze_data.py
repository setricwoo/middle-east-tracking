#!/usr/bin/env python3
import json

with open('next_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 导航到 dehydratedState
state = data['props']['pageProps']['dehydratedState']
print(f"dehydratedState type: {type(state)}")
print(f"Keys: {list(state.keys())[:10]}")

if 'queries' in state:
    print(f"\nQueries count: {len(state['queries'])}")
    for i, q in enumerate(state['queries'][:5]):
        print(f"\nQuery {i}:")
        query_key = q.get("queryKey", "N/A")
        print(f"  queryKey: {query_key}")
        if 'state' in q and 'data' in q['state']:
            d = q['state']['data']
            if isinstance(d, dict):
                print(f"  data keys: {list(d.keys())[:5]}")
            elif isinstance(d, list):
                print(f"  data length: {len(d)}")
                if len(d) > 0 and isinstance(d[0], dict):
                    print(f"  first item keys: {list(d[0].keys())[:5]}")
