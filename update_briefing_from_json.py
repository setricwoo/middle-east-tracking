#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新版简报更新脚本 - 从 briefing_data.json 读取数据生成HTML
"""

import json
import os

def generate_html(data):
    """根据数据生成HTML"""
    
    # 生成战局进展HTML
    war_html = "\n".join([
        f'''<div class="highlight-box military">
            <h5>{item['title']}</h5>
            <p><strong>时间：</strong>{item['time']} | <strong>来源：</strong>{item['source']}</p>
            <p>{item['content']}</p>
        </div>''' for item in data.get('war_progress', [])
    ])
    
    # 生成各方表态HTML
    statements_html = "\n".join([
        f'''<div class="highlight-box statements">
            <h5>{item['country']}</h5>
            <p><strong>时间：</strong>{item['time']} | <strong>来源：</strong>{item['source']}</p>
            <p>{item['content']}</p>
        </div>''' for item in data.get('statements', [])
    ])
    
    # 生成海峡通行情况HTML
    strait_status = data.get('strait_status', {})
    strait_events = "\n".join([f"<li>{event}</li>" for event in strait_status.get('key_events', [])])
    
    strait_html = f'''<div class="highlight-box warning">
        <h5>海峡通行状态</h5>
        <p><strong>当前状态：</strong>{strait_status.get('status', '-')} | <strong>封锁天数：</strong>第{strait_status.get('blockade_day', '-')}天</p>
        <p><strong>通行数据：</strong>{strait_status.get('daily_transit', '-')}</p>
        <p><strong>关键事件：</strong></p>
        <ul>{strait_events}</ul>
        <p><strong>影响评估：</strong>{strait_status.get('impact', '-')}</p>
    </div>'''
    
    # 生成供应链HTML
    supply_html = "\n".join([
        f'''<div class="highlight-box">
            <h5>{item['sector']}</h5>
            <p><strong>事件：</strong>{item['event']}</p>
            <p><strong>影响：</strong>{item['impact']}</p>
        </div>''' for item in data.get('supply_chain', [])
    ])
    
    # 生成投行讨论HTML
    bank_html = "\n".join([
        f'''<div class="highlight-box">
            <h5>{item['bank']}</h5>
            {f"<p><strong>发言人：</strong>{item['speaker']}</p>" if 'speaker' in item else ""}
            <p>{item['view']}</p>
            <p style="font-size:0.8rem;color:#64748b;">来源：{item['source']}</p>
        </div>''' for item in data.get('investment_banks', [])
    ])
    
    # 生成市场数据HTML
    market = data.get('market_data', {})
    market_html = f'''<div class="market-grid">
        <div class="market-card"><h5>布伦特原油</h5><p>{market.get('brent', '-')}</p></div>
        <div class="market-card"><h5>WTI原油</h5><p>{market.get('wti', '-')}</p></div>
        <div class="market-card"><h5>标普500</h5><p>{market.get('sp500', '-')}</p></div>
        <div class="market-card"><h5>纳斯达克</h5><p>{market.get('nasdaq', '-')}</p></div>
        <div class="market-card"><h5>VIX波动率</h5><p>{market.get('vix', '-')}</p></div>
        <div class="market-card"><h5>美元指数</h5><p>{market.get('dxy', '-')}</p></div>
    </div>'''
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>【华泰固收】中东地缘跟踪 - 美以伊冲突每日简报</title>
    <style>
        *{{margin:0;padding:0;box-sizing:border-box;}}
        body{{font-family:'Segoe UI',system-ui,-apple-system,sans-serif;background:#f8fafc;color:#1e293b;line-height:1.8;}}
        .header {{
            background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
            color: white;
            padding: 12px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        .header-main {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
        }}
        .header-left {{
            position: absolute;
            left: 20px;
        }}
        .header-left h1 {{
            font-size: 1.1rem;
            font-weight: 600;
            margin: 0;
        }}
        .header-center {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            justify-content: center;
        }}
        .nav-btn {{
            color: rgba(255,255,255,0.85);
            text-decoration: none;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 0.85rem;
            transition: all 0.2s;
            white-space: nowrap;
        }}
        .nav-btn:hover {{
            background: rgba(255,255,255,0.15);
            color: white;
        }}
        .nav-btn.active {{
            background: rgba(255,255,255,0.2);
            color: white;
            font-weight: 500;
        }}
        .container{{max-width:900px;margin:0 auto;padding:24px 20px;}}
        .briefing-header{{background:linear-gradient(135deg,#fef3c7 0%,#fde68a 100%);border:1px solid #f59e0b;border-radius:12px;padding:24px;margin-bottom:24px;}}
        .briefing-header h2{{color:#92400e;font-size:1.4rem;margin-bottom:12px;}}
        .briefing-header .summary{{color:#78350f;font-size:0.95rem;line-height:1.8;}}
        .section{{background:#fff;border-radius:12px;padding:24px;margin-bottom:20px;box-shadow:0 1px 3px rgba(0,0,0,0.08);border:1px solid #e2e8f0;}}
        .section h3{{color:#1e40af;font-size:1.15rem;margin-bottom:16px;padding-bottom:10px;border-bottom:2px solid #e2e8f0;}}
        .section h4{{color:#334155;font-size:1rem;margin:20px 0 12px 0;}}
        .section p{{color:#475569;font-size:0.95rem;margin-bottom:12px;text-align:justify;}}
        .section ul{{padding-left:20px;margin-bottom:12px;}}
        .section li{{color:#475569;font-size:0.95rem;margin-bottom:8px;}}
        .highlight-box{{background:#eff6ff;border-left:4px solid #3b82f6;padding:16px;border-radius:0 8px 8px 0;margin:16px 0;}}
        .highlight-box.critical{{background:#fef2f2;border-left-color:#dc2626;}}
        .highlight-box.warning{{background:#fffbeb;border-left-color:#f59e0b;}}
        .highlight-box.statements{{background:#f0fdf4;border-left-color:#16a34a;}}
        .highlight-box h5{{color:#1e40af;font-size:0.95rem;margin-bottom:10px;}}
        .highlight-box.critical h5{{color:#dc2626;}}
        .highlight-box.warning h5{{color:#b45309;}}
        .highlight-box.statements h5{{color:#166534;}}
        .market-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:16px 0;}}
        .market-card{{background:#f8fafc;border-radius:8px;padding:16px;border:1px solid #e2e8f0;}}
        .market-card h5{{color:#1e40af;font-size:0.9rem;margin-bottom:8px;}}
        .market-card p{{color:#475569;font-size:0.85rem;margin:0;}}
        .footer{{text-align:center;padding:24px;color:#64748b;font-size:0.8rem;border-top:1px solid #e2e8f0;margin-top:40px;}}
        @media (max-width: 768px) {{
            .market-grid{{grid-template-columns:repeat(2,1fr);}}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-main">
            <div class="header-left">
                <h1>【华泰固收】中东地缘跟踪</h1>
            </div>
            <div class="header-center">
                <a href="index.html" class="nav-btn">海峡跟踪</a>
                <a href="polymarket.html" class="nav-btn">Polymarket</a>
                <a href="data-tracking.html" class="nav-btn">全球市场</a>
                <a href="war-situation.html" class="nav-btn">战局形势</a>
                <a href="news.html" class="nav-btn">实时新闻</a>
                <a href="briefing.html" class="nav-btn active">每日简报</a>
                <a href="oil-chart.html" class="nav-btn">原油图谱</a>
            </div>
        </div>
    </div>

    <div class="container">
        <div class="briefing-header">
            <h2>每日简报 ({data['date']})</h2>
            <p class="summary">{data.get('summary', '')}</p>
        </div>

        <!-- 1. 战局进展 -->
        <div class="section">
            <h3>战局进展</h3>
            {war_html}
        </div>

        <!-- 2. 各方表态 -->
        <div class="section">
            <h3>各方最新表态</h3>
            {statements_html}
        </div>

        <!-- 3. 海峡通行情况 -->
        <div class="section">
            <h3>霍尔木兹海峡通行情况</h3>
            {strait_html}
        </div>

        <!-- 4. 全球供应链 -->
        <div class="section">
            <h3>全球供应链影响</h3>
            {supply_html}
        </div>

        <!-- 5. 海外投行讨论 -->
        <div class="section">
            <h3>海外投行观点</h3>
            {bank_html}
        </div>

        <!-- 市场数据 -->
        <div class="section">
            <h3>市场数据速览</h3>
            {market_html}
            <p style="font-size:0.8rem;color:#64748b;margin-top:12px;">
                数据截止时间：{data['date']} 12:00 UTC+8
            </p>
        </div>

        <div class="footer">数据来源：路透社、彭博社、半岛电视台、CNN、华尔街日报等 | 仅供参考，不构成投资建议</div>
    </div>
</body>
</html>'''
    
    return html

def main():
    # 读取数据文件
    data_file = r'D:\python_code\海湾以来-最新\briefing_data.json'
    
    if not os.path.exists(data_file):
        print(f"错误：数据文件不存在: {data_file}")
        print("请按照 BRIEFING_UPDATE_PROMPT.md 的指引，先创建 briefing_data.json 文件")
        return
    
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 生成HTML
    html_content = generate_html(data)
    
    # 保存文件
    output_file = r'D:\python_code\海湾以来-最新\briefing.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("简报更新完成！")
    print(f"日期: {data['date']}")
    print(f"冲突第{data['conflict_day']}天")
    print(f"封锁第{data['blockade_day']}天")
    print(f"\n内容板块:")
    print(f"  - 战局进展: {len(data.get('war_progress', []))}条")
    print(f"  - 各方表态: {len(data.get('statements', []))}条")
    print(f"  - 海峡通行: {len(data.get('strait_status', {}).get('key_events', []))}个关键事件")
    print(f"  - 供应链: {len(data.get('supply_chain', []))}个行业")
    print(f"  - 投行观点: {len(data.get('investment_banks', []))}家机构")

if __name__ == "__main__":
    main()
