import re
import json

with open('data-tracking.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 查找aluminum_urea组的完整数据
match = re.search(r'aluminum_urea.*?items.*?(\[.*?\])', content, re.DOTALL)
if match:
    # 找到方括号的开始
    start = content.find('[', match.start())
    bracket_count = 0
    data_str = None
    for i in range(start, min(start + 50000, len(content))):
        if content[i] == '[':
            bracket_count += 1
        elif content[i] == ']':
            bracket_count -= 1
            if bracket_count == 0:
                data_str = content[start:i+1]
                break
    
    if data_str:
        try:
            items = json.loads(data_str)
            print('Aluminum_Urea组的商品:')
            for item in items:
                symbol = item.get('symbol')
                label = item.get('label')
                dates = item.get('dates', [])
                values = item.get('values', [])
                print(f"  Symbol: {symbol}, Label: {label}")
                print(f"    Dates: {len(dates)}个, Values: {len(values)}个")
                if dates:
                    print(f"    范围: {dates[0]} ~ {dates[-1]}")
                print()
        except Exception as e:
            print(f'Parse error: {e}')
            print('Raw data (first 5000 chars):')
            print(data_str[:5000])
