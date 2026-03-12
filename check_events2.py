import json
with open('iran_events.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=" * 60)
print("查找特朗普相关事件")
print("=" * 60)
for e in data['events']:
    title = e.get('title', '').lower()
    if 'trump' in title or 'military' in title or 'announce' in title:
        print(f"ID: {e['id']}")
        print(f"Title: {e['title']}")
        print(f"Category: {e['category']}")
        for m in e.get('markets', []):
            print(f"  - {m['question']}")
        print('---')

print("\n" + "=" * 60)
print("查找霍尔木兹海峡交通恢复")
print("=" * 60)
for e in data['events']:
    title = e.get('title', '').lower()
    desc = e.get('description', '').lower()
    if 'traffic' in title or 'restore' in title or 'resume' in title or '正常' in title:
        print(f"ID: {e['id']}")
        print(f"Title: {e['title']}")
        print(f"Category: {e['category']}")
        for m in e.get('markets', []):
            print(f"  - {m['question']}")
        print('---')

print("\n" + "=" * 60)
print("查找原油价格 - 6月底")
print("=" * 60)
for e in data['events']:
    title = e.get('title', '').lower()
    if 'crude' in title and 'june' in title:
        print(f"ID: {e['id']}")
        print(f"Title: {e['title']}")
        print(f"Category: {e['category']}")
        for m in e.get('markets', []):
            print(f"  - {m['question']}")
        print('---')
