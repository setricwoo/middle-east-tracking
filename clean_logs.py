#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('data-tracking.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 删除 console.log 中引用已删除变量的行
import re

# 删除包含 STATIC_STRAIT_DATA 或 STATIC_ISW_DATA 的 console.log 行
content = re.sub(r"\s*console\.log\('STATIC_STRAIT_DATA:[^;]+;", "", content)
content = re.sub(r"\s*console\.log\('STATIC_ISW_DATA:[^;]+;", "", content)

# 或者更精确地删除这些特定行
lines = content.split('\n')
filtered = []
for line in lines:
    if "STATIC_STRAIT_DATA:" in line and "console.log" in line:
        continue
    if "STATIC_ISW_DATA:" in line and "console.log" in line:
        continue
    filtered.append(line)

with open('data-tracking.html', 'w', encoding='utf-8') as f:
    f.write('\n'.join(filtered))

print(f'清理完成，剩余行数: {len(filtered)}')
