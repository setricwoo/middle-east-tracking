import json

with open('iran_events.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

events = data['events']
print('Total events:', len(events))
for i, e in enumerate(events):
    print(f"{i+1}. {e['category']}: {e['title']}")
    for m in e['markets'][:3]:
        print(f"   - {m['question'][:60]}...")
    if len(e['markets']) > 3:
        print(f"   ... and {len(e['markets'])-3} more markets")
