#!/usr/bin/env python3
"""
使用Gamma API获取的真实数据更新HTML
"""
import json
from datetime import datetime

# 读取数据
with open('midterm_chart_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 提取数据
house_r = data['house_republican']
house_d = data['house_democratic']
senate_r = data['senate_republican']
senate_d = data['senate_democratic']

# 提取最近的30个点
labels = [h['time'] for h in house_r['history'][-30:]]
house_r_data = [h['probability'] for h in house_r['history'][-30:]]
house_d_data = [h['probability'] for h in house_d['history'][-30:]]
senate_r_data = [h['probability'] for h in senate_r['history'][-30:]]
senate_d_data = [h['probability'] for h in senate_d['history'][-30:]]

# 读取HTML
with open('polymarket.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 替换众议院数据
html = html.replace(
    '<div class="text-3xl font-bold" style="color: #e11d48">85%</div>',
    f'<div class="text-3xl font-bold" style="color: #e11d48">{house_r["current"]}%</div>'
)
html = html.replace(
    '<div class="text-3xl font-bold" style="color: #2563eb">15%</div>',
    f'<div class="text-3xl font-bold" style="color: #2563eb">{house_d["current"]}%</div>'
)

# 替换参议院数据  
html = html.replace(
    '<div class="text-3xl font-bold" style="color: #e11d48">47%</div>',
    f'<div class="text-3xl font-bold" style="color: #e11d48">{senate_r["current"]}%</div>'
)
html = html.replace(
    '<div class="text-3xl font-bold" style="color: #2563eb">53%</div>',
    f'<div class="text-3xl font-bold" style="color: #2563eb">{senate_d["current"]}%</div>'
)

# 替换众议院图表数据
old_house_labels = "['03-01', '03-05', '03-10', '03-15', '03-20', '03-24']"
old_house_r = "[82, 83, 84, 84, 85, 85]"
old_house_d = "[18, 17, 16, 16, 15, 15]"

html = html.replace(
    f"labels: {old_house_labels}",
    f"labels: {labels}"
)
html = html.replace(
    f"data: {old_house_r}",
    f"data: {house_r_data}",
    1  # 只替换第一个（众议院）
)
html = html.replace(
    f"data: {old_house_d}",
    f"data: {house_d_data}",
    1  # 只替换第一个（众议院）
)

# 替换参议院图表数据
old_senate_labels = "['03-01', '03-05', '03-10', '03-15', '03-20', '03-24']"
old_senate_r = "[45, 46, 47, 47, 47, 47]"
old_senate_d = "[55, 54, 53, 53, 53, 53]"

# 找到参议院图表的位置并替换
senate_start = html.find("chart_senate")
if senate_start != -1:
    # 替换参议院labels
    senate_labels_start = html.find(old_senate_labels, senate_start)
    if senate_labels_start != -1:
        html = html[:senate_labels_start] + f"labels: {labels}" + html[senate_labels_start + len(old_senate_labels):]
    
    # 替换参议院共和党数据
    senate_r_start = html.find(old_senate_r, senate_start)
    if senate_r_start != -1:
        html = html[:senate_r_start] + f"data: {senate_r_data}" + html[senate_r_start + len(old_senate_r):]
    
    # 替换参议院民主党数据
    senate_d_start = html.find(old_senate_d, senate_start)
    if senate_d_start != -1:
        html = html[:senate_d_start] + f"data: {senate_d_data}" + html[senate_d_start + len(old_senate_d):]

# 保存
with open('polymarket.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("HTML updated with real Gamma API data!")
print(f"\nHouse:")
print(f"  Republican: {house_r['current']}%")
print(f"  Democratic: {house_d['current']}%")
print(f"\nSenate:")
print(f"  Republican: {senate_r['current']}%")
print(f"  Democratic: {senate_d['current']}%")
print(f"\nData points: {len(labels)} (hourly)")
print(f"Time range: {labels[0]} -> {labels[-1]}")
print(f"\nSources:")
print(f"  House: https://polymarket.com/zh/event/which-party-will-win-the-house-in-2026 (Event ID: 32225)")
print(f"  Senate: https://polymarket.com/zh/event/which-party-will-win-the-senate-in-2026 (Event ID: 32224)")
print(f"  API: gamma-api.polymarket.com + clob.polymarket.com")
