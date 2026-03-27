import json
import re

with open('data-tracking.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 查找STATIC_COMMODITIES_DATA中的aluminum_urea组
match = re.search(r'STATIC_COMMODITIES_DATA = (\{.*?\});', content, re.DOTALL)
if match:
    data_str = match.group(1)
    # 找到aluminum_urea的位置
    start = data_str.find('"aluminum_urea"')
    if start > 0:
        # 从这个位置开始找items数组
        items_start = data_str.find('"items":', start)
        if items_start > 0:
            # 找到方括号开始
            bracket_start = data_str.find('[', items_start)
            bracket_count = 0
            for i in range(bracket_start, min(bracket_start + 10000, len(data_str))):
                if data_str[i] == '[':
                    bracket_count += 1
                elif data_str[i] == ']':
                    bracket_count -= 1
                    if bracket_count == 0:
                        items_str = data_str[bracket_start:i+1]
                        try:
                            items = json.loads(items_str)
                            print('STATIC_COMMODITIES_DATA - aluminum_urea组的商品:')
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
                            print(items_str[:2000])
                        break
