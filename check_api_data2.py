import json
import re

with open('data-tracking.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 查找STATIC_COMMODITIES_DATA
match = re.search(r'STATIC_COMMODITIES_DATA = (\{.*?\});', content, re.DOTALL)
if match:
    data_str = match.group(1)
    data = json.loads(data_str)
    
    groups = data.get('groups', {})
    aluminum_urea = groups.get('aluminum_urea', {})
    
    print('STATIC_COMMODITIES_DATA - aluminum_urea组:')
    print(f"  Name: {aluminum_urea.get('name')}")
    print(f"  Unit: {aluminum_urea.get('unit')}")
    print(f"  Items:")
    
    for item in aluminum_urea.get('symbols', []):
        symbol = item.get('symbol')
        label = item.get('label')
        dates = item.get('dates', [])
        values = item.get('values', [])
        print(f"    Symbol: {symbol}, Label: {label}")
        print(f"      Dates: {len(dates)}个, Values: {len(values)}个")
        if dates:
            print(f"      范围: {dates[0]} ~ {dates[-1]}")
        print()
