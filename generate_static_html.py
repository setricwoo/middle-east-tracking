#!/usr/bin/env python3
"""
生成静态数据跟踪网页
将数据直接嵌入 HTML，不再依赖 JavaScript 动态加载
"""

import json
import csv
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

WORKDIR = Path(__file__).parent.resolve()
BEIJING_TZ = ZoneInfo("Asia/Shanghai")


def load_strait_data():
    """加载海峡通行数据"""
    try:
        with open(WORKDIR / "strait_data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"加载 strait_data.json 失败: {e}")
        return None


def load_polymarket_data():
    """加载 Polymarket 数据"""
    try:
        with open(WORKDIR / "polymarket_real_data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"加载 polymarket_real_data.json 失败: {e}")
        return {}


def load_market_data():
    """加载市场数据"""
    try:
        with open(WORKDIR / "market_data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"加载 market_data.json 失败: {e}")
        return None


def load_liquidity_data():
    """加载流动性数据"""
    try:
        with open(WORKDIR / "liquidity_data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"加载 liquidity_data.json 失败: {e}")
        return None


def load_isw_data():
    """加载 ISW 数据"""
    try:
        with open(WORKDIR / "isw_data.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"加载 isw_data.json 失败: {e}")
        return None


def generate_strait_section(data):
    """生成海峡通行 tab 的静态 HTML"""
    if not data or 'jin10' not in data:
        return "<!-- 海峡数据加载失败 -->"
    
    jin10 = data['jin10']
    sc = jin10.get('ship_counts', {})
    ip = jin10.get('industry_pressure', {})
    
    # 风险等级
    total_pressure = ip.get('total', 0)
    if total_pressure >= 95:
        risk_level, risk_color = "极高风险", "#7f1d1d"
    elif total_pressure >= 80:
        risk_level, risk_color = "高风险", "#cf1322"
    elif total_pressure >= 60:
        risk_level, risk_color = "中等风险", "#fa8c16"
    else:
        risk_level, risk_color = "低风险", "#52c41a"
    
    # 各品类数据
    categories_html = ""
    cat_map = [
        ('oil', '原油'), ('lng', 'LNG'), ('lpg', 'LPG'),
        ('fertilizer', '化肥'), ('aluminum', '铝材'), ('methanol', '甲醇')
    ]
    for key, name in cat_map:
        value = ip.get(key, {}).get('value', 0)
        display_value = f"{value}%" if value else "--%"
        bar_width = f"{value}%" if value else "0%"
        categories_html += f'''
                <div style="text-align: center; padding: 8px; background: #fafafa; border-radius: 8px;">
                    <div style="font-size: 0.75rem; color: #8c8c8c; margin-bottom: 4px;">{name}</div>
                    <div style="font-size: 1.1rem; font-weight: 700; color: #262626;">{display_value}</div>
                    <div style="margin-top: 4px; height: 3px; background: #f5f5f5; border-radius: 2px;">
                        <div style="height: 100%; width: {bar_width}; background: linear-gradient(90deg, #ff4d4f, #cf1322); border-radius: 2px; transition: width 0.5s;"></div>
                    </div>
                </div>'''
    
    # 历史图表数据
    hist = data.get('history', {})
    dates = hist.get('dates', [])
    ship_counts = hist.get('ship_counts', [])
    tonnages = hist.get('tonnages', [])
    
    # 构建图表数据
    chart_labels = [d[5:] if len(d) > 5 else d for d in dates]  # MM-DD
    chart_ships = ship_counts
    chart_tonnages = [t/10000 if t else None for t in tonnages]
    
    html = f'''
<!-- ══════════ Tab 1: 海峡通行 ══════════ -->
<div class="content">
<div id="tab-strait" class="tab-content active">

    <!-- 1. 金十数据：船只实时通行状态 + 行业通行压力系数 -->
    <div class="grid-2" style="margin-bottom: 20px; align-items: stretch;">
        <!-- 左侧：船只实时通行状态 -->
        <div class="card" style="display: flex; flex-direction: column;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <div class="chart-title" style="margin: 0;">🚢 船只实时通行状态</div>
                <span style="font-size: 0.75rem; color: #94a3b8;">更新: {jin10.get('updated', '--')[:16].replace('T', ' ')}</span>
            </div>
            
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px; flex: 1;">
                <!-- 当前通过霍尔木兹海峡 -->
                <div style="background: linear-gradient(135deg, #fff5eb 0%, #ffe4cc 100%); border-radius: 12px; padding: 20px; text-align: center; border: 1px solid #ffd8bf; display: flex; flex-direction: column; justify-content: center;">
                    <div style="font-size: 0.85rem; color: #595959; margin-bottom: 8px;">当前通过霍尔木兹海峡</div>
                    <div style="display: flex; align-items: baseline; justify-content: center; gap: 4px;">
                        <span style="font-size: 2.5rem; font-weight: 700; color: #fa8c16; line-height: 1;">{sc.get('hormuz_passing', '--')}</span>
                        <span style="font-size: 1rem; color: #595959;">艘</span>
                    </div>
                    <div style="font-size: 0.75rem; color: #8c8c8c; margin-top: 4px;">根据媒体报道更新</div>
                </div>
                
                <!-- 阿曼湾与波斯湾海域内 -->
                <div style="background: #fafafa; border-radius: 12px; padding: 20px; border: 1px solid #f0f0f0; display: flex; flex-direction: column; justify-content: center;">
                    <div style="font-size: 0.85rem; color: #595959; text-align: center; margin-bottom: 8px;">阿曼湾与波斯湾海域内</div>
                    <div style="text-align: center; margin-bottom: 12px;">
                        <span style="font-size: 1.8rem; font-weight: 700; color: #262626;">{sc.get('total_in_area', '--'):,}</span>
                        <span style="font-size: 0.9rem; color: #595959;">艘</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.75rem;">
                        <div style="text-align: center;">
                            <div style="color: #1890ff; font-weight: 600;">航行中</div>
                            <div style="color: #1890ff;">{sc.get('sailing', '--')}艘</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="color: #f5222d; font-weight: 600;">锚泊/停靠</div>
                            <div style="color: #f5222d;">{sc.get('anchored', '--')}艘</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <!-- 右侧：行业通行压力系数 -->
        <div class="card" style="display: flex; flex-direction: column;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <div class="chart-title" style="margin: 0;">🔴 行业通行压力系数</div>
                <span style="font-size: 0.8rem; color: #94a3b8;">来源：金十数据</span>
            </div>
            
            <!-- 综合压力系数 -->
            <div style="background: linear-gradient(135deg, #fff2f0 0%, #ffccc7 100%); border-radius: 12px; padding: 16px; text-align: center; margin-bottom: 12px; border: 1px solid #ffa39e;">
                <div style="display: flex; align-items: center; justify-content: center; gap: 12px;">
                    <div>
                        <div style="font-size: 0.8rem; color: #595959; margin-bottom: 4px;">综合通行压力系数</div>
                        <div style="display: flex; align-items: baseline; justify-content: center; gap: 4px;">
                            <span style="font-size: 2rem; font-weight: 800; color: #cf1322; line-height: 1;">{total_pressure}</span>
                            <span style="font-size: 1rem; color: #cf1322; font-weight: 600;">%</span>
                        </div>
                    </div>
                    <div style="padding: 4px 12px; background: {risk_color}; color: white; border-radius: 12px; font-size: 0.75rem; font-weight: 500;">{risk_level}</div>
                </div>
            </div>
            
            <!-- 分行业压力系数 -->
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; flex: 1;">
                {categories_html}
            </div>
        </div>
    </div>

    <!-- 2. 历史通行量折线图（双轴：船次 + 承运量） -->
    <div class="card" style="margin-bottom:20px;">
        <div class="chart-title">霍尔木兹海峡日通行量与承运量</div>
        <div class="chart-sub">历史数据（来自历史.csv）| 红线=冲突开始(2026-01-07)</div>
        <div class="chart-wrap" style="height:320px;"><canvas id="chart-ships"></canvas></div>
    </div>

    <!-- 3. 24h航运回溯（视频）和实时快照（图片） -->
    <div class="grid-2" style="margin-bottom:20px;">
        <div class="card">
            <div class="chart-title">📹 24h航运回溯</div>
            <div class="chart-sub">来自金十数据实时监控页面</div>
            <div style="position: relative; width: 100%; height: 400px; overflow: hidden; border-radius: 8px; background: #000;">
                <video width="100%" height="100%" controls style="object-fit: cover;">
                    <source src="{jin10.get('video_url', '')}" type="video/mp4">
                    您的浏览器不支持视频播放
                </video>
            </div>
        </div>
        <div class="card">
            <div class="chart-title">📸 实时快照</div>
            <div class="chart-sub">来自金十数据实时监控页面</div>
            <div style="position: relative; width: 100%; height: 400px; overflow: hidden; border-radius: 8px; background: #f8fafc;">
                <img src="{jin10.get('snapshot_url', '')}" alt="实时快照" style="width: 100%; height: 100%; object-fit: contain;"
                     onerror="this.style.display='none'; this.parentElement.innerHTML='<div style=\'display:flex;align-items:center;justify-content:center;height:100%;color:#94a3b8;\'>暂无快照数据</div>'">
            </div>
        </div>
    </div>

</div>
'''
    
    # 添加图表脚本
    html += f'''
<script>
// 海峡历史图表
(function() {{
    const ctx = document.getElementById('chart-ships');
    if (!ctx) return;
    
    const labels = {json.dumps(chart_labels)};
    const shipData = {json.dumps(chart_ships)};
    const tonnageData = {json.dumps(chart_tonnages)};
    
    new Chart(ctx, {{
        type: 'line',
        data: {{
            labels: labels,
            datasets: [
                {{
                    label: '日通行船次(艘)',
                    data: shipData,
                    borderColor: '#2563eb',
                    backgroundColor: '#2563eb22',
                    yAxisID: 'y',
                    tension: 0.3,
                    pointRadius: 0,
                    borderWidth: 2,
                    fill: false
                }},
                {{
                    label: '承运量(万吨)',
                    data: tonnageData,
                    borderColor: '#f59e0b',
                    backgroundColor: '#f59e0b22',
                    yAxisID: 'y1',
                    borderDash: [5, 3],
                    tension: 0.3,
                    pointRadius: 0,
                    borderWidth: 2,
                    fill: false
                }}
            ]
        }},
        options: {{
            responsive: true,
            maintainAspectRatio: false,
            interaction: {{ intersect: false, mode: 'index' }},
            plugins: {{ legend: {{ position: 'top', labels: {{ color: '#334155', font: {{ size: 11 }}, boxWidth: 12 }} }} }},
            scales: {{
                x: {{ grid: {{ color: 'rgba(100,116,139,.15)' }}, ticks: {{ color: '#64748b', maxTicksLimit: 12, font: {{ size: 10 }} }} }},
                y: {{ position: 'left', title: {{ display: true, text: '船次(艘)', color: '#2563eb', font: {{ size: 11 }} }}, grid: {{ color: 'rgba(100,116,139,.15)' }}, ticks: {{ color: '#64748b', font: {{ size: 10 }} }} }},
                y1: {{ position: 'right', title: {{ display: true, text: '承运量(万吨)', color: '#f59e0b', font: {{ size: 11 }} }}, grid: {{ drawOnChartArea: false }}, ticks: {{ color: '#f59e0b', font: {{ size: 10 }} }} }}
            }}
        }}
    }});
}})();
</script>
'''
    return html


def generate_polymarket_section(data):
    """生成 Polymarket tab 的静态 HTML"""
    # 这里简化处理，保留原有的 Polymarket 图表逻辑
    # 实际使用时需要根据数据结构生成静态图表
    return '''
<!-- ══════════ Tab 2: Polymarket预测 ══════════ -->
<div id="tab-polymarket" class="tab-content">
    <div class="pm-title">📊 Polymarket 预测市场追踪</div>
    <div class="pm-subtitle">基于 Polymarket 实时数据 | 反映市场预期与地缘政治风险溢价</div>
    
    <div id="pm-charts-container" class="grid-2" style="margin-bottom: 20px;">
        <div class="card" style="text-align: center; padding: 40px;">
            <p style="color: #94a3b8;">Polymarket 数据图表</p>
            <p style="font-size: 0.85rem; color: #64748b; margin-top: 8px;">请运行 update_polymarket_html.py 更新</p>
        </div>
    </div>
</div>
'''


def generate_commodities_section(data):
    """生成商品价格 tab 的静态 HTML"""
    if not data:
        return "<!-- 商品价格数据加载失败 -->"
    
    commodities = data.get('commodities', {})
    
    # 生成商品卡片
    cards_html = ""
    for code, info in commodities.items():
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
    
    return f'''
<!-- ══════════ Tab 3: 商品价格 ══════════ -->
<div id="tab-commodities" class="tab-content">
    <div class="chart-title" style="margin-bottom: 20px;">📦 大宗商品价格追踪</div>
    <div class="grid-4" style="margin-bottom: 20px;">
        {cards_html}
    </div>
</div>
'''


def generate_liquidity_section(data):
    """生成流动性 tab 的静态 HTML"""
    if not data:
        return "<!-- 流动性数据加载失败 -->"
    
    # FCI 数据
    fci = data.get('fci', {})
    fci_latest = fci.get('latest', '--')
    
    # VIX 数据
    vix = data.get('vix', {})
    vix_latest = vix.get('vix_latest', '--')
    
    return f'''
<!-- ══════════ Tab 4: 全球流动性 ══════════ -->
<div id="tab-liquidity" class="tab-content">
    <div class="chart-title" style="margin-bottom: 20px;">💧 全球流动性指标</div>
    
    <div class="grid-2" style="margin-bottom: 20px;">
        <div class="card">
            <div class="chart-title">金融条件指数 (FCI)</div>
            <div style="font-size: 2rem; font-weight: 700; color: #1e293b; text-align: center; padding: 20px;">
                {fci_latest}
            </div>
        </div>
        <div class="card">
            <div class="chart-title">VIX 波动率指数</div>
            <div style="font-size: 2rem; font-weight: 700; color: #1e293b; text-align: center; padding: 20px;">
                {vix_latest}
            </div>
        </div>
    </div>
</div>
'''


def generate_financial_section(data):
    """生成金融 tab 的静态 HTML"""
    if not data:
        return "<!-- 金融数据加载失败 -->"
    
    # GSCPI 数据
    gscpi = data.get('gscpi', {})
    gscpi_latest = gscpi.get('latest', '--')
    
    return f'''
<!-- ══════════ Tab 5: 全球金融 ══════════ -->
<div id="tab-financial" class="tab-content">
    <div class="chart-title" style="margin-bottom: 20px;">🌐 全球金融指标</div>
    
    <div class="card" style="margin-bottom: 20px;">
        <div class="chart-title">全球供应链压力指数 (GSCPI)</div>
        <div style="font-size: 2rem; font-weight: 700; color: #1e293b; text-align: center; padding: 20px;">
            {gscpi_latest}
        </div>
    </div>
</div>
'''


def generate_war_section(data):
    """生成战局形势 tab 的静态 HTML"""
    if not data:
        return "<!-- 战局数据加载失败 -->"
    
    title = data.get('title', '无数据')
    date = data.get('date', '--')
    takeaways_zh = data.get('takeaways_zh', [])
    
    takeaways_html = ""
    for point in takeaways_zh[:5]:  # 最多显示5条
        takeaways_html += f"<li style='margin-bottom: 8px;'>{point}</li>"
    
    return f'''
<!-- ══════════ Tab 6: 战局形势 ══════════ -->
<div id="tab-war" class="tab-content">
    <div class="card" style="margin-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 16px;">
            <div>
                <span style="padding: 4px 12px; background: #dc2626; color: white; border-radius: 4px; font-size: 0.75rem;">ISW 最新战况</span>
                <div class="chart-title" style="margin-top: 8px;">{title}</div>
                <div style="font-size: 0.8rem; color: #64748b; margin-top: 4px;">{date}</div>
            </div>
        </div>
        
        <div style="margin-top: 20px;">
            <div style="font-size: 0.85rem; font-weight: 700; color: #475569; margin-bottom: 10px;">KEY TAKEAWAYS</div>
            <ol style="padding-left: 20px; font-size: 0.92rem; line-height: 1.8; color: #1e293b;">
                {takeaways_html}
            </ol>
        </div>
    </div>
</div>
'''


def generate_full_html():
    """生成完整的静态 HTML"""
    
    # 加载所有数据
    strait_data = load_strait_data()
    polymarket_data = load_polymarket_data()
    market_data = load_market_data()
    liquidity_data = load_liquidity_data()
    isw_data = load_isw_data()
    
    now = datetime.now(BEIJING_TZ).strftime("%Y-%m-%d %H:%M")
    
    # 生成各 tab 内容
    strait_section = generate_strait_section(strait_data)
    polymarket_section = generate_polymarket_section(polymarket_data)
    commodities_section = generate_commodities_section(market_data)
    liquidity_section = generate_liquidity_section(liquidity_data)
    financial_section = generate_financial_section(market_data)
    war_section = generate_war_section(isw_data)
    
    # 读取原始 HTML 的 head 和导航部分
    try:
        with open(WORKDIR / "data-tracking.html", "r", encoding="utf-8") as f:
            original = f.read()
    except Exception as e:
        print(f"读取原始 HTML 失败: {e}")
        return
    
    # 提取 head 部分（到 </head>）
    head_match = original.find('</head>')
    head = original[:head_match + 7] if head_match > 0 else "<head><title>数据跟踪</title></head>"
    
    # 提取导航部分
    nav_start = original.find('<body>')
    nav_end = original.find('<!-- ══════════ Tab 1:')
    nav = original[nav_start:nav_end] if nav_start > 0 and nav_end > 0 else "<body>"
    
    # 组合新的 HTML
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
{head}
{nav}
{strait_section}
{polymarket_section}
{commodities_section}
{liquidity_section}
{financial_section}
{war_section}

</div><!-- /content -->

<script>
// Tab 切换
function switchTab(name, btnElement) {{
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
    document.getElementById('tab-' + name).classList.add('active');
    if (btnElement) btnElement.classList.add('active');
    history.replaceState(null, '', '#' + name);
}}

// 从 hash 恢复 tab
(function() {{
    const hash = location.hash.replace('#', '');
    if (hash) {{
        const btn = document.querySelector(`.tab-btn[onclick*="${{hash}}"]`);
        if (btn) switchTab(hash, btn);
    }}
}})();
</script>
</body>
</html>
'''
    
    # 保存静态 HTML
    output_file = WORKDIR / "data-tracking-static.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"静态 HTML 已生成: {output_file}")
    print(f"生成时间: {now}")
    
    return output_file


if __name__ == "__main__":
    generate_full_html()
