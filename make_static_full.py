#!/usr/bin/env python3
"""
完全静态化数据跟踪网页
将所有数据直接嵌入HTML，移除所有fetch请求
"""
import json
import re
from datetime import datetime
from zoneinfo import ZoneInfo

def load_json(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载 {filename} 失败: {e}")
        return None

# 加载所有数据
strait_data = load_json('strait_data.json')
market_data = load_json('market_data.json')
liquidity_data = load_json('liquidity_data.json')
isw_data = load_json('isw_data.json')

# 读取原始HTML
with open('data-tracking.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ========== 1. 更新海峡通行数据 ==========
if strait_data and 'jin10' in strait_data:
    jin10 = strait_data['jin10']
    sc = jin10.get('ship_counts', {})
    ip = jin10.get('industry_pressure', {})
    
    # 基础数据替换
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

# ========== 2. 静态化全球流动性 Tab ==========
if liquidity_data:
    # FCI 数据
    fci = liquidity_data.get('fci', {})
    fci_latest = fci.get('latest', '--')
    fci_hist = fci.get('hist', [])
    
    # 生成FCI图表数据嵌入
    fci_labels = [item[0] for item in fci_hist[-20:]] if fci_hist else []
    fci_values = [item[1] for item in fci_hist[-20:]] if fci_hist else []
    
    # 替换FCI显示
    html = re.sub(
        r'<div id="fci-info"[^>]*>.*?</div>',
        f'<div id="fci-info" style="font-size:.82rem;color:#64748b;margin:6px 0;">当前: <b>{fci_latest}</b> | 来源: 芝加哥联储</div>',
        html, flags=re.DOTALL
    )
    
    # VIX 数据
    vix = liquidity_data.get('vix', {})
    vix_latest = vix.get('vix_latest', '--')
    vix_hist = vix.get('hist', [])
    
    # 信用利差
    credit = liquidity_data.get('credit_spread', {})
    ig = credit.get('ig_latest', '--')
    hy = credit.get('hy_latest', '--')
    
    # 替换流动性数据显示 - 找到并替换整个buildLiquidityCharts调用
    liquidity_script = f'''
// 全球流动性图表 - 静态数据
(function() {{
    const liquidityData = {json.dumps(liquidity_data, ensure_ascii=False)};
    
    // FCI图表
    const fciCtx = document.getElementById('chart-fci');
    if (fciCtx && liquidityData.fci) {{
        const hist = liquidityData.fci.hist || [];
        const labels = hist.slice(-20).map(h => h[0]);
        const values = hist.slice(-20).map(h => h[1]);
        
        new Chart(fciCtx, {{
            type: 'line',
            data: {{
                labels: labels,
                datasets: [{{
                    label: 'NFCI',
                    data: values,
                    borderColor: '#2563eb',
                    backgroundColor: '#2563eb22',
                    fill: true,
                    tension: 0.3,
                    pointRadius: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    x: {{ display: false }},
                    y: {{ grid: {{ color: 'rgba(100,116,139,.15)' }}, ticks: {{ color: '#64748b', font: {{ size: 10 }} }} }}
                }}
            }}
        }});
    }}
    
    // VIX图表
    const vixCtx = document.getElementById('chart-vix');
    if (vixCtx && liquidityData.vix) {{
        const vixHist = liquidityData.vix.hist || [];
        new Chart(vixCtx, {{
            type: 'line',
            data: {{
                labels: vixHist.map(h => h[0]),
                datasets: [{{
                    label: 'VIX',
                    data: vixHist.map(h => h[1]),
                    borderColor: '#dc2626',
                    backgroundColor: '#dc262622',
                    fill: true,
                    tension: 0.3,
                    pointRadius: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: false }} }},
                scales: {{
                    x: {{ display: false }},
                    y: {{ grid: {{ color: 'rgba(100,116,139,.15)' }}, ticks: {{ color: '#64748b', font: {{ size: 10 }} }} }}
                }}
            }}
        }});
    }}
    
    // 信用利差
    const creditCtx = document.getElementById('chart-credit-spread');
    if (creditCtx && liquidityData.credit_spread) {{
        const hist = liquidityData.credit_spread.hist || [];
        new Chart(creditCtx, {{
            type: 'line',
            data: {{
                labels: hist.map(h => h[0]),
                datasets: [
                    {{
                        label: 'IG',
                        data: hist.map(h => h[1]),
                        borderColor: '#10b981',
                        backgroundColor: '#10b98122',
                        tension: 0.3,
                        pointRadius: 0
                    }},
                    {{
                        label: 'HY',
                        data: hist.map(h => h[2]),
                        borderColor: '#dc2626',
                        backgroundColor: '#dc262622',
                        tension: 0.3,
                        pointRadius: 0
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{ legend: {{ display: true, labels: {{ boxWidth: 12, font: {{ size: 11 }} }} }} }},
                scales: {{
                    x: {{ display: false }},
                    y: {{ grid: {{ color: 'rgba(100,116,139,.15)' }}, ticks: {{ color: '#64748b', font: {{ size: 10 }} }} }}
                }}
            }}
        }});
    }}
}})();
'''
    
    # 替换buildLiquidityCharts调用
    html = re.sub(r'buildLiquidityCharts\(\);', liquidity_script, html)
    html = re.sub(r'buildLiquidityCharts\(\);?\s*//.*?\n', liquidity_script, html)

# ========== 3. 静态化商品价格 Tab ==========
if market_data and 'commodities' in market_data:
    comm = market_data['commodities']
    
    # 构建商品卡片HTML
    cards_html = ""
    for code, info in comm.items():
        name = info.get('name', code)
        price = info.get('latest', '--')
        change = info.get('change_pct', 0)
        change_str = f"{change:+.2f}%" if isinstance(change, (int, float)) else "--"
        change_color = "#52c41a" if change and change > 0 else "#cf1322" if change and change < 0 else "#64748b"
        
        cards_html += f'''
        <div class="card" style="text-align: center;">
            <div style="font-size: 0.85rem; color: #64748b; margin-bottom: 8px;">{name}</div>
            <div style="font-size: 1.5rem; font-weight: 700; color: #1e293b;">{price}</div>
            <div style="font-size: 0.85rem; color: {change_color}; margin-top: 4px;">{change_str}</div>
        </div>'''
    
    # 替换商品卡片容器
    html = re.sub(
        r'<div class="grid-2" id="commodity-charts"[^>]*>.*?</div>',
        f'<div class="grid-4" style="margin-bottom: 20px;">{cards_html}</div>',
        html, flags=re.DOTALL
    )
    
    # 移除fetch market_data.json的代码
    html = re.sub(
        r"fetch\('market_data\.json[^']*'\)[\s\S]*?\.catch\([^)]*\)\s*\{[^}]*\}\s*\);?",
        "// market_data 已静态嵌入",
        html
    )

# ========== 4. 静态化全球金融 Tab ==========
if market_data:
    # GSCPI数据
    gscpi = market_data.get('gscpi', {})
    gscpi_latest = gscpi.get('latest', '--')
    gscpi_hist = gscpi.get('hist', [])
    
    # 金融数据卡片
    financial = market_data.get('financial', {})
    cards_html = ""
    for code, info in financial.items():
        name = info.get('name', code)
        latest = info.get('latest', '--')
        change = info.get('change_pct', 0)
        unit = info.get('unit', '')
        change_str = f"{change:+.1f}%" if isinstance(change, (int, float)) else "--"
        change_color = "#52c41a" if change and change > 0 else "#cf1322" if change and change < 0 else "#64748b"
        
        cards_html += f'''
        <div class="stat-card">
            <div class="label">{name}</div>
            <div class="value" style="color: #1e293b;">{latest}</div>
            <div class="sub" style="color: {change_color};">{unit} {change_str}</div>
        </div>'''
    
    # 替换金融卡片
    html = re.sub(
        r'<div id="financial-cards"[^>]*>.*?</div>',
        f'<div id="financial-cards" class="grid-4" style="margin-bottom:20px;">{cards_html}</div>',
        html, flags=re.DOTALL
    )

# ========== 5. 静态化战局形势 Tab ==========
if isw_data:
    title = isw_data.get('title', '无数据')
    date = isw_data.get('date', '--')
    takeaways_zh = isw_data.get('takeaways_zh', [])
    
    takeaways_html = ""
    for point in takeaways_zh[:5]:
        takeaways_html += f"<li style='margin-bottom: 8px;'>{point}</li>"
    
    # 替换战局内容
    html = re.sub(
        r'<div class="chart-title" id="war-title"[^>]*>.*?</div>',
        f'<div class="chart-title" id="war-title" style="font-size:1.15rem;">{title}</div>',
        html, flags=re.DOTALL
    )
    
    html = re.sub(
        r'<div[^>]*id="war-meta"[^>]*>.*?</div>',
        f'<div style="font-size:.8rem;color:#64748b;margin-top:6px;" id="war-meta">{date}</div>',
        html, flags=re.DOTALL
    )
    
    html = re.sub(
        r'<ol id="war-takeaways"[^>]*>.*?</ol>',
        f'<ol id="war-takeaways" style="padding-left:20px;font-size:.92rem;line-height:1.9;color:#1e293b;">{takeaways_html}</ol>',
        html, flags=re.DOTALL
    )
    
    # 移除loadISWData调用
    html = re.sub(r'loadISWData\(\);?', '// loadISWData(); // 已静态嵌入', html)

# ========== 6. 通用处理 ==========
# 更新时间
now = datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M")
html = re.sub(r'id="page-update-time"[^>]*>[^<]*</div>', f'id="page-update-time">更新: {now}</div>', html)

# 移除其他动态加载脚本
html = re.sub(r'loadStraitData\(\);?', '// loadStraitData(); // 静态页面已注入数据', html)

# 保存
with open('data-tracking-static.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: data-tracking-static.html")
print(f"更新时间: {now}")
