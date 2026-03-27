#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""手动更新嵌入的金十数据到tracking.html"""

import json
import re
from pathlib import Path

WORKDIR = Path(__file__).parent.resolve()

# 读取最新数据
with open(WORKDIR / 'jin10_strait_data.json', 'r', encoding='utf-8') as f:
    latest_data = json.load(f)

# 读取HTML
with open(WORKDIR / 'tracking.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 准备数据JSON
data_json = json.dumps(latest_data, ensure_ascii=False, indent=2)

# 构建新的嵌入脚本
new_embed = f'''<!-- 金十数据嵌入 (更新于 {latest_data['updated'][:19].replace('T', ' ')}) -->
<script id="jin10-embedded-data">
const JIN10_STRAIT_DATA = {data_json};

document.addEventListener('DOMContentLoaded', function() {{
    fillJin10Data(JIN10_STRAIT_DATA);
}});

function fillJin10Data(data) {{
    if (!data) return;
    
    const shipStatusSection = document.getElementById('jin10-ship-status-section');
    if (shipStatusSection) {{
        shipStatusSection.style.display = 'block';
        if (data.ship_counts) {{
            if (data.ship_counts.hormuz_passing !== undefined) {{
                document.getElementById('jin10-hormuz-passing').textContent = data.ship_counts.hormuz_passing;
            }}
            if (data.ship_counts.total_in_area > 0) {{
                document.getElementById('jin10-total-ships').textContent = data.ship_counts.total_in_area.toLocaleString();
            }}
            if (data.ship_counts.sailing !== undefined) {{
                document.getElementById('jin10-sailing').textContent = data.ship_counts.sailing.toLocaleString() + '艘';
            }}
            if (data.ship_counts.anchored !== undefined) {{
                document.getElementById('jin10-anchored').textContent = data.ship_counts.anchored.toLocaleString() + '艘';
            }}
        }}
        if (data.updated) {{
            document.getElementById('jin10-ship-update-time').textContent = data.updated.slice(0, 16).replace('T', ' ');
        }}
    }}
    
    const pressureSection = document.getElementById('jin10-pressure-section');
    if (pressureSection && data.industry_pressure) {{
        pressureSection.style.display = 'block';
        if (data.industry_pressure.total) {{
            const totalPressure = data.industry_pressure.total;
            document.getElementById('jin10-total-pressure').textContent = totalPressure;
            const levelEl = document.getElementById('jin10-pressure-level');
            if (levelEl) {{
                if (totalPressure >= 95) {{ levelEl.textContent = '极高风险'; levelEl.style.background = '#cf1322'; }}
                else if (totalPressure >= 80) {{ levelEl.textContent = '高风险'; levelEl.style.background = '#cf1322'; }}
                else if (totalPressure >= 60) {{ levelEl.textContent = '中等风险'; levelEl.style.background = '#fa8c16'; }}
                else {{ levelEl.textContent = '低风险'; levelEl.style.background = '#52c41a'; }}
            }}
        }}
        const categoryMap = {{ 'oil': 'jin10-oil', 'lng': 'jin10-lng', 'lpg': 'jin10-lpg', 'fertilizer': 'jin10-fertilizer', 'aluminum': 'jin10-aluminum', 'methanol': 'jin10-methanol' }};
        for (const [key, elementId] of Object.entries(categoryMap)) {{
            if (data.industry_pressure[key]) {{
                const value = data.industry_pressure[key].value;
                const el = document.getElementById(elementId);
                if (el) el.textContent = value;
                const barEl = document.getElementById(elementId + '-bar');
                if (barEl) barEl.style.width = value + '%';
            }}
        }}
    }}
}}
</script>'''

# 替换旧数据（从 <!-- 金十数据嵌入 到 </script>）
pattern = r'<!-- 金十数据嵌入.*?<script id="jin10-embedded-data">.*?</script>'
replacement = new_embed

if re.search(pattern, content, re.DOTALL):
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    print('已替换嵌入数据')
else:
    # 查找 <script id="jin10-embedded-data"> 到 </script>
    alt_pattern = r'<script id="jin10-embedded-data">.*?</script>'
    if re.search(alt_pattern, content, re.DOTALL):
        content = re.sub(alt_pattern, replacement, content, flags=re.DOTALL)
        print('已替换嵌入数据（替代方法）')
    else:
        print('未找到嵌入数据标记')

# 保存
with open(WORKDIR / 'tracking.html', 'w', encoding='utf-8') as f:
    f.write(content)

print(f"完成！更新时间: {latest_data['updated']}")
print(f"综合通行压力: {latest_data.get('industry_pressure', {}).get('total')}%")
print(f"正在通过: {latest_data['ship_counts'].get('hormuz_passing')}艘")
print(f"航行中: {latest_data['ship_counts'].get('sailing')}艘")
print(f"锚泊/停靠: {latest_data['ship_counts'].get('anchored')}艘")
