#!/usr/bin/env python3
"""
生成带有历史价格变化图表的 Polymarket HTML 展示页面
"""

import json
from datetime import datetime

def build_html():
    # 读取数据
    with open('iran_top10_events.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    events = data.get('events', [])
    updated_at = data.get('updatedAt', datetime.now().isoformat())
    
    # 按分类整理
    categories = {}
    for e in events:
        cat = e['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(e)
    
    # 生成分类标签和内容
    category_tabs = []
    category_contents = []
    
    cat_order = list(categories.keys())
    
    for i, cat in enumerate(cat_order):
        cat_events = categories[cat]
        is_active = 'active' if i == 0 else ''
        
        # Tab
        category_tabs.append(f'''
        <button class="tab-btn {is_active}" onclick="showCategory('{cat}')">
            {cat} ({len(cat_events)})
        </button>''')
        
        # Content
        events_html = []
        for event in cat_events:
            event_html = build_event_card(event)
            events_html.append(event_html)
        
        category_contents.append(f'''
        <div id="cat-{cat}" class="category-content {is_active}">
            {''.join(events_html)}
        </div>''')
    
    # 生成图表数据
    chart_data = generate_chart_data(events)
    
    # HTML 模板
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Polymarket 伊朗/中东预测市场 - TOP10事件</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 50%, #16213e 100%);
            min-height: 100vh;
            color: #e0e0e0;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        header {{
            text-align: center;
            padding: 40px 20px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 30px;
        }}
        
        header h1 {{
            font-size: 2.5rem;
            margin-bottom: 15px;
            background: linear-gradient(90deg, #00d4ff, #7b68ee, #ff6b6b);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }}
        
        header p {{
            color: #888;
            font-size: 1rem;
            max-width: 600px;
            margin: 0 auto;
        }}
        
        .update-time {{
            color: #666;
            font-size: 0.85rem;
            margin-top: 15px;
        }}
        
        .summary-bar {{
            background: rgba(255,255,255,0.03);
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 35px;
            display: flex;
            flex-wrap: wrap;
            gap: 30px;
            justify-content: center;
            border: 1px solid rgba(255,255,255,0.05);
        }}
        
        .summary-item {{
            text-align: center;
            padding: 0 20px;
        }}
        
        .summary-value {{
            font-size: 2.2rem;
            font-weight: bold;
            background: linear-gradient(90deg, #00d4ff, #7b68ee);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .summary-label {{
            font-size: 0.9rem;
            color: #888;
            margin-top: 5px;
        }}
        
        .tabs {{
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            margin-bottom: 30px;
            padding: 0 10px;
            justify-content: center;
        }}
        
        .tab-btn {{
            padding: 12px 24px;
            border: none;
            border-radius: 30px;
            background: rgba(255,255,255,0.05);
            color: #aaa;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 0.95rem;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        
        .tab-btn:hover {{
            background: rgba(255,255,255,0.1);
            color: #fff;
            transform: translateY(-2px);
        }}
        
        .tab-btn.active {{
            background: linear-gradient(90deg, #00d4ff, #7b68ee);
            color: #fff;
            border-color: transparent;
            box-shadow: 0 4px 15px rgba(123, 104, 238, 0.3);
        }}
        
        .category-content {{
            display: none;
        }}
        
        .category-content.active {{
            display: block;
        }}
        
        .event-card {{
            background: rgba(255,255,255,0.03);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            border: 1px solid rgba(255,255,255,0.05);
            transition: all 0.3s;
        }}
        
        .event-card:hover {{
            border-color: rgba(123, 104, 238, 0.3);
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }}
        
        .event-header {{
            display: flex;
            gap: 20px;
            margin-bottom: 25px;
        }}
        
        .event-image {{
            width: 100px;
            height: 100px;
            border-radius: 16px;
            object-fit: cover;
            background: linear-gradient(135deg, #1a1a2e, #16213e);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2.5rem;
        }}
        
        .event-info {{
            flex: 1;
        }}
        
        .event-title {{
            font-size: 1.4rem;
            font-weight: 600;
            margin-bottom: 12px;
            line-height: 1.4;
            color: #fff;
        }}
        
        .event-description {{
            font-size: 0.9rem;
            color: #888;
            line-height: 1.6;
            margin-bottom: 15px;
        }}
        
        .event-meta {{
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            font-size: 0.85rem;
        }}
        
        .event-meta span {{
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 6px 12px;
            background: rgba(255,255,255,0.05);
            border-radius: 20px;
        }}
        
        .markets-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
            gap: 20px;
        }}
        
        .market-item {{
            background: rgba(0,0,0,0.2);
            border-radius: 16px;
            padding: 20px;
            border-left: 4px solid #7b68ee;
            transition: all 0.3s;
        }}
        
        .market-item:hover {{
            background: rgba(0,0,0,0.3);
            transform: translateX(5px);
        }}
        
        .market-question {{
            font-size: 1rem;
            margin-bottom: 15px;
            line-height: 1.5;
            color: #e0e0e0;
        }}
        
        .probabilities {{
            display: flex;
            gap: 8px;
            margin-bottom: 15px;
        }}
        
        .prob-bar {{
            height: 36px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 0.9rem;
            transition: all 0.3s;
        }}
        
        .prob-yes {{
            background: linear-gradient(90deg, #22c55e, #16a34a);
            color: white;
        }}
        
        .prob-no {{
            background: linear-gradient(90deg, #ef4444, #dc2626);
            color: white;
        }}
        
        .prob-other {{
            background: linear-gradient(90deg, #6b7280, #4b5563);
            color: white;
        }}
        
        .market-stats {{
            display: flex;
            justify-content: space-between;
            font-size: 0.8rem;
            color: #888;
            margin-bottom: 15px;
        }}
        
        .market-deadline {{
            color: #fbbf24;
        }}
        
        .history-chart {{
            height: 120px;
            margin-top: 15px;
        }}
        
        .risk-high {{ border-left-color: #ef4444; }}
        .risk-medium {{ border-left-color: #f59e0b; }}
        .risk-low {{ border-left-color: #22c55e; }}
        
        .chart-container {{
            position: relative;
            height: 100px;
            margin-top: 10px;
        }}
        
        @media (max-width: 768px) {{
            .container {{ padding: 15px; }}
            header h1 {{ font-size: 1.8rem; }}
            .tabs {{ justify-content: center; }}
            .tab-btn {{ font-size: 0.85rem; padding: 10px 18px; }}
            .markets-grid {{ grid-template-columns: 1fr; }}
            .event-header {{ flex-direction: column; }}
            .event-image {{ width: 100%; height: 150px; }}
            .market-item {{ padding: 15px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔮 Polymarket 伊朗/中东预测市场</h1>
            <p>实时追踪全球资金流向的预测市场动态 · 包含概率历史变化趋势</p>
            <div class="update-time">数据来源: polymarket.com/zh/iran | 更新: {updated_at[:19].replace('T', ' ')}</div>
        </header>
        
        <div class="summary-bar">
            <div class="summary-item">
                <div class="summary-value">{len(events)}</div>
                <div class="summary-label">热门事件</div>
            </div>
            <div class="summary-item">
                <div class="summary-value">{sum(e['totalMarkets'] for e in events)}</div>
                <div class="summary-label">预测市场</div>
            </div>
            <div class="summary-item">
                <div class="summary-value">${sum(e['totalVolume'] for e in events)/1000000:.1f}M</div>
                <div class="summary-label">总交易量</div>
            </div>
            <div class="summary-item">
                <div class="summary-value">{len(categories)}</div>
                <div class="summary-label">分类</div>
            </div>
        </div>
        
        <div class="tabs">
            {''.join(category_tabs)}
        </div>
        
        <div class="categories-container">
            {''.join(category_contents)}
        </div>
    </div>
    
    <script>
        // 嵌入的市场数据
        const marketData = {json.dumps(data, ensure_ascii=False, indent=2)};
        
        // 分类切换
        function showCategory(category) {{
            document.querySelectorAll('.tab-btn').forEach(btn => {{
                btn.classList.remove('active');
                if (btn.textContent.includes(category)) {{
                    btn.classList.add('active');
                }}
            }});
            
            document.querySelectorAll('.category-content').forEach(content => {{
                content.classList.remove('active');
            }});
            document.getElementById('cat-' + category).classList.add('active');
        }}
        
        // 渲染历史图表
        function renderHistoryChart(canvasId, history) {{
            const ctx = document.getElementById(canvasId).getContext('2d');
            const labels = history.map(h => h.date.slice(5)); // MM-DD
            const data = history.map(h => h.probability);
            
            // 确定趋势颜色
            const startPrice = data[0];
            const endPrice = data[data.length - 1];
            const isRising = endPrice > startPrice;
            const color = isRising ? '#22c55e' : '#ef4444';
            
            new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: labels,
                    datasets: [{{
                        label: '概率 (%)',
                        data: data,
                        borderColor: color,
                        backgroundColor: color + '20',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4,
                        pointRadius: 3,
                        pointBackgroundColor: color,
                        pointBorderColor: '#fff',
                        pointBorderWidth: 1
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ display: false }},
                        tooltip: {{
                            mode: 'index',
                            intersect: false,
                            callbacks: {{
                                label: function(context) {{
                                    return context.parsed.y.toFixed(2) + '%';
                                }}
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{
                            display: true,
                            grid: {{ display: false }},
                            ticks: {{
                                color: '#666',
                                font: {{ size: 10 }},
                                maxTicksLimit: 5
                            }}
                        }},
                        y: {{
                            display: true,
                            min: 0,
                            max: 100,
                            grid: {{ color: 'rgba(255,255,255,0.05)' }},
                            ticks: {{
                                color: '#666',
                                font: {{ size: 10 }},
                                callback: function(value) {{
                                    return value + '%';
                                }}
                            }}
                        }}
                    }}
                }}
            }});
        }}
        
        // 页面加载完成后渲染所有图表
        document.addEventListener('DOMContentLoaded', function() {{
            marketData.events.forEach(event => {{
                event.markets.forEach((market, idx) => {{
                    if (market.history && market.history.length > 0) {{
                        const canvasId = `chart-${{event.id}}-${{idx}}`;
                        renderHistoryChart(canvasId, market.history);
                    }}
                }});
            }});
        }});
        
        // 更新时间显示
        setInterval(() => {{
            const now = new Date().toLocaleString('zh-CN');
            document.querySelector('.update-time').textContent = 
                '数据来源: polymarket.com/zh/iran | 更新: ' + now;
        }}, 60000);
    </script>
</body>
</html>'''
    
    with open('polymarket_top10.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"HTML 生成完成: polymarket_top10.html")
    print(f"包含 {len(events)} 个事件，{sum(e['totalMarkets'] for e in events)} 个市场")


def build_event_card(event):
    """生成事件卡片 HTML"""
    markets_html = []
    
    for idx, m in enumerate(event['markets'][:8]):  # 最多显示8个市场
        probs = m.get('probabilities', [])
        
        # 生成概率条
        if len(probs) >= 2:
            yes_prob = next((p['probability'] for p in probs if p['outcome'] == 'Yes'), probs[0]['probability'])
            no_prob = next((p['probability'] for p in probs if p['outcome'] == 'No'), probs[1]['probability'])
            
            # 风险级别
            if yes_prob >= 70:
                risk_class = 'risk-high'
            elif yes_prob >= 30:
                risk_class = 'risk-medium'
            else:
                risk_class = 'risk-low'
            
            prob_bars = f'''
            <div class="prob-bar prob-yes" style="width: {yes_prob}%">
                Yes {yes_prob:.1f}%
            </div>
            <div class="prob-bar prob-no" style="width: {max(20, no_prob)}%">
                No {no_prob:.1f}%
            </div>'''
        elif len(probs) == 1:
            prob = probs[0]['probability']
            prob_bars = f'''
            <div class="prob-bar prob-yes" style="width: 100%">
                {probs[0]['outcome']} {prob:.1f}%
            </div>'''
            risk_class = 'risk-medium'
        else:
            prob_bars = '<div class="prob-bar prob-other" style="width: 100%">N/A</div>'
            risk_class = 'risk-medium'
        
        # 历史图表
        has_history = m.get('history') and len(m['history']) > 0
        chart_html = f'''
        <div class="history-chart">
            <div class="chart-container">
                <canvas id="chart-{event['id']}-{idx}"></canvas>
            </div>
        </div>''' if has_history else ''
        
        markets_html.append(f'''
        <div class="market-item {risk_class}">
            <div class="market-question">{m['question']}</div>
            <div class="probabilities">
                {prob_bars}
            </div>
            <div class="market-stats">
                <span>💰 ${m.get('volumeNum', 0)/1000000:.2f}M 交易量</span>
                <span>💧 ${m.get('liquidityNum', 0)/1000000:.2f}M 流动性</span>
                <span class="market-deadline">📅 {m.get('deadline', 'N/A')}</span>
            </div>
            {chart_html}
        </div>''')
    
    # 事件图片
    image_html = f'<img src="{event.get("image", "")}" class="event-image" alt="">' if event.get('image') else '<div class="event-image">🔮</div>'
    
    return f'''
    <div class="event-card">
        <div class="event-header">
            {image_html}
            <div class="event-info">
                <div class="event-title">{event['title']}</div>
                <div class="event-description">{event.get('description', '')[:250]}...</div>
                <div class="event-meta">
                    <span>📊 {event['totalMarkets']} 个市场</span>
                    <span>💰 ${event['totalVolume']/1000000:.2f}M 总交易量</span>
                    <span>🏷️ {event['category']}</span>
                    <span>📅 截止: {event.get('endDate', 'N/A')[:10] if event.get('endDate') else 'N/A'}</span>
                </div>
            </div>
        </div>
        <div class="markets-grid">
            {''.join(markets_html)}
        </div>
    </div>'''


def generate_chart_data(events):
    """生成图表数据"""
    return {}


if __name__ == '__main__':
    build_html()
