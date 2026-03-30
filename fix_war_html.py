#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复 war-situation.html 中的 ISW 数据
"""

import json
import re

# 读取正确的数据
with open('isw_data_fixed.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 转换为 JSON 字符串
output = json.dumps(data, ensure_ascii=False, separators=(',', ':'))

# 读取 HTML
with open('war-situation.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换 STATIC_ISW_DATA
pattern = r'(let STATIC_ISW_DATA = ).*?(;</script>)'
replacement = r'\1' + output + r'\2'
new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# 写回
with open('war-situation.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("[OK] war-situation.html 已修复")

# 验证
with open('war-situation.html', 'r', encoding='utf-8') as f:
    verify = f.read()
    if '【霍吉尔军事综合体' in verify:
        print("[OK] 中文内容验证通过")
    else:
        print("[警告] 未找到中文内容")
        # 查找实际内容
        idx = verify.find('霍吉尔')
        if idx > 0:
            print(f"找到'霍吉尔'在位置 {idx}")
            print(f"周围内容: {verify[idx-10:idx+50]}")
