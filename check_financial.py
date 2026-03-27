import re, json

with open('data-tracking.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 查找 STATIC_EXCEL_DATA 中的 financial 部分
match = re.search(r'STATIC_EXCEL_DATA = (\{.*?\});', content, re.DOTALL)
if match:
    data = json.loads(match.group(1))
    financial = data.get('financial', {})
    stocks = financial.get('stocks', {})
    
    print('Excel数据中的金融市场数据:')
    print(f'  股票数量: {len(stocks)}')
    for key, val in stocks.items():
        name = val.get('name')
        count = len(val.get('dates', []))
        latest = val.get('latest')
        print(f'    {name}: {count}条, 最新={latest}')
