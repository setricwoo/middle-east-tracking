#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('data-tracking.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

lines_to_remove = []

# 1. 找到并删除 straitChart 和相关函数
for i in range(len(lines)-1):
    if '// ═══════════════════════════════════════════════════════════════' in lines[i] and i+1 < len(lines) and 'var straitChart' in lines[i+1]:
        start = i
        for j in range(i+1, len(lines)):
            if j+1 < len(lines) and '// ═══════════════════════════════════════════════════════════════' in lines[j] and '商品价格数据' in lines[j+1]:
                lines_to_remove.extend(range(start, j))
                print(f'找到海峡代码块: 第{start+1}行到第{j}行')
                break
        break

# 2. 找到并删除 ISW 代码块
for i in range(len(lines)-1):
    if '// ISW战局数据' in lines[i]:
        start = i - 1
        for j in range(i+1, len(lines)):
            if j+1 < len(lines) and '// ═══════════════════════════════════════════════════════════════' in lines[j] and '页面初始化' in lines[j+1]:
                lines_to_remove.extend(range(start, j))
                print(f'找到ISW代码块: 第{start+1}行到第{j}行')
                break
        break

# 3. 删除初始化调用
for i, line in enumerate(lines):
    if 'updateStraitData()' in line or 'updateISWData()' in line:
        lines_to_remove.append(i)
        print(f'找到初始化调用: 第{i+1}行')

# 去重并排序
lines_to_remove = sorted(set(lines_to_remove), reverse=True)

print(f'\n总共需要删除 {len(lines_to_remove)} 行')

# 删除行
for idx in lines_to_remove:
    del lines[idx]

with open('data-tracking.html', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f'删除完成，新文件行数: {len(lines)}')
