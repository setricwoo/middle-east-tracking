with open('data-tracking-static.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# 找到每个tab的开始和结束
tabs = []
current_tab = None
depth = 0

for i, line in enumerate(lines):
    stripped = line.strip()
    
    # 检测tab开始
    if '<div id="tab-' in stripped and 'tab-content' in stripped:
        tab_id = stripped.split('id="')[1].split('"')[0]
        current_tab = tab_id
        tabs.append({'id': tab_id, 'start': i+1, 'end': None})
        depth = 1
    elif current_tab:
        # 计算div深度
        if '<div' in stripped and not stripped.endswith('/>'):
            opens = stripped.count('<div')
            closes = stripped.count('</div>')
            depth += opens - closes
            if depth == 0:
                tabs[-1]['end'] = i+1
                current_tab = None

for tab in tabs:
    print(f"{tab['id']}: lines {tab['start']}-{tab['end']}")
