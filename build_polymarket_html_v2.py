#!/usr/bin/env python3
"""
生成 embedded standalone HTML 展示 Polymarket 伊朗事件数据
"""

import json
from datetime import datetime

def build_html():
    # 读取数据
    with open('iran_events.json', 'r', encoding='utf-8') as f:
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
    
    # 分类顺序（按重要性）
    cat_order = ['霍尔木兹海峡', '伊朗政权', '停火协议', '伊朗袭击以色列', '美军进入伊朗', '原油价格', '黎巴嫩', '其他']
    
    # 生成分类标签
    category_tabs = []
    category_contents = []
    
    for i, cat in enumerate(cat_order):
        if cat not in categories:
            continue
        
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
    
    # HTML 模板
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Polymarket 伊朗/中东预测市场</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f0f23 100%);
            min-height: 100vh;
            color: #fff;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        header {{
            text-align: center;
            padding: 30px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 30px;
        }}
        
        header h1 {{
            font-size: 2rem;
            margin-bottom: 10px;
            background: linear-gradient(90deg, #00d4ff, #7b68ee);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        header p {{
            color: #888;
            font-size: 0.9rem;
        }}
        
        .update-time {{
            color: #666;
            font-size: 0.8rem;
            margin-top: 5px;
        }}
        
        .tabs {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 25px;
            padding: 0 10px;
        }}
        
        .tab-btn {{
            padding: 10px 20px;
            border: none;
            border-radius: 25px;
            background: rgba(255,255,255,0.1);
            color: #aaa;
            cursor: pointer;
            transition: all 0.3s;
            font-size: 0.9rem;
        }}
        
        .tab-btn:hover {{
            background: rgba(255,255,255,0.2);
            color: #fff;
        }}
        
        .tab-btn.active {{
            background: linear-gradient(90deg, #00d4ff, #7b68ee);
            color: #fff;
        }}
        
        .category-content {{
            display: none;
        }}
        
        .category-content.active {{
            display: block;
        }}
        
        .event-card {{
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 20px;
            margin-bottom: 20px;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        
        .event-header {{
            display: flex;
            gap: 15px;
            margin-bottom: 15px;
        }}
        
        .event-image {{
            width: 80px;
            height: 80px;
            border-radius: 12px;
            object-fit: cover;
            background: rgba(255,255,255,0.1);
        }}
        
        .event-info {{
            flex: 1;
        }}
        
        .event-title {{
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 8px;
            line-height: 1.4;
        }}
        
        .event-meta {{
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
            font-size: 0.85rem;
            color: #888;
        }}
        
        .event-meta span {{
            display: flex;
            align-items: center;
            gap: 5px;
        }}
        
        .markets-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
        }}
        
        .market-item {{
            background: rgba(0,0,0,0.2);
            border-radius: 12px;
            padding: 15px;
            border-left: 4px solid #7b68ee;
        }}
        
        .market-question {{
            font-size: 0.95rem;
            margin-bottom: 12px;
            line-height: 1.4;
        }}
        
        .probabilities {{
            display: flex;
            gap: 10px;
            margin-bottom: 12px;
        }}
        
        .prob-bar {{
            flex: 1;
            height: 30px;
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 0.85rem;
            position: relative;
        }}
        
        .prob-yes {{
            background: linear-gradient(90deg, #22c55e, #16a34a);
        }}
        
        .prob-no {{
            background: linear-gradient(90deg, #ef4444, #dc2626);
        }}
        
        .prob-neutral {{
            background: linear-gradient(90deg, #6b7280, #4b5563);
        }}
        
        .market-stats {{
            display: flex;
            justify-content: space-between;
            font-size: 0.8rem;
            color: #666;
        }}
        
        .market-deadline {{
            color: #fbbf24;
        }}
        
        .risk-high {{ border-left-color: #ef4444; }}
        .risk-medium {{ border-left-color: #f59e0b; }}
        .risk-low {{ border-left-color: #22c55e; }}
        
        .summary-bar {{
            background: rgba(255,255,255,0.05);
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 25px;
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            justify-content: center;
        }}
        
        .summary-item {{
            text-align: center;
        }}
        
        .summary-value {{
            font-size: 1.8rem;
            font-weight: bold;
            color: #00d4ff;
        }}
        
        .summary-label {{
            font-size: 0.8rem;
            color: #888;
        }}
        
        @media (max-width: 768px) {{
            .container {{ padding: 10px; }}
            header h1 {{ font-size: 1.5rem; }}
            .tabs {{ justify-content: center; }}
            .tab-btn {{ font-size: 0.8rem; padding: 8px 15px; }}
            .markets-grid {{ grid-template-columns: 1fr; }}
            .event-header {{ flex-direction: column; }}
            .event-image {{ width: 100%; height: 120px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🔮 Polymarket 伊朗/中东预测市场</h1>
            <p>实时追踪全球资金流向的预测市场动态</p>
            <div class="update-time">更新: {updated_at[:19].replace('T', ' ')}</div>
        </header>
        
        <div class="summary-bar">
            <div class="summary-item">
                <div class="summary-value">{len(events)}</div>
                <div class="summary-label">相关事件</div>
            </div>
            <div class="summary-item">
                <div class="summary-value">{sum(e['totalMarkets'] for e in events)}</div>
                <div class="summary-label">预测市场</div>
            </div>
            <div class="summary-item">
                <div class="summary-value">${sum(e['totalVolume'] for e in events)/1000000:.1f}M</div>
                <div class="summary-label">总交易量</div>
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
        // 嵌入的数据
        const marketData = {json.dumps(data, ensure_ascii=False, indent=2)};
        
        function showCategory(category) {{
            // 更新标签样式
            document.querySelectorAll('.tab-btn').forEach(btn => {{
                btn.classList.remove('active');
                if (btn.textContent.includes(category)) {{
                    btn.classList.add('active');
                }}
            }});
            
            // 更新内容显示
            document.querySelectorAll('.category-content').forEach(content => {{
                content.classList.remove('active');
            }});
            document.getElementById('cat-' + category).classList.add('active');
        }}
        
        // 每分钟刷新一次（这里只是重新渲染，实际数据不变）
        setInterval(() => {{
            document.querySelector('.update-time').textContent = 
                '更新: ' + new Date().toLocaleString('zh-CN');
        }}, 60000);
    </script>
</body>
</html>'''
    
    with open('polymarket_events.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"HTML 生成完成: polymarket_events.html")
    print(f"包含 {len(events)} 个事件，{sum(e['totalMarkets'] for e in events)} 个市场")

def build_event_card(event):
    """生成事件卡片 HTML"""
    markets_html = []
    
    for m in event['markets'][:6]:  # 最多显示6个市场
        probs = m.get('probabilities', [])
        if len(probs) >= 2:
            yes_prob = probs[0]['probability'] if probs[0]['outcome'] == 'Yes' else probs[1]['probability']
            no_prob = probs[1]['probability'] if probs[1]['outcome'] == 'No' else probs[0]['probability']
            
            # 判断风险级别
            if yes_prob >= 80 or no_prob >= 80:
                risk_class = 'risk-high' if yes_prob >= 80 else 'risk-low'
            elif yes_prob >= 50 or no_prob >= 50:
                risk_class = 'risk-medium'
            else:
                risk_class = 'risk-low'
        else:
            yes_prob = probs[0]['probability'] if probs else 50
            no_prob = 100 - yes_prob
            risk_class = 'risk-medium'
        
        markets_html.append(f'''
        <div class="market-item {risk_class}">
            <div class="market-question">{m['question']}</div>
            <div class="probabilities">
                <div class="prob-bar prob-yes" style="width: {yes_prob}%">
                    Yes {yes_prob:.1f}%
                </div>
                <div class="prob-bar prob-no" style="width: {no_prob}%">
                    No {no_prob:.1f}%
                </div>
            </div>
            <div class="market-stats">
                <span>💰 ${m.get('volumeNum', 0)/1000000:.1f}M 交易量</span>
                <span class="market-deadline">📅 {m.get('deadline', 'N/A')}</span>
            </div>
        </div>''')
    
    image_html = f'<img src="{event.get("image", "")}" class="event-image" alt="">' if event.get('image') else '<div class="event-image" style="display:flex;align-items:center;justify-content:center;background:rgba(255,255,255,0.1)">🔮</div>'
    
    return f'''
    <div class="event-card">
        <div class="event-header">
            {image_html}
            <div class="event-info">
                <div class="event-title">{event['title']}</div>
                <div class="event-meta">
                    <span>📊 {event['totalMarkets']} 个市场</span>
                    <span>💰 ${event['totalVolume']/1000000:.1f}M 总交易量</span>
                    <span>🏷️ {event['category']}</span>
                </div>
            </div>
        </div>
        <div class="markets-grid">
            {''.join(markets_html)}
        </div>
    </div>'''

if __name__ == '__main__':
    build_html()
