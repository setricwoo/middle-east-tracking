import json

# 读取HTML
with open('data-tracking.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 读取商品数据
with open('commodities_data.json', 'r', encoding='utf-8') as f:
    commodities_data = json.load(f)

# 在 STATIC_ISW_DATA 后添加 STATIC_COMMODITIES_DATA
insert_after = 'let STATIC_ISW_DATA = '
insert_pos = html.find(insert_after)
if insert_pos > 0:
    # 找到 STATIC_ISW_DATA 的结束位置（分号）
    data_start = insert_pos
    # 找到这个变量的结束
    bracket_count = 0
    in_data = False
    i = data_start
    while i < len(html):
        if html[i] == '{':
            bracket_count += 1
            in_data = True
        elif html[i] == '}':
            bracket_count -= 1
            if in_data and bracket_count == 0:
                # 找到结束位置，现在找分号
                i += 1
                while i < len(html) and html[i] != ';':
                    i += 1
                insert_pos = i + 1  # 在分号后插入
                break
        i += 1
    
    # 插入新数据
    new_data = '\n    let STATIC_COMMODITIES_DATA = ' + json.dumps(commodities_data, ensure_ascii=False) + ';'
    html = html[:insert_pos] + new_data + html[insert_pos:]
    
    # 保存
    with open('data-tracking.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print('✓ 已嵌入 STATIC_COMMODITIES_DATA')
else:
    print('✗ 未找到插入位置')
