import re, json

with open('data-tracking.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到 STATIC_EXCEL_DATA
match = re.search(r'STATIC_EXCEL_DATA = (\{.*?\});', content, re.DOTALL)
if match:
    data = json.loads(match.group(1))
    
    # 找到aluminum_urea组
    groups = data.get('commodity_groups', {})
    al_urea = groups.get('aluminum_urea', {})
    
    print('aluminum_urea组:')
    for item in al_urea.get('items', []):
        dates = item.get('dates', [])
        print(f"  {item.get('name')}: {len(dates)}条")
        if dates:
            print(f"    第一条: {dates[0]}")
            print(f"    最后一条: {dates[-1]}")
