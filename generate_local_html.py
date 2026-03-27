#!/usr/bin/env python3
"""
生成本地查看版HTML文件
将JSON数据嵌入到HTML中，双击即可查看
"""

import json
import csv
from pathlib import Path

# 读取数据文件
def load_json(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def load_csv_data(filename):
    data = []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
    except:
        pass
    return data

# 生成data-tracking的本地版本
print("=== 生成 data-tracking_local.html ===")

# 读取原始HTML
with open('data-tracking.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 加载各种数据文件
jin10_data = load_json('jin10_strait_data.json')
liquidity_data = load_json('liquidity_data.json')
strait_data = load_json('strait_data.json')
isw_data = load_json('isw_update.json')
market_data = load_json('market_data.json')

# 加载历史CSV数据
csv_data = load_csv_data('历史.csv')

# 准备嵌入的数据脚本
data_script = f"""<script>
// 本地嵌入的数据（解决CORS问题）
window.LOCAL_DATA = {{
    jin10: {json.dumps(jin10_data, ensure_ascii=False)},
    liquidity: {json.dumps(liquidity_data, ensure_ascii=False)},
    strait: {json.dumps(strait_data, ensure_ascii=False)},
    isw: {json.dumps(isw_data, ensure_ascii=False)},
    market: {json.dumps(market_data, ensure_ascii=False)},
    csv: {json.dumps(csv_data[-60:], ensure_ascii=False)}  // 最近60天
}};

// 覆盖fetch函数，优先使用本地数据
const originalFetch = window.fetch;
window.fetch = function(url, options) {{
    const urlStr = url.toString();
    if (urlStr.includes('jin10_strait_data.json')) {{
        return Promise.resolve({{
            ok: true,
            json: () => Promise.resolve(window.LOCAL_DATA.jin10)
        }});
    }}
    if (urlStr.includes('liquidity_data.json')) {{
        return Promise.resolve({{
            ok: true,
            json: () => Promise.resolve(window.LOCAL_DATA.liquidity)
        }});
    }}
    if (urlStr.includes('strait_data.json')) {{
        return Promise.resolve({{
            ok: true,
            json: () => Promise.resolve(window.LOCAL_DATA.strait)
        }});
    }}
    if (urlStr.includes('isw_update.json')) {{
        return Promise.resolve({{
            ok: true,
            json: () => Promise.resolve(window.LOCAL_DATA.isw)
        }});
    }}
    if (urlStr.includes('market_data.json')) {{
        return Promise.resolve({{
            ok: true,
            json: () => Promise.resolve(window.LOCAL_DATA.market)
        }});
    }}
    if (urlStr.includes('历史.csv')) {{
        // 返回一个模拟的Response对象
        const csvContent = window.LOCAL_DATA.csv.map(row => Object.values(row).join(',')).join('\\n');
        return Promise.resolve({{
            ok: true,
            text: () => Promise.resolve(csvContent)
        }});
    }}
    return originalFetch(url, options);
}};
</script>
"""

# 将数据脚本插入到HTML头部
html_with_data = html.replace('<head>', f'<head>\n{data_script}')

# 保存为本地版
output_file = 'data-tracking_local.html'
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html_with_data)

print(f"[OK] 已生成: {output_file}")
print(f"\n包含数据:")
print(f"   - 金十数据: {'[OK] 已嵌入' if jin10_data else '[MISSING] 未找到 (使用空数据)'}")
print(f"   - 流动性数据: {'[OK] 已嵌入' if liquidity_data else '[MISSING] 未找到 (使用空数据)'}")
print(f"   - 海峡数据: {'[OK] 已嵌入' if strait_data else '[MISSING] 未找到 (使用空数据)'}")
print(f"   - ISW数据: {'[OK] 已嵌入' if isw_data else '[MISSING] 未找到 (使用空数据)'}")
print(f"   - 市场数据: {'[OK] 已嵌入' if market_data else '[MISSING] 未找到 (使用空数据)'}")
print(f"   - CSV数据: {len(csv_data)} 条记录")
print(f"\n双击 {output_file} 即可直接查看（无需服务器）")
