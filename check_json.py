import json
with open('commodities_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

groups = data.get('groups', {})
aluminum_urea = groups.get('aluminum_urea', {})

print('commodities_data.json - aluminum_urea组:')
print('Name:', aluminum_urea.get('name'))
print('Unit:', aluminum_urea.get('unit'))
print('Symbols:')
for item in aluminum_urea.get('symbols', []):
    print(f"  - {item.get('symbol')}: {item.get('label')}")
