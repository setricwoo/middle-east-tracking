#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 查找嵌入数据
start = content.find('const JIN10_STRAIT_DATA = {')
if start > 0:
    # 找到匹配的结束括号
    brace_count = 0
    end = start
    for i, char in enumerate(content[start:]):
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                end = start + i + 1
                break
    
    data_size = (end - start) / 1024
    print(f'嵌入的 JIN10_STRAIT_DATA 大小: 约 {data_size:.1f} KB')
    
    # 检查是否有base64图片
    data_section = content[start:end]
    base64_count = data_section.count('data:image')
    print(f'其中包含 {base64_count} 个base64图片')
    
    # 计算base64部分大小
    base64_urls = re.findall(r'data:image/[^;]+;base64,[^"\'\s]+', data_section)
    total_base64 = sum(len(u) for u in base64_urls)
    print(f'base64数据总大小: 约 {total_base64/1024:.1f} KB')
else:
    print('未找到嵌入数据')
