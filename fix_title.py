# -*- coding: utf-8 -*-
with open('tracking.html', 'r', encoding='utf-8') as f:
    content = f.read()

old_title = '伊朗新领袖强硬表态：继续封锁海峡'
new_title = '伊朗行动：已击中10余艘商船'

if old_title in content:
    content = content.replace(old_title, new_title, 1)  # 只替换第一个出现
    with open('tracking.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Title updated successfully')
else:
    print('Old title not found')
    # 尝试打印相关内容
    import re
    matches = re.findall(r'伊朗[^<]{0,20}', content)
    for m in matches[:10]:
        print(repr(m))
