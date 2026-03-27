import re, json

with open('data-tracking.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到最新的 STATIC_COMMODITIES_DATA（最后一个）
matches = list(re.finditer(r'STATIC_COMMODITIES_DATA = (\{.*?\});', content, re.DOTALL))
if matches:
    data_str = matches[-1].group(1)
    data = json.loads(data_str)
    
    groups = data.get('groups', {})
    aluminum_urea = groups.get('aluminum_urea', {})
    
    print('aluminum_urea组:')
    for sym in aluminum_urea.get('symbols', []):
        dates = sym.get('dates', [])
        values = sym.get('values', [])
        print(f"  {sym.get('label')}: {len(dates)}条数据")
        if len(dates) > 0:
            print(f"    第一条: {dates[0]} -> {values[0]}")
            print(f"    最后一条: {dates[-1]} -> {values[-1]}")
            # 显示中间的一条
            mid = len(dates) // 2
            print(f"    中间条: {dates[mid]} -> {values[mid]}")
