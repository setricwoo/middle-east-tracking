#!/usr/bin/env python3
"""
生成静态数据跟踪网页 v2 - 简化版
将数据直接嵌入 HTML，只保留必要的 JavaScript
"""

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

WORKDIR = Path(__file__).parent.resolve()
BEIJING_TZ = ZoneInfo("Asia/Shanghai")


def load_json(filename):
    try:
        with open(WORKDIR / filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"加载 {filename} 失败: {e}")
        return None


def generate_html():
    # 加载数据
    strait_data = load_json("strait_data.json")
    market_data = load_json("market_data.json")
    liquidity_data = load_json("liquidity_data.json")
    isw_data = load_json("isw_data.json")
    
    now = datetime.now(BEIJING_TZ).strftime("%Y-%m-%d %H:%M")
    
    # 提取数据
    jin10 = strait_data.get('jin10', {}) if strait_data else {}
    sc = jin10.get('ship_counts', {})
    ip = jin10.get('industry_pressure', {})
    
    # 品类数据
    cat_data = []
    cat_map = [
        ('oil', '原油'), ('lng', 'LNG'), ('lpg', 'LPG'),
        ('fertilizer', '化肥'), ('aluminum', '铝材'), ('methanol', '甲醇')
    ]
    for key, name in cat_map:
        value = ip.get(key, {}).get('value', 0)
        cat_data.append((name, value))
    
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
    
    # 历史数据
    hist = strait_data.get('history', {}) if strait_data else {}
    dates = hist.get('dates', [])
    ship_counts = hist.get('ship_counts', [])
    tonnages = hist.get('tonnages', [])
    
    # 商品数据
    commodities = []
    if market_data and 'commodities' in market_data:
        for code, info in market_data['commodities'].items():
            commodities.append((
                info.get('name', code),
                info.get('latest', '--'),
                info.get('change_pct', 0)
            ))
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>【华泰固收】中东地缘跟踪 - 数据跟踪</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; background: #f8fafc; color: #334155; line-height: 1.6; }}
        .header {{ background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%); color: white; padding: 16px 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1); position: sticky; top: 0; z-index: 100; }}
        .header-content {{ max-width: 1400px; margin: 0 auto; padding: 0 20px; display: flex; justify-content: space-between; align-items: center; }}
        .header-left {{ display: flex; align-items: center; gap: 16px; }}
        .header-left h1 {{ font-size: 1.25rem; font-weight: 600; }}
        .nav {{ display: flex; gap: 8px; }}
        .nav a {{ color: rgba(255,255,255,0.8); text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 0.85rem; transition: all 0.2s; }}
        .nav a:hover, .nav a.active {{ background: rgba(255,255,255,0.15); color: white; }}
        .header-right {{ font-size: 0.8rem; color: rgba(255,255,255,0.7); }}
        
        .container {{ max-width: 1400px; margin: 0 auto; padding: 24px 20px; }}
        
        .sub-nav {{ display: flex; gap: 8px; margin-bottom: 24px; flex-wrap: wrap; }}
        .tab-btn {{ padding: 8px 20px; border: 1px solid #e2e8f0; background: white; color: #475569; border-radius: 8px; cursor: pointer; font-size: 0.9rem; transition: all 0.2s; }}
        .tab-btn:hover {{ background: #f1f5f9; color: #1e40af; }}
        .tab-btn.active {{ background: #1e40af; color: white; border-color: #1e40af; font-weight: 500; }}
        
        .tab-content {{ display: none; }}
        .tab-content.active {{ display: block; }}
        
        .card {{ background: white; border-radius: 12px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
        .grid-2 {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }}
        .grid-4 {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }}
        @media (max-width: 768px) {{ .grid-2, .grid-4 {{ grid-template-columns: 1fr; }} }}
        
        .chart-title {{ font-size: 1.1rem; font-weight: 600; color: #1e293b; margin-bottom: 12px; }}
        .chart-sub {{ font-size: 0.8rem; color: #64748b; margin-bottom: 16px; }}
        .chart-wrap {{ height: 320px; }}
    </style>
</head>
<body>
    <header class="header">
        <div class="header-content">
            <div class="header-left">
                <h1>【华泰固收】中东地缘跟踪</h1>
                <nav class="nav">
                    <a href="index.html">📊 原油图谱</a>
                    <a href="briefing.html">📰 每日简报</a>
                    <a href="news.html">🔥 实时新闻</a>
                    <a href="tracking.html">🚢 海峡跟踪</a>
                    <a href="data-tracking.html" class="active">📈 数据跟踪</a>
                </nav>
            </div>
            <div class="header-right">更新: {now}</div>
        </div>
    </header>
    
    <div class="container">
        <div class="sub-nav">
            <button class="tab-btn active" onclick="switchTab('strait', this)">🚢 海峡通行</button>
            <button class="tab-btn" onclick="switchTab('commodities', this)">📦 商品价格</button>
            <button class="tab-btn" onclick="switchTab('liquidity', this)">💧 全球流动性</button>
            <button class="tab-btn" onclick="switchTab('financial', this)">🌐 全球金融</button>
        </div>
        
        <!-- Tab 1: 海峡通行 -->
        <div id="tab-strait" class="tab-content active">
            <div class="grid-2" style="margin-bottom: 20px;">
                <div class="card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                        <div class="chart-title" style="margin: 0;">🚢 船只实时通行状态</div>
                        <span style="font-size: 0.75rem; color: #94a3b8;">更新: {jin10.get('updated', '--')[:16].replace('T', ' ')}</span>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 12px;">
                        <div style="background: linear-gradient(135deg, #fff5eb 0%, #ffe4cc 100%); border-radius: 12px; padding: 20px; text-align: center; border: 1px solid #ffd8bf;">
                            <div style="font-size: 0.85rem; color: #595959; margin-bottom: 8px;">当前通过霍尔木兹海峡</div>
                            <div style="font-size: 2.5rem; font-weight: 700; color: #fa8c16;">{sc.get('hormuz_passing', '--')}</div>
                            <div style="font-size: 0.75rem; color: #8c8c8c; margin-top: 4px;">根据媒体报道更新</div>
                        </div>
                        <div style="background: #fafafa; border-radius: 12px; padding: 20px; border: 1px solid #f0f0f0;">
                            <div style="font-size: 0.85rem; color: #595959; text-align: center; margin-bottom: 8px;">阿曼湾与波斯湾海域内</div>
                            <div style="text-align: center; margin-bottom: 12px;">
                                <span style="font-size: 1.8rem; font-weight: 700; color: #262626;">{sc.get('total_in_area', 0):,}</span>
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
                
                <div class="card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                        <div class="chart-title" style="margin: 0;">🔴 行业通行压力系数</div>
                        <span style="font-size: 0.8rem; color: #94a3b8;">来源：金十数据</span>
                    </div>
                    <div style="background: linear-gradient(135deg, #fff2f0 0%, #ffccc7 100%); border-radius: 12px; padding: 16px; text-align: center; margin-bottom: 12px; border: 1px solid #ffa39e;">
                        <div style="display: flex; align-items: center; justify-content: center; gap: 12px;">
                            <div>
                                <div style="font-size: 0.8rem; color: #595959; margin-bottom: 4px;">综合通行压力系数</div>
                                <div style="font-size: 2rem; font-weight: 800; color: #cf1322;">{total_pressure}%</div>
                            </div>
                            <div style="padding: 4px 12px; background: {risk_color}; color: white; border-radius: 12px; font-size: 0.75rem; font-weight: 500;">{risk_level}</div>
                        </div>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px;">
                        {''.join([f'<div style="text-align: center; padding: 8px; background: #fafafa; border-radius: 8px;"><div style="font-size: 0.75rem; color: #8c8c8c;">{name}</div><div style="font-size: 1.1rem; font-weight: 700; color: #262626;">{value}%</div><div style="margin-top: 4px; height: 3px; background: #f5f5f5; border-radius: 2px;"><div style="height: 100%; width: {value}%; background: linear-gradient(90deg, #ff4d4f, #cf1322); border-radius: 2px;"></div></div></div>' for name, value in cat_data])}
                    </div>
                </div>
            </div>
            
            <div class="card" style="margin-bottom: 20px;">
                <div class="chart-title">霍尔木兹海峡日通行量与承运量</div>
                <div class="chart-sub">历史数据（来自历史.csv）| 红线=冲突开始(2026-01-07)</div>
                <div class="chart-wrap"><canvas id="chart-ships"></canvas></div>
            </div>
            
            <div class="grid-2">
                <div class="card">
                    <div class="chart-title">📹 24h航运回溯</div>
                    <div style="position: relative; width: 100%; height: 400px; overflow: hidden; border-radius: 8px; background: #000;">
                        <video width="100%" height="100%" controls style="object-fit: cover;">
                            <source src="{jin10.get('video_url', '')}" type="video/mp4">
                        </video>
                    </div>
                </div>
                <div class="card">
                    <div class="chart-title">📸 实时快照</div>
                    <div style="position: relative; width: 100%; height: 400px; overflow: hidden; border-radius: 8px; background: #f8fafc;">
                        <img src="{jin10.get('snapshot_url', '')}" alt="实时快照" style="width: 100%; height: 100%; object-fit: contain;"
                             onerror="this.style.display='none'; this.parentElement.innerHTML='<div style=display:flex;align-items:center;justify-content:center;height:100%;color:#94a3b8;>暂无快照数据</div>'">
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Tab 2: 商品价格 -->
        <div id="tab-commodities" class="tab-content">
            <div class="chart-title" style="margin-bottom: 20px;">📦 大宗商品价格追踪</div>
            <div class="grid-4">
                {''.join([f'<div class="card" style="text-align: center;"><div style="font-size: 0.85rem; color: #64748b; margin-bottom: 8px;">{name}</div><div style="font-size: 1.5rem; font-weight: 700; color: #1e293b;">{price}</div><div style="font-size: 0.85rem; color: {"#52c41a" if change and change > 0 else "#cf1322" if change and change < 0 else "#64748b"}; margin-top: 4px;">{change:+.2f}%</div></div>' for name, price, change in commodities[:8]])}
            </div>
        </div>
        
        <!-- Tab 3: 全球流动性 -->
        <div id="tab-liquidity" class="tab-content">
            <div class="chart-title" style="margin-bottom: 20px;">💧 全球流动性指标</div>
            <div class="grid-2">
                <div class="card" style="text-align: center;">
                    <div style="font-size: 0.85rem; color: #64748b; margin-bottom: 8px;">金融条件指数 (FCI)</div>
                    <div style="font-size: 2.5rem; font-weight: 700; color: #1e293b;">{liquidity_data.get('fci', {}).get('latest', '--') if liquidity_data else '--'}</div>
                </div>
                <div class="card" style="text-align: center;">
                    <div style="font-size: 0.85rem; color: #64748b; margin-bottom: 8px;">VIX 波动率指数</div>
                    <div style="font-size: 2.5rem; font-weight: 700; color: #1e293b;">{liquidity_data.get('vix', {}).get('vix_latest', '--') if liquidity_data else '--'}</div>
                </div>
            </div>
        </div>
        
        <!-- Tab 4: 全球金融 -->
        <div id="tab-financial" class="tab-content">
            <div class="chart-title" style="margin-bottom: 20px;">🌐 全球金融指标</div>
            <div class="card" style="text-align: center;">
                <div style="font-size: 0.85rem; color: #64748b; margin-bottom: 8px;">全球供应链压力指数 (GSCPI)</div>
                <div style="font-size: 2.5rem; font-weight: 700; color: #1e293b;">{market_data.get('gscpi', {}).get('latest', '--') if market_data else '--'}</div>
            </div>
        </div>
    </div>
    
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
                const btn = document.querySelector('.tab-btn[onclick*="' + hash + '"]]');
                if (btn) switchTab(hash, btn);
            }}
        }})();
        
        // 海峡历史图表
        (function() {{
            const ctx = document.getElementById('chart-ships');
            if (!ctx) return;
            
            const labels = {json.dumps([d[5:] for d in dates])};
            const shipData = {json.dumps(ship_counts)};
            const tonnageData = {json.dumps([t/10000 if t else None for t in tonnages])};
            
            new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: labels,
                    datasets: [
                        {{
                            label: '日通行船次(艘)',
                            data: shipData,
                            borderColor: '#2563eb',
                            yAxisID: 'y',
                            tension: 0.3,
                            pointRadius: 0,
                            borderWidth: 2
                        }},
                        {{
                            label: '承运量(万吨)',
                            data: tonnageData,
                            borderColor: '#f59e0b',
                            yAxisID: 'y1',
                            borderDash: [5, 3],
                            tension: 0.3,
                            pointRadius: 0,
                            borderWidth: 2
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {{ intersect: false, mode: 'index' }},
                    plugins: {{ legend: {{ position: 'top' }} }},
                    scales: {{
                        y: {{ position: 'left', title: {{ display: true, text: '船次(艘)' }} }},
                        y1: {{ position: 'right', title: {{ display: true, text: '承运量(万吨)' }}, grid: {{ drawOnChartArea: false }} }}
                    }}
                }}
            }});
        }})();
    </script>
</body>
</html>
'''
    
    output_file = WORKDIR / "data-tracking-static.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"静态 HTML 已生成: {output_file}")
    return output_file


if __name__ == "__main__":
    generate_html()
