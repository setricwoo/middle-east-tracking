#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从Polymarket获取数据并直接更新HTML页面
"""

import requests
import json
import time
import re
from datetime import datetime
from typing import Dict, List, Any

# Polymarket APIs
GAMMA_API = "https://gamma-api.polymarket.com"
CLOB_API = "https://clob.polymarket.com"

# 事件slug列表
EVENT_SLUGS = [
    "trump-announces-end-of-military-operations-against-iran-by",
    "us-x-iran-ceasefire-by",
    "avg-of-ships-transiting-strait-of-hormuz-end-of-march",
    "strait-of-hormuz-traffic-returns-to-normal-by-april-30",
    "will-crude-oil-cl-hit-by-end-of-march",
    "cl-hit-jun-2026",
]

# 请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "Origin": "https://polymarket.com",
    "Referer": "https://polymarket.com/",
}

# 颜色配置
COLORS = {
    "blue": "#3b82f6",
    "green": "#10b981",
    "amber": "#f59e0b",
    "red": "#ef4444",
    "purple": "#8b5cf6",
    "cyan": "#06b6d4",
    "pink": "#ec4899",
}


def get_event_by_slug(slug: str) -> Dict:
    """通过slug获取事件数据"""
    url = f"{GAMMA_API}/events"
    params = {"slug": slug, "_s": "slug"}
    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if isinstance(data, list) and len(data) > 0:
            event = data[0]
            event_id = event.get("id")
            if event_id:
                detail_url = f"{GAMMA_API}/events/{event_id}"
                detail_resp = requests.get(detail_url, headers=HEADERS, timeout=30)
                if detail_resp.status_code == 200:
                    return detail_resp.json()
            return event
        return {}
    except Exception as e:
        print(f"  获取事件失败 {slug}: {e}")
        return {}


def get_price_history(token_id: str, interval: str = "all") -> List[Dict]:
    """获取价格历史数据"""
    url = f"{CLOB_API}/prices-history"
    params = {"market": token_id, "interval": interval}
    try:
        resp = requests.get(url, params=params, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data.get("history", [])
    except:
        for alt_interval in ["max", "1d"]:
            try:
                params["interval"] = alt_interval
                resp = requests.get(url, params=params, headers=HEADERS, timeout=30)
                if resp.status_code == 200:
                    data = resp.json()
                    return data.get("history", [])
            except:
                pass
        return []


def parse_json_field(field) -> List:
    """解析JSON字段"""
    if isinstance(field, str):
        try:
            return json.loads(field)
        except:
            return []
    elif isinstance(field, list):
        return field
    return []


def fetch_all_events_data() -> Dict:
    """获取所有事件数据"""
    all_data = {}

    for slug in EVENT_SLUGS:
        print(f"获取: {slug}")
        event = get_event_by_slug(slug)
        if not event:
            continue

        event_id = event.get("id")
        event_title = event.get("title", "")
        markets = event.get("markets", [])

        markets_data = []
        for m in markets:
            question = m.get("question", "")
            outcomes = parse_json_field(m.get("outcomes"))
            outcome_prices = parse_json_field(m.get("outcomePrices"))
            clob_token_ids = parse_json_field(m.get("clobTokenIds"))
            volume = m.get("volume", "0")

            market_info = {
                "question": question,
                "outcomes": {},
                "volume": volume,
                "closed": m.get("closed", False),
            }

            for i, outcome_name in enumerate(outcomes):
                token_id = clob_token_ids[i] if i < len(clob_token_ids) else ""
                current_price = 0.0
                if i < len(outcome_prices):
                    try:
                        current_price = float(outcome_prices[i])
                    except:
                        pass

                # 获取价格历史
                price_history = []
                if token_id and not m.get("closed", False):
                    history = get_price_history(token_id)
                    for h in history:
                        try:
                            ts = h.get("t", 0)
                            price = h.get("p", 0)
                            dt = datetime.fromtimestamp(ts)
                            price_history.append({
                                "time": dt.strftime('%m-%d %H:%M'),
                                "timestamp": ts,
                                "price": round(price * 100, 2)
                            })
                        except:
                            pass
                    time.sleep(0.15)

                market_info["outcomes"][outcome_name] = {
                    "currentPrice": round(current_price * 100, 2),
                    "priceHistory": price_history
                }

            markets_data.append(market_info)

        all_data[slug] = {
            "title": event_title,
            "markets": markets_data
        }

    return all_data


def generate_html(data: Dict) -> str:
    """生成完整的HTML页面"""
    update_time = datetime.now().strftime('%Y-%m-%d %H:%M')

    html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Polymarket 伊朗相关预测市场 | 实时追踪</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #0f172a; color: #e2e8f0; }
        .chart-container { position: relative; height: 300px; width: 100%; }
        .card { background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); border: 1px solid #334155; }
        .positive { color: #10b981; }
        .negative { color: #ef4444; }
    </style>
</head>
<body class="min-h-screen">
    <nav class="bg-slate-900/95 backdrop-blur border-b border-slate-700 sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex items-center justify-between h-16">
                <div class="flex items-center space-x-4">
                    <span class="text-xl font-bold text-blue-400">Polymarket Iran</span>
                    <span class="text-xs text-slate-400">实时预测市场数据</span>
                </div>
                <div class="flex items-center space-x-6 text-sm">
                    <a href="index.html" class="text-slate-300 hover:text-white transition">首页</a>
                    <a href="briefing.html" class="text-slate-300 hover:text-white transition">简报</a>
                    <a href="tracking.html" class="text-slate-300 hover:text-white transition">追踪</a>
                    <a href="news.html" class="text-slate-300 hover:text-white transition">新闻</a>
                </div>
            </div>
        </div>
    </nav>

    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div class="mb-8">
            <h1 class="text-3xl font-bold text-white mb-2">伊朗相关预测市场追踪</h1>
            <p class="text-slate-400">基于 Polymarket 实时数据 | 更新时间: ''' + update_time + '''</p>
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
'''

    # 图表计数器
    chart_idx = 0

    # 1. 特朗普宣布结束军事行动
    trump_data = data.get("trump-announces-end-of-military-operations-against-iran-by", {})
    html += generate_event_card(trump_data, "特朗普宣布结束对伊朗军事行动", "不同截止日期的概率预测",
                                 ["March 15th", "March 31st", "April 30th", "June 30th"],
                                 ["blue", "green", "amber", "purple"], chart_idx)
    chart_idx += 1

    # 2. 美伊停火
    ceasefire_data = data.get("us-x-iran-ceasefire-by", {})
    html += generate_event_card(ceasefire_data, "美伊停火时间", "不同截止日期的概率预测",
                                 ["March 31", "April 30", "June 30"],
                                 ["blue", "green", "amber"], chart_idx)
    chart_idx += 1

    # 3. 霍尔木兹海峡船舶数量
    ships_data = data.get("avg-of-ships-transiting-strait-of-hormuz-end-of-march", {})
    html += generate_ships_card(ships_data, chart_idx)
    chart_idx += 1

    # 4. 霍尔木兹海峡恢复正常
    normal_data = data.get("strait-of-hormuz-traffic-returns-to-normal-by-april-30", {})
    html += generate_simple_card(normal_data, "霍尔木兹海峡恢复正常", "4月30日前恢复正常的概率",
                                  chart_idx, "blue")
    chart_idx += 1

    # 5. 3月原油价格
    oil_march_data = data.get("will-crude-oil-cl-hit-by-end-of-march", {})
    html += generate_oil_card(oil_march_data, "3月原油价格预测", "Will Crude Oil (CL) hit by end of March?",
                               ["$90", "$100", "$110", "$120"], chart_idx)
    chart_idx += 1

    # 6. 6月原油价格
    oil_june_data = data.get("cl-hit-jun-2026", {})
    html += generate_oil_card(oil_june_data, "6月原油价格预测", "Will Crude Oil (CL) hit by end of June?",
                               ["$90", "$100", "$110", "$150"], chart_idx)
    chart_idx += 1

    html += '''
        </div>
    </div>

    <footer class="bg-slate-900 border-t border-slate-700 mt-12 py-6">
        <div class="max-w-7xl mx-auto px-4 text-center text-slate-400 text-sm">
            <p>数据来源: Polymarket | 仅供信息参考，不构成投资建议</p>
        </div>
    </footer>
</body>
</html>
'''
    return html


def generate_event_card(event_data: Dict, title: str, subtitle: str,
                        date_labels: List[str], colors: List[str], chart_idx: int) -> str:
    """生成事件卡片HTML"""
    markets = event_data.get("markets", [])

    # 查找匹配的市场
    matched_markets = []
    for label in date_labels:
        for m in markets:
            q = m.get("question", "").lower()
            if label.lower() in q and not m.get("closed", False):
                matched_markets.append({"label": label, "market": m})
                break

    if not matched_markets:
        return ""

    # 生成概率显示
    prob_html = '<div class="grid grid-cols-2 gap-2 mb-4">\n'
    color_list = list(COLORS.values())
    datasets = []
    all_times = set()

    for i, item in enumerate(matched_markets):
        label = item["label"]
        m = item["market"]
        outcomes = m.get("outcomes", {})
        yes_price = outcomes.get("Yes", {}).get("currentPrice", 0)
        volume = float(m.get("volume", 0))
        volume_str = f"${int(volume/1000)}K" if volume > 0 else ""

        color = color_list[i % len(color_list)]
        prob_html += f'''            <div class="flex items-center gap-2">
                <div class="w-3 h-3 rounded-full" style="background-color: {color}"></div>
                <span class="text-sm text-slate-300">{label}:</span>
                <span class="text-lg font-bold" style="color: {color}">{yes_price}%</span>
                <span class="text-xs text-slate-500">({volume_str})</span>
            </div>\n'''

        # 收集历史数据
        history = outcomes.get("Yes", {}).get("priceHistory", [])
        data_points = {}
        for h in history:
            t = h["time"]
            all_times.add(t)
            data_points[t] = h["price"]

        datasets.append({
            "label": label,
            "data": data_points,
            "color": color
        })

    prob_html += '        </div>\n'

    # 排序时间点
    sorted_times = sorted(list(all_times))
    labels_json = json.dumps(sorted_times)

    # 生成数据集
    chart_datasets = []
    for ds in datasets:
        data_arr = [ds["data"].get(t, None) for t in sorted_times]
        chart_datasets.append({
            "label": ds["label"],
            "data": data_arr,
            "borderColor": ds["color"],
            "backgroundColor": ds["color"].replace(")", ", 0.1)").replace("rgb", "rgba"),
            "borderWidth": 2,
            "fill": True,
            "tension": 0.4,
            "pointRadius": 0,
            "pointHoverRadius": 4
        })

    chart_id = f"chart_{chart_idx}"

    html = f'''            <div class="card rounded-xl p-6">
                <h2 class="text-xl font-semibold text-white mb-1">{title}</h2>
                <p class="text-sm text-slate-400 mb-4">{subtitle}</p>

                {prob_html}

                <div class="chart-container">
                    <canvas id="{chart_id}"></canvas>
                </div>
            </div>

            <script>
                new Chart(document.getElementById('{chart_id}'), {{
                    type: 'line',
                    data: {{
                        labels: {labels_json},
                        datasets: {json.dumps(chart_datasets)}
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        interaction: {{ intersect: false, mode: 'index' }},
                        plugins: {{
                            legend: {{ position: 'top', labels: {{ color: '#94a3b8', font: {{ size: 11 }} }} }}
                        }},
                        scales: {{
                            x: {{ grid: {{ color: 'rgba(100, 116, 139, 0.2)', lineWidth: 0.5, drawBorder: false }}, ticks: {{ color: '#64748b', maxTicksLimit: 10 }} }},
                            y: {{ grid: {{ color: 'rgba(100, 116, 139, 0.2)', lineWidth: 0.5, drawBorder: false }}, ticks: {{ color: '#64748b' }} }}
                        }}
                    }}
                }});
            </script>
'''
    return html


def generate_ships_card(ships_data: Dict, chart_idx: int) -> str:
    """生成船舶数量卡片"""
    markets = ships_data.get("markets", [])

    # 船舶区间
    ranges = ["0-10", "10-20", "20-30", "30-40", "40-50", "50-60", "60+"]
    prob_data = {}

    for m in markets:
        q = m.get("question", "").lower()
        outcomes = m.get("outcomes", {})
        yes_price = outcomes.get("Yes", {}).get("currentPrice", 0)

        for r in ranges:
            # 匹配区间
            if f"between {r.split('-')[0]} and {r.split('-')[-1]}" in q or f"{r.split('-')[0]} and {r.split('-')[-1]}" in q:
                prob_data[r] = yes_price
                break
            elif "60 or more" in q and r == "60+":
                prob_data[r] = yes_price
                break

    if not prob_data:
        return ""

    color_list = list(COLORS.values())

    prob_html = '<div class="grid grid-cols-3 gap-2 mb-4">\n'
    for i, r in enumerate(ranges):
        if r in prob_data:
            color = color_list[i % len(color_list)]
            prob_html += f'''            <div class="flex items-center gap-2">
                <div class="w-3 h-3 rounded-full" style="background-color: {color}"></div>
                <span class="text-sm text-slate-300">{r}:</span>
                <span class="text-lg font-bold" style="color: {color}">{prob_data[r]}%</span>
            </div>\n'''
    prob_html += '        </div>\n'

    # 图表数据
    chart_data = [prob_data.get(r, 0) for r in ranges]
    chart_id = f"chart_{chart_idx}"

    html = f'''            <div class="card rounded-xl p-6">
                <h2 class="text-xl font-semibold text-white mb-1">3月霍尔木兹海峡船舶数量</h2>
                <p class="text-sm text-slate-400 mb-4">平均每日通过船舶数量的概率分布</p>

                {prob_html}

                <div class="chart-container">
                    <canvas id="{chart_id}"></canvas>
                </div>
            </div>

            <script>
                new Chart(document.getElementById('{chart_id}'), {{
                    type: 'bar',
                    data: {{
                        labels: {json.dumps(ranges)},
                        datasets: [{{
                            label: '概率 (%)',
                            data: {json.dumps(chart_data)},
                            backgroundColor: {json.dumps(color_list[:len(ranges)])},
                            borderWidth: 0
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{
                            legend: {{ display: false }}
                        }},
                        scales: {{
                            x: {{ grid: {{ color: 'rgba(100, 116, 139, 0.2)', lineWidth: 0.5, drawBorder: false }}, ticks: {{ color: '#64748b' }} }},
                            y: {{ grid: {{ color: 'rgba(100, 116, 139, 0.2)', lineWidth: 0.5, drawBorder: false }}, ticks: {{ color: '#64748b' }} }}
                        }}
                    }}
                }});
            </script>
'''
    return html


def generate_simple_card(event_data: Dict, title: str, subtitle: str,
                         chart_idx: int, color_name: str) -> str:
    """生成简单Yes/No卡片"""
    markets = event_data.get("markets", [])
    if not markets:
        return ""

    m = markets[0]
    outcomes = m.get("outcomes", {})
    yes_price = outcomes.get("Yes", {}).get("currentPrice", 0)
    no_price = outcomes.get("No", {}).get("currentPrice", 100 - yes_price)

    history = outcomes.get("Yes", {}).get("priceHistory", [])
    labels = [h["time"] for h in history]
    data = [h["price"] for h in history]

    color = COLORS.get(color_name, COLORS["blue"])
    chart_id = f"chart_{chart_idx}"

    html = f'''            <div class="card rounded-xl p-6">
                <h2 class="text-xl font-semibold text-white mb-1">{title}</h2>
                <p class="text-sm text-slate-400 mb-4">{subtitle}</p>

                <div class="grid grid-cols-2 gap-4 mb-4">
                    <div class="text-center p-4 bg-slate-800/50 rounded-lg">
                        <div class="text-3xl font-bold" style="color: {color}">{yes_price}%</div>
                        <div class="text-sm text-slate-400 mt-1">Yes</div>
                    </div>
                    <div class="text-center p-4 bg-slate-800/50 rounded-lg">
                        <div class="text-3xl font-bold text-slate-400">{no_price}%</div>
                        <div class="text-sm text-slate-400 mt-1">No</div>
                    </div>
                </div>

                <div class="chart-container">
                    <canvas id="{chart_id}"></canvas>
                </div>
            </div>

            <script>
                new Chart(document.getElementById('{chart_id}'), {{
                    type: 'line',
                    data: {{
                        labels: {json.dumps(labels)},
                        datasets: [{{
                            label: 'Yes (%)',
                            data: {json.dumps(data)},
                            borderColor: '{color}',
                            backgroundColor: '{color}'.replace(')', ', 0.1)').replace('#', 'rgba(').replace(/([0-9a-f]{{2}})/gi, function(m) {{ return parseInt(m, 16) + ','; }}),
                            borderWidth: 2,
                            fill: true,
                            tension: 0.4,
                            pointRadius: 0
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{ legend: {{ display: false }} }},
                        scales: {{
                            x: {{ grid: {{ color: 'rgba(100, 116, 139, 0.2)', lineWidth: 0.5, drawBorder: false }}, ticks: {{ color: '#64748b', maxTicksLimit: 10 }} }},
                            y: {{ grid: {{ color: 'rgba(100, 116, 139, 0.2)', lineWidth: 0.5, drawBorder: false }}, ticks: {{ color: '#64748b' }} }}
                        }}
                    }}
                }});
            </script>
'''
    return html


def generate_oil_card(oil_data: Dict, title: str, subtitle: str,
                      price_points: List[str], chart_idx: int) -> str:
    """生成原油价格卡片"""
    markets = oil_data.get("markets", [])

    # 匹配价格点
    price_data = {}
    for m in markets:
        q = m.get("question", "")
        outcomes = m.get("outcomes", {})
        yes_price = outcomes.get("Yes", {}).get("currentPrice", 0)

        for p in price_points:
            if f"${p.replace('$', '')}" in q or f"hit__ by" in q.lower():
                # 提取价格
                import re
                match = re.search(r'\$(\d+)', q)
                if match:
                    price = f"${match.group(1)}"
                    if price in price_points or match.group(1) in [p.replace('$', '') for p in price_points]:
                        price_data[price] = yes_price
                        break

    if not price_data:
        # 使用默认匹配
        for p in price_points:
            for m in markets:
                if f"${p.replace('$', '')}" in m.get("question", ""):
                    outcomes = m.get("outcomes", {})
                    price_data[p] = outcomes.get("Yes", {}).get("currentPrice", 0)
                    break

    if not price_data:
        return ""

    color_list = list(COLORS.values())
    prob_html = '<div class="grid grid-cols-2 gap-2 mb-4">\n'
    for i, (price, prob) in enumerate(sorted(price_data.items())):
        color = color_list[i % len(color_list)]
        prob_html += f'''            <div class="flex items-center gap-2">
                <div class="w-3 h-3 rounded-full" style="background-color: {color}"></div>
                <span class="text-sm text-slate-300">{price}:</span>
                <span class="text-lg font-bold" style="color: {color}">{prob}%</span>
            </div>\n'''
    prob_html += '        </div>\n'

    chart_id = f"chart_{chart_idx}"
    sorted_prices = sorted(price_data.keys(), key=lambda x: int(x.replace('$', '')))
    chart_data = [price_data[p] for p in sorted_prices]

    html = f'''            <div class="card rounded-xl p-6">
                <h2 class="text-xl font-semibold text-white mb-1">{title}</h2>
                <p class="text-sm text-slate-400 mb-4">{subtitle}</p>

                {prob_html}

                <div class="chart-container">
                    <canvas id="{chart_id}"></canvas>
                </div>
            </div>

            <script>
                new Chart(document.getElementById('{chart_id}'), {{
                    type: 'bar',
                    data: {{
                        labels: {json.dumps(sorted_prices)},
                        datasets: [{{
                            label: '概率 (%)',
                            data: {json.dumps(chart_data)},
                            backgroundColor: {json.dumps(color_list[:len(sorted_prices)])},
                            borderWidth: 0
                        }}]
                    }},
                    options: {{
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {{ legend: {{ display: false }} }},
                        scales: {{
                            x: {{ grid: {{ color: 'rgba(100, 116, 139, 0.2)', lineWidth: 0.5, drawBorder: false }}, ticks: {{ color: '#64748b' }} }},
                            y: {{ grid: {{ color: 'rgba(100, 116, 139, 0.2)', lineWidth: 0.5, drawBorder: false }}, ticks: {{ color: '#64748b' }} }}
                        }}
                    }}
                }});
            </script>
'''
    return html


def main():
    print("="*60)
    print("Polymarket HTML 更新器")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    # 获取数据
    print("\n正在获取Polymarket数据...")
    data = fetch_all_events_data()

    # 生成HTML
    print("\n正在生成HTML...")
    html = generate_html(data)

    # 保存HTML
    filename = "polymarket.html"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"HTML已保存: {filename}")

    # 同时保存JSON数据
    json_filename = "polymarket_data.json"
    with open(json_filename, 'w', encoding='utf-8') as f:
        json.dump({"fetchedAt": datetime.now().isoformat(), "events": data}, f, ensure_ascii=False, indent=2)
    print(f"数据已保存: {json_filename}")

    print("\n" + "="*60)
    print("完成!")
    print("="*60)


if __name__ == "__main__":
    main()
