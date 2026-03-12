import json
with open('iran_events.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
for e in data['events']:
    if 'crude' in e['title'].lower() or 'oil' in e['title'].lower():
        print(f"Category: {e['category']}")
        print(f"Title: {e['title']}")
        for m in e['markets']:
            print(f"  - {m['question']}")
        print()
