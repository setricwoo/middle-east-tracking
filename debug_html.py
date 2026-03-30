#!/usr/bin/env python3
import re

with open('war-situation.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 查找 STATIC_ISW_DATA
if 'STATIC_ISW_DATA' in content:
    print("找到 STATIC_ISW_DATA")
    # 找位置
    pos = content.find('STATIC_ISW_DATA')
    print(f"位置: {pos}")
    # 显示片段
    snippet = content[pos:pos+200]
    print(f"片段: {snippet[:200]}")
else:
    print("未找到 STATIC_ISW_DATA")
