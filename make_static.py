#!/usr/bin/env python3
"""
将 data-tracking.html 转为静态版本
直接注入数据，移除动态获取
"""
import json
import re
from datetime import datetime
from zoneinfo import ZoneInfo

# 加载数据
with open('strait_data.json', 'r', encoding='utf-8') as f:
    strait_data = json.load(f)

with open('market_data.json', 'r', encoding='utf-8') as f:
    market_data = json.load(f)

with open('liquidity_data.json', 'r', encoding='utf-8') as f:
    liquidity_data = json.load(f)

with open('polymarket_real_data.json', 'r', encoding='utf-8') as f:
    pm_data = json.load(f)

# 读取原始 HTML
with open('data-tracking.html', 'r', encoding='utf-8') as f:
    html = f.read()

jin10 = strait_data.get('jin10', {})
sc = jin10.get('ship_counts', {})
ip = jin10.get('industry_pressure', {})

# 1. 更新页面时间
now = datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M")
html = re.sub(r'id="page-update-time"[^>]*>[^<]*</div>', f'id="page-update-time">更新: {now}</div>', html)

# 2. 更新海峡数据
html = re.sub(r'id="strait-update-time"[^>]*>[^<]*</span>', 
    f'id="strait-update-time" style="font-size: 0.75rem; color: #94a3b8;">更新: {jin10.get("updated", "--")[:16].replace("T", " ")}</span>', html)

html = re.sub(r'id="jin10-hormuz-passing"[^>]*>[^<]*</span>',
    f'id="jin10-hormuz-passing" style="font-size: 2.5rem; font-weight: 700; color: #fa8c16; line-height: 1;">{sc.get("hormuz_passing", "--")}</span>', html)

html = re.sub(r'id="jin10-total-ships"[^>]*>[^<]*</span>',
    f'id="jin10-total-ships" style="font-size: 1.8rem; font-weight: 700; color: #262626;">{sc.get("total_in_area", 0):,}</span>', html)

html = re.sub(r'id="jin10-sailing"[^>]*>[^<]*</div>',
    f'id="jin10-sailing" style="color: #1890ff;">{sc.get("sailing", "--")}艘</div>', html)

html = re.sub(r'id="jin10-anchored"[^>]*>[^<]*</div>',
    f'id="jin10-anchored" style="color: #f5222d;">{sc.get("anchored", "--")}艘</div>', html)

# 压力系数
total_p = ip.get('total', 0)
if total_p >= 95:
    risk_level, risk_color = "极高风险", "#7f1d1d"
elif total_p >= 80:
    risk_level, risk_color = "高风险", "#cf1322"
elif total_p >= 60:
    risk_level, risk_color = "中等风险", "#fa8c16"
else:
    risk_level, risk_color = "低风险", "#52c41a"

html = re.sub(r'id="jin10-total-pressure"[^>]*>[^<]*</span>',
    f'id="jin10-total-pressure" style="font-size: 2rem; font-weight: 800; color: #cf1322; line-height: 1;">{total_p}</span>', html)

html = re.sub(r'id="jin10-pressure-level"[^>]*>[^<]*</div>',
    f'id="jin10-pressure-level" style="padding: 4px 12px; background: {risk_color}; color: white; border-radius: 12px; font-size: 0.75rem; font-weight: 500;">{risk_level}</div>', html)

# 各品类
cat_map = {'oil': 'jin10-oil', 'lng': 'jin10-lng', 'lpg': 'jin10-lpg', 
           'fertilizer': 'jin10-fertilizer', 'aluminum': 'jin10-aluminum', 'methanol': 'jin10-methanol'}

for key, elem_id in cat_map.items():
    val = ip.get(key, {}).get('value', 0)
    display = f"{val:.1f}" if val else "--"
    html = re.sub(rf'id="{elem_id}"[^>]*>[^<]*</span>', 
        f'id="{elem_id}" style="font-size: 1.1rem; font-weight: 700; color: #262626;">{display}</span>%', html)
    bar_w = f"{val}%" if val else "0%"
    html = re.sub(rf'id="{elem_id}-bar"[^>]*style="[^"]*width:[^;]*;',
        f'id="{elem_id}-bar" style="height: 100%; width: {bar_w};', html)

# 视频和快照
if jin10.get('video_url'):
    html = re.sub(r'<source[^>]*src="[^"]*"[^>]*>', f'<source src="{jin10["video_url"]}" type="video/mp4">', html)
if jin10.get('snapshot_url'):
    html = re.sub(r'id="strait-snapshot"[^>]*src="[^"]*"', f'id="strait-snapshot" src="{jin10["snapshot_url"]}"', html)

# 移除动态加载脚本，保留图表初始化
# 找到 loadStraitData 调用并注释掉
html = re.sub(r'loadStraitData\(\);', '// loadStraitData(); // 静态页面已注入数据', html)

# 保存
with open('data-tracking-static.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Static HTML saved: data-tracking-static.html")
print(f"Updated at: {now}")
