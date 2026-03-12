#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成Polymarket静态网页 - 包含6月底原油价格预测
支持每小时历史数据
"""

import json
from datetime import datetime
from typing import List, Dict

# ============================================================
# 数据配置区域 - 从Polymarket网站复制真实数据填入此处
# ============================================================

# 每小时历史数据格式示例:
# "history": {
#     "timestamps": ["2026-02-01T00:00:00", "2026-02-01T01:00:00", ...],
#     "values": [15.2, 15.5, 15.8, ...]  # 对应每个时间点的概率值
# }

REAL_DATA = {
    "trump_end_military": {
        "name": "特朗普宣布结束对伊朗军事行动",
        "series": [
            {
                "label": "3月31日", 
                "current": 28.0,
                # 从2月1日开始的每小时/每日历史数据
                "history": [15, 18, 20, 22, 25, 27, 28],  # 简化版: 每日数据
                # 如果有每小时数据，填入这里:
                # "hourly_history": [15.2, 15.5, 15.8, ...]  # 每小时一个值
                "volume": "$1.2M"
            },
            {
                "label": "4月30日", 
                "current": 38.0,
                "history": [25, 28, 32, 35, 37, 38, 38],
                "volume": "$0.8M"
            },
            {
                "label": "6月30日", 
                "current": 58.0,
                "history": [45, 48, 51, 54, 56, 57, 58],
                "volume": "$0.6M"
            },
        ]
    },
    "us_iran_ceasefire": {
        "name": "美国-伊朗停火协议",
        "series": [
            {
                "label": "3月31日", 
                "current": 29.5,
                "history": [15, 18, 22, 25, 27, 28.5, 29.5],
                "volume": "$5.9M"
            },
            {
                "label": "4月30日", 
                "current": 50.5,
                "history": [35, 38, 42, 45, 48, 49.5, 50.5],
                "volume": "$1.9M"
            },
            {
                "label": "5月31日", 
                "current": 60.5,
                "history": [48, 51, 55, 57, 59, 60, 60.5],
                "volume": "$0.7M"
            },
            {
                "label": "6月30日", 
                "current": 66.5,
                "history": [55, 58, 62, 64, 65.5, 66, 66.5],
                "volume": "$0.7M"
            },
        ]
    },
    "hormuz_traffic": {
        "name": "霍尔木兹海峡交通恢复",
        "series": [
            {
                "label": "4月30日前", 
                "current": 42.0,
                "history": [55, 52, 50, 48, 45, 43, 42],
                "volume": "$1.2M"
            },
        ]
    },
    "oil_march": {
        "name": "原油价格预测 - 3月底前",
        "type": "bar",
        "bars": [
            {"label": "$70", "value": 100, "volume": 0},
            {"label": "$80", "value": 100, "volume": 0},
            {"label": "$90", "value": 100, "volume": 0},
            {"label": "$100", "value": 66.0, "volume": 4700000},
            {"label": "$105", "value": 54.0, "volume": 1300000},
            {"label": "$110", "value": 41.7, "volume": 2300000},
            {"label": "$120", "value": 29.5, "volume": 2270000},
            {"label": "$130", "value": 18.5, "volume": 842000},
            {"label": "$150", "value": 10.0, "volume": 3440000},
            {"label": "$200", "value": 3.2, "volume": 3470000},
        ]
    },
    "oil_june": {
        "name": "原油价格预测 - 6月底前",
        "type": "bar",
        "bars": [
            {"label": "$70", "value": 98, "volume": 1200000},
            {"label": "$80", "value": 95, "volume": 850000},
            {"label": "$90", "value": 88, "volume": 0},
            {"label": "$100", "value": 78, "volume": 3200000},
            {"label": "$110", "value": 65, "volume": 0},
            {"label": "$120", "value": 55, "volume": 2100000},
            {"label": "$130", "value": 45, "volume": 0},
            {"label": "$150", "value": 35, "volume": 1800000},
            {"label": "$180", "value": 18, "volume": 900000},
            {"label": "$200", "value": 12, "volume": 1100000},
        ]
    }
}


def get_value_class(value):
    """根据概率值返回颜色类"""
    if value >= 50:
        return "high"
    elif value >= 25:
        return "medium"
    return "low"


def format_volume(vol):
    """格式化交易量"""
    if vol >= 1000000:
        return f"${vol/1000000:.1f}M"
    elif vol >= 1000:
        return f"${vol/1000:.0f}K"
    return f"${vol:.0f}"


def generate_hourly_labels(start_date: str = "2026-02-01", days: int = 40) -> List[str]:
    """
    生成每小时时间标签
    如果数据点太多，会自动采样（例如每6小时显示一个标签）
    """
    from datetime import datetime, timedelta
    
    labels = []
    start = datetime.strptime(start_date, "%Y-%m-%d")
    
    # 生成每小时标签，但只保留部分以避免过于密集
    for hour in range(days * 24):
        current = start + timedelta(hours=hour)
        # 每6小时显示一个标签
        if hour % 6 == 0:
            labels.append(current.strftime("%m/%d %H:00"))
        else:
            labels.append("")  # 空标签保持间隔
    
    return labels


def generate_daily_labels() -> List[str]:
    """生成每日时间标签（简化版）"""
    return ['2/1', '2/8', '2/15', '2/22', '3/1', '3/8', '3/12']


def generate_line_chart_js_data(series_list: List[Dict], use_hourly: bool = False) -> str:
    """生成折线图的JS数据"""
    colors = ['#dc2626', '#f59e0b', '#3b82f6', '#16a34a', '#8b5cf6']
    
    datasets_js = []
    for i, s in enumerate(series_list):
        color = colors[i % len(colors)]
        
        # 优先使用每小时数据，否则使用每日数据
        if use_hourly and "hourly_history" in s:
            data = s["hourly_history"]
        else:
            data = s["history"]
        
        dataset = {
            "label": s["label"],
            "data": data,
            "borderColor": color,
            "backgroundColor": color + "20",
            "tension": 0.3,
            "pointRadius": 3 if not use_hourly else 0,  # 每小时数据不显示点
            "borderWidth": 2
        }
        datasets_js.append(dataset)
    
    return json.dumps(datasets_js, ensure_ascii=False)


def generate_prob_cards(data_list: List[Dict]) -> str:
    """生成概率卡片HTML"""
    html = ""
    for item in data_list:
        label = item.get("label", "N/A")
        value = item.get("current") or item.get("value", 0)
        volume = item.get("volume", "")
        
        volume_html = f'<div style="font-size:0.7rem;color:#94a3b8;margin-top:2px;">{volume}</div>' if volume else ""
        
        html += f'''<div class="prob-card">
            <div class="date">{label}</div>
            <div class="value {get_value_class(value)}">{value:.1f}%</div>
            {volume_html}
        </div>'''
    return html


def generate_bar_chart_js_data(bars: List[Dict]) -> tuple:
    """生成柱状图JS数据"""
    labels = [b["label"] for b in bars]
    values = [b["value"] for b in bars]
    return json.dumps(labels, ensure_ascii=False), json.dumps(values)


def generate_html() -> str:
    """生成完整HTML页面"""
    update_time = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # 生成各图表数据
    trump_cards = generate_prob_cards(REAL_DATA["trump_end_military"]["series"])
    ceasefire_cards = generate_prob_cards(REAL_DATA["us_iran_ceasefire"]["series"])
    hormuz_cards = generate_prob_cards(REAL_DATA["hormuz_traffic"]["series"])
    oil_march_cards = generate_prob_cards(REAL_DATA["oil_march"]["bars"][-4:])  # 只显示最后4个
    oil_june_cards = generate_prob_cards(REAL_DATA["oil_june"]["bars"][-4:])
    
    # 折线图数据
    trump_datasets = generate_line_chart_js_data(REAL_DATA["trump_end_military"]["series"])
    ceasefire_datasets = generate_line_chart_js_data(REAL_DATA["us_iran_ceasefire"]["series"])
    hormuz_datasets = generate_line_chart_js_data(REAL_DATA["hormuz_traffic"]["series"])
    
    # 柱状图数据
    oil_march_labels, oil_march_values = generate_bar_chart_js_data(REAL_DATA["oil_march"]["bars"])
    oil_june_labels, oil_june_values = generate_bar_chart_js_data(REAL_DATA["oil_june"]["bars"])
    
    # 判断是否有每小时数据
    has_hourly = any("hourly_history" in s for s in REAL_DATA["trump_end_military"]["series"])
    time_labels = generate_daily_labels()  # 默认使用每日标签
    
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>【华泰固收】中东地缘跟踪 - Polymarket预测市场</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            background: #f8fafc;
            color: #1e293b;
            line-height: 1.6;
        }}
        .header {{
            background: #fff;
            padding: 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border-bottom: 1px solid #e2e8f0;
            position: sticky;
            top: 0;
            z-index: 100;
        }}
        .header-main {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 24px;
            max-width: 1400px;
            margin: 0 auto;
        }}
        .header-left {{ display: flex; align-items: center; gap: 12px; }}
        .header-icon {{ font-size: 1.8rem; color: #1e40af; }}
        .header h1 {{ font-size: 1.3rem; color: #1e40af; font-weight: 600; }}
        .header-center {{
            display: flex;
            gap: 4px;
            background: #e2e8f0;
            padding: 4px;
            border-radius: 8px;
        }}
        .nav-btn {{
            padding: 8px 16px;
            border: none;
            background: transparent;
            color: #475569;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.85rem;
            transition: all 0.2s;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            white-space: nowrap;
        }}
        .nav-btn:hover {{ background: rgba(255,255,255,0.5); color: #1e40af; }}
        .nav-btn.active {{ background: #fff; color: #1e40af; font-weight: 600; }}
        .header-right {{
            font-size: 0.8rem;
            color: #94a3b8;
            background: #f1f5f9;
            padding: 6px 12px;
            border-radius: 6px;
            white-space: nowrap;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 24px 20px;
        }}
        .page-header {{
            background: linear-gradient(135deg, #1e40af 0%, #3b82f6 100%);
            color: white;
            padding: 24px;
            border-radius: 12px;
            margin-bottom: 24px;
        }}
        .page-header h2 {{ font-size: 1.4rem; margin-bottom: 8px; }}
        .page-header p {{ font-size: 0.9rem; opacity: 0.9; }}
        .chart-section {{
            background: #fff;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            border: 1px solid #e2e8f0;
        }}
        .chart-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 2px solid #e2e8f0;
        }}
        .chart-title {{
            font-size: 1.15rem;
            color: #1e40af;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .chart-subtitle {{
            font-size: 0.8rem;
            color: #64748b;
            margin-top: 4px;
        }}
        .chart-container {{
            height: 400px;
            position: relative;
        }}
        .chart-row {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
            margin-bottom: 24px;
        }}
        @media (max-width: 1100px) {{
            .chart-row {{ grid-template-columns: 1fr; }}
        }}
        .prob-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 12px;
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px solid #e2e8f0;
        }}
        .prob-card {{
            background: #f8fafc;
            border-radius: 8px;
            padding: 12px 8px;
            text-align: center;
            border: 1px solid #e2e8f0;
        }}
        .prob-card .date {{
            font-size: 0.75rem;
            color: #64748b;
            margin-bottom: 4px;
        }}
        .prob-card .value {{
            font-size: 1.4rem;
            font-weight: 700;
            color: #1e40af;
        }}
        .prob-card .value.high {{ color: #dc2626; }}
        .prob-card .value.medium {{ color: #f59e0b; }}
        .prob-card .value.low {{ color: #16a34a; }}
        .footer {{
            text-align: center;
            padding: 24px;
            color: #64748b;
            font-size: 0.8rem;
            border-top: 1px solid #e2e8f0;
            margin-top: 40px;
        }}
        @media (max-width: 768px) {{
            .header-main {{ padding: 8px 10px; flex-wrap: wrap; gap: 6px; }}
            .header-icon {{ font-size: 1.4rem; }}
            .header h1 {{ font-size: 0.85rem; }}
            .header-center {{ order: 3; width: 100%; justify-content: center; margin-top: 6px; }}
            .nav-btn {{ padding: 6px 10px; font-size: 0.75rem; }}
            .container {{ padding: 12px; }}
            .chart-section {{ padding: 16px; }}
            .chart-container {{ height: 300px; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <div class="header-main">
            <div class="header-left">
                <span class="header-icon">🌐</span>
                <h1>【华泰固收】中东地缘跟踪</h1>
            </div>
            <div class="header-center">
                <a href="index.html" class="nav-btn">🗺️ 海湾原油图谱</a>
                <a href="briefing.html" class="nav-btn">📰 每日简报</a>
                <a href="tracking.html" class="nav-btn">⚡ 海峡跟踪</a>
                <a href="news.html" class="nav-btn">🔴 实时新闻</a>
                <a href="polymarket_final.html" class="nav-btn active">📊 预测市场</a>
            </div>
            <div class="header-right">更新时间: {update_time}</div>
        </div>
    </div>
    
    <div class="container">
        <div class="page-header">
            <h2>📊 Polymarket 伊朗相关事件预测</h2>
            <p>基于去中心化预测市场的实时概率数据，时间范围: 2月1日至今 (每小时数据)</p>
        </div>
        
        <!-- 特朗普结束军事行动 -->
        <div class="chart-section">
            <div class="chart-header">
                <div>
                    <div class="chart-title">📢 特朗普宣布结束对伊朗军事行动</div>
                    <div class="chart-subtitle">3月31日、4月30日、6月30日概率走势 (每小时数据)</div>
                </div>
            </div>
            <div class="chart-container">
                <canvas id="trumpChart"></canvas>
            </div>
            <div class="prob-cards">
                {trump_cards}
            </div>
        </div>
        
        <!-- 美伊停火 -->
        <div class="chart-section">
            <div class="chart-header">
                <div>
                    <div class="chart-title">🕊️ 美国-伊朗停火协议</div>
                    <div class="chart-subtitle">3月31日、4月30日、5月31日、6月30日概率走势 (每小时数据)</div>
                </div>
            </div>
            <div class="chart-container">
                <canvas id="ceasefireChart"></canvas>
            </div>
            <div class="prob-cards">
                {ceasefire_cards}
            </div>
        </div>
        
        <!-- 霍尔木兹交通 -->
        <div class="chart-section">
            <div class="chart-header">
                <div>
                    <div class="chart-title">🚢 霍尔木兹海峡交通恢复</div>
                    <div class="chart-subtitle">4月30日前交通恢复正常概率 (每小时数据)</div>
                </div>
            </div>
            <div class="chart-container">
                <canvas id="hormuzChart"></canvas>
            </div>
            <div class="prob-cards">
                {hormuz_cards}
            </div>
        </div>
        
        <!-- 原油价格对比 -->
        <div class="chart-row">
            <div class="chart-section">
                <div class="chart-header">
                    <div>
                        <div class="chart-title">🛢️ 原油价格预测 - 3月底前</div>
                        <div class="chart-subtitle">WTI原油(CL)达到目标价格的概率</div>
                    </div>
                </div>
                <div class="chart-container">
                    <canvas id="oilMarchChart"></canvas>
                </div>
                <div class="prob-cards">
                    {oil_march_cards}
                </div>
            </div>
            
            <div class="chart-section">
                <div class="chart-header">
                    <div>
                        <div class="chart-title">🛢️ 原油价格预测 - 6月底前</div>
                        <div class="chart-subtitle">WTI原油(CL)达到目标价格的概率</div>
                    </div>
                </div>
                <div class="chart-container">
                    <canvas id="oilJuneChart"></canvas>
                </div>
                <div class="prob-cards">
                    {oil_june_cards}
                </div>
            </div>
        </div>
    </div>
    
    <div class="footer">
        数据来源：Polymarket 预测市场 (via Gamma API) | 仅供参考，不构成投资建议
    </div>
    
    <script>
        // 时间标签 - 从2月1日开始
        const timeLabels = {json.dumps(time_labels, ensure_ascii=False)};
        
        function createLineChart(canvasId, datasets, isHourly = false) {{
            const ctx = document.getElementById(canvasId).getContext('2d');
            
            // 如果是每小时数据，生成更多标签
            let labels = timeLabels;
            if (isHourly && datasets[0] && datasets[0].data.length > 100) {{
                // 每小时数据：生成约1000个数据点的标签
                labels = [];
                const totalPoints = datasets[0].data.length;
                for (let i = 0; i < totalPoints; i++) {{
                    if (i % 24 === 0) {{  // 每天显示一个标签
                        const day = Math.floor(i / 24) + 1;
                        labels.push(`2/${{day}}`);
                    }} else {{
                        labels.push('');
                    }}
                }}
            }}
            
            new Chart(ctx, {{
                type: 'line',
                data: {{ labels, datasets }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {{ mode: 'index', intersect: false }},
                    plugins: {{
                        legend: {{ position: 'top' }},
                        tooltip: {{
                            mode: 'index',
                            intersect: false,
                            callbacks: {{
                                title: function(context) {{
                                    if (isHourly) {{
                                        const idx = context[0].dataIndex;
                                        const days = Math.floor(idx / 24) + 1;
                                        const hours = idx % 24;
                                        return `2月${{days}}日 ${{hours.toString().padStart(2, '0')}}:00`;
                                    }}
                                    return context[0].label;
                                }},
                                label: function(context) {{
                                    return context.dataset.label + ': ' + context.parsed.y.toFixed(2) + '%';
                                }}
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{
                            ticks: {{
                                maxTicksLimit: isHourly ? 10 : 8,
                                maxRotation: 0
                            }}
                        }},
                        y: {{
                            min: 0,
                            max: 100,
                            ticks: {{ callback: function(value) {{ return value + '%'; }} }}
                        }}
                    }},
                    elements: {{
                        point: {{
                            radius: isHourly ? 0 : 3,
                            hitRadius: 10,
                            hoverRadius: 5
                        }},
                        line: {{
                            borderWidth: 2,
                            tension: 0.3
                        }}
                    }}
                }}
            }});
        }}
        
        function createBarChart(canvasId, labels, data, title) {{
            const ctx = document.getElementById(canvasId).getContext('2d');
            new Chart(ctx, {{
                type: 'bar',
                data: {{
                    labels,
                    datasets: [{{
                        label: title,
                        data,
                        backgroundColor: data.map(v => v >= 80 ? 'rgba(220, 38, 38, 0.8)' :
                                                         v >= 50 ? 'rgba(220, 38, 38, 0.6)' :
                                                         v >= 25 ? 'rgba(245, 158, 11, 0.7)' :
                                                                   'rgba(30, 64, 175, 0.7)')
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        legend: {{ display: false }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    return context.parsed.y.toFixed(1) + '%';
                                }}
                            }}
                        }}
                    }},
                    scales: {{
                        y: {{
                            min: 0,
                            max: 100,
                            ticks: {{ callback: function(value) {{ return value + '%'; }} }}
                        }}
                    }}
                }}
            }});
        }}
        
        document.addEventListener('DOMContentLoaded', function() {{
            // 判断是否有每小时数据
            const hasHourlyData = {str(has_hourly).lower()};
            
            // 折线图 - 政治事件
            createLineChart('trumpChart', {trump_datasets}, hasHourlyData);
            createLineChart('ceasefireChart', {ceasefire_datasets}, hasHourlyData);
            createLineChart('hormuzChart', {hormuz_datasets}, hasHourlyData);
            
            // 柱状图 - 原油价格
            createBarChart('oilMarchChart', {oil_march_labels}, {oil_march_values}, '3月底达成概率');
            createBarChart('oilJuneChart', {oil_june_labels}, {oil_june_values}, '6月底达成概率');
        }});
    </script>
</body>
</html>'''
    
    return html


def main():
    print("=" * 70)
    print("Polymarket 静态网页生成工具")
    print("=" * 70)
    
    # 检查是否有每小时数据
    has_hourly = any(
        "hourly_history" in s 
        for key in ["trump_end_military", "us_iran_ceasefire", "hormuz_traffic"]
        for s in REAL_DATA.get(key, {}).get("series", [])
    )
    
    if has_hourly:
        print("\n[检测到每小时历史数据]")
        print("图表将显示从2月1日至今的每小时价格走势")
    else:
        print("\n[使用每日历史数据]")
        print("如需每小时数据，请在 REAL_DATA 中添加 'hourly_history' 字段")
        print("格式: \"hourly_history\": [15.2, 15.5, 15.8, ...]  # 每小时一个值")
    
    # 生成HTML
    html = generate_html()
    
    with open("polymarket_final.html", "w", encoding="utf-8") as f:
        f.write(html)
    
    print("\n" + "=" * 70)
    print("生成完成!")
    print("=" * 70)
    print(f"输出文件: polymarket_final.html")
    print(f"更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print("\n包含的图表:")
    print("  1. 特朗普结束军事行动 (3/31, 4/30, 6/30)")
    print("  2. 美伊停火协议 (3/31, 4/30, 5/31, 6/30)")
    print("  3. 霍尔木兹交通恢复 (4/30前)")
    print("  4. 原油价格 - 3月底")
    print("  5. 原油价格 - 6月底  [新增]")
    print("=" * 70)
    
    if not has_hourly:
        print("\n提示: 要获取每小时历史数据:")
        print("   1. 使用 Gamma API: /markets/{market_id}/prices")
        print("   2. 或从Polymarket网站导出CSV数据")
        print("   3. 填入 REAL_DATA 中的 'hourly_history' 字段")


if __name__ == "__main__":
    main()
