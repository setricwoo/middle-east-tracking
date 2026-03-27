import json
with open('commodities_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

groups = data.get('groups', {})
aluminum_urea = groups.get('aluminum_urea', {})

print('commodities_data.json - aluminum_urea组:')
print('Name:', aluminum_urea.get('name'))
print('Unit:', aluminum_urea.get('unit'))
print()

for item in aluminum_urea.get('symbols', []):
    symbol = item.get('symbol')
    label = item.get('label')
    dates = item.get('dates', [])
    values = item.get('values', [])
    print(f'Symbol: {symbol}, Label: {label}')
    print(f'  Dates: {len(dates)}个')
    if len(dates) > 0:
        print(f'  范围: {dates[0]} ~ {dates[-1]}')
        if len(dates) > 100:
            print(f'  中间样本: {dates[len(dates)//2]} -> {values[len(dates)//2]}')
    print()
