#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新版简报更新脚本 - 按5个板块组织内容
1. 战局进展 2. 各方表态 3. 海峡通行情况 4. 全球供应链 5. 海外投行讨论
"""

import json
from datetime import datetime, timedelta

# 近36小时最新信息（基于搜索结果）
LATEST_NEWS = {
    "date": "2026-04-07",
    "conflict_day": 39,
    "blockade_day": 37,
    
    # 1. 战局进展
    "war_progress": [
        {
            "title": "美以联军扩大对伊朗能源基础设施打击",
            "time": "4月6日 22:30 - 4月7日 03:45",
            "content": "美以联军出动F-35A战机、战斧巡航导弹及B-52H轰炸机，对伊朗胡齐斯坦省阿巴丹炼油厂及Shahran油库群发动多波空袭。卫星图像显示至少4座10万桶容量油罐起火，产能损失约18万桶/日。伊朗官方称7名平民死亡、14人受伤。",
            "source": "Reuters/Fox News"
        },
        {
            "title": "伊朗导弹反击全部被拦截",
            "time": "4月7日 04:20-05:10",
            "content": "伊朗伊斯兰革命卫队发射约25枚'征服者-313'及'流星-3'中程弹道导弹，目标指向以色列内盖夫沙漠军事设施及波斯湾美军基地。美以联合防空系统拦截22枚，仅3枚残片落入无人区，无人员伤亡。",
            "source": "CNN/Times of Israel"
        },
        {
            "title": "以色列空袭德黑兰三座机场",
            "time": "4月6日",
            "content": "以军空袭德黑兰三座机场，摧毁数十架伊朗战斗机。美军中央司令部指挥官指挥对IRGC地下总部发动打击。",
            "source": "Jerusalem Post/Fox News"
        }
    ],
    
    # 2. 各方表态
    "statements": [
        {
            "country": "🇺🇸 美国/特朗普",
            "time": "4月6-7日",
            "content": "设定周二（4月7日）晚8点为最后期限，要求伊朗开放霍尔木兹海峡。威胁'周二将是发电厂日，也是桥梁日'，称'开放那该死的海峡，否则你们将活在地狱里'。警告若伊朗不开放海峡，'整个国家可以在一夜之间被摧毁'。",
            "source": "CNN/NBC News/Bloomberg"
        },
        {
            "country": "🇮🇷 伊朗/最高领袖",
            "time": "4月6日",
            "content": "最高领袖Mojtaba Khamenei表示将继续袭击海峡航运，称海峡将永远不会回到战前状态。IRGC称正在规划'新波斯湾秩序'。伊朗宣称1300万人报名参加'牺牲生命'运动。若民用目标被攻击，将发动'更具毁灭性'的报复。",
            "source": "ISW/Times of Israel/ynetnews"
        },
        {
            "country": "🇸🇦 沙特/阿联酋",
            "time": "4月6日",
            "content": "沙特称拦截7枚弹道导弹，碎片落在能源设施附近。阿联酋表示任何协议必须保证霍尔木兹的使用权，'海峡不能被任何国家扣为人质'，与巴林敦促安理会就霍尔木兹采取行动。",
            "source": "Reuters/Jerusalem Post"
        }
    ],
    
    # 3. 海峡通行情况
    "strait_status": {
        "status": "部分松动但仍受限",
        "daily_transit": "周末21艘船通过，为3月初以来最高；伊朗允许15艘船只通过",
        "blockade_day": 37,
        "key_events": [
            "首艘LNG运输船自战争爆发以来穿越霍尔木兹海峡（4月6日）",
            "两艘卡塔尔满载LNG油轮在抵达海峡前掉头返航",
            "全球航运巨头马士基及MSC宣布暂停所有经霍尔木兹航线，改走好望角",
            "战争险保费较封锁前飙升450%",
            "伊朗官员称海峡将保持关闭直至获得战争赔偿"
        ],
        "impact": "累计导致约5.2亿桶原油运输延迟，亚洲炼厂现货溢价扩大"
    },
    
    # 4. 全球供应链
    "supply_chain": [
        {
            "sector": "铝业",
            "event": "阿联酋EGA Al Taweelah工厂遭袭后需12个月恢复，巴林Alba冶炼厂宣布不可抗力。霍尔木兹关闭使全球约9%原铝供应被困。",
            "impact": "LME铝价突破3500美元/吨，创4年新高"
        },
        {
            "sector": "化肥",
            "event": "阿联酋负责约30%全球化肥（硝酸钾和磷肥）供应的设施受损。每年约1600万吨化肥通过霍尔木兹海峡运输。",
            "impact": "以色列化肥价格飙升180%，FAO警告全球粮食市场受冲击"
        },
        {
            "sector": "LNG/能源",
            "event": "卡塔尔Ras Laffan出口工厂因伊朗袭击已关闭一个多月，约50艘卡塔尔LNG运输船在亚洲闲置。印度在七年 hiatus 后恢复伊朗石油进口。",
            "impact": "全球LNG供应持续紧张，印度经历数十年来最严重天然气短缺"
        },
        {
            "sector": "供应链指数",
            "event": "纽约联储供应链压力指数升至0.68，为2023年初以来最高水平。",
            "impact": "全球商品贸易增长预计从4.7%降至1.5%-2.5%"
        }
    ],
    
    # 5. 海外投行讨论
    "investment_banks": [
        {
            "bank": "摩根大通 (JP Morgan)",
            "speaker": "CEO Jamie Dimon",
            "view": "战争是'不确定性的领域'，可能导致持续的石油和商品价格冲击。全球供应链重塑可能导致粘性通胀，最终利率可能高于市场预期。若霍尔木兹关闭至5月中旬，油价或达150美元/桶。",
            "source": "Greenwich Time/CNN/Newsweek"
        },
        {
            "bank": "高盛 (Goldman Sachs)",
            "view": "认为印度经济能够承受伊朗冲突的能源冲击。上调油价预测，判断冲突将持续6-8周，全球经济增速下修0.4个百分点。",
            "source": "CNBC"
        },
        {
            "bank": "摩根士丹利 (Morgan Stanley)",
            "view": "基准情景下油价中枢90-105美元，冲突降级概率40%，建议减持高收益债、增配黄金ETF，特别指出欧洲能源脆弱性。",
            "source": "Investopedia"
        },
        {
            "bank": "其他分析师",
            "view": "油市可能高估了霍尔木兹海峡的中断程度。Q1 IPO市场已被石油冲击扰乱。布伦特原油约110美元/桶，WTI约113-114美元（较战前上涨约50%）。",
            "source": "Seeking Alpha/Bloomberg Law"
        }
    ],
    
    # 市场数据
    "market_data": {
        "brent": "110.00美元/桶 (+4.5%)",
        "wti": "113.50美元/桶 (+5.2%)",
        "sp500": "5185点 (-1.3%)",
        "nasdaq": "15980点 (-1.6%)",
        "vix": "28.4 (+2.1)",
        "dxy": "105.60 (+0.55)"
    }
}

def generate_html():
    """生成新的简报HTML"""
    
    data = LATEST_NEWS
    
    # 生成战局进展HTML
    war_html = "\n".join([
        f'''<div class="highlight-box military">
            <h5>{item['title']}</h5>
            <p><strong>时间：</strong>{item['time']} | <strong>来源：</strong>{item['source']}</p>
            <p>{item['content']}</p>
        </div>''' for item in data['war_progress']
    ])
    
    # 生成各方表态HTML
    statements_html = "\n".join([
        f'''<div class="highlight-box statements">
            <h5>{item['country']}</h5>
            <p><strong>时间：</strong>{item['time']} | <strong>来源：</strong>{item['source']}</p>
            <p>{item['content']}</p>
        </div>''' for item in data['statements']
    ])
    
    # 生成海峡通行情况HTML
    strait_events = "\n".join([f"<li>{event}</li>" for event in data['strait_status']['key_events']])
    
    strait_html = f'''<div class="highlight-box warning">
        <h5>🚢 霍尔木兹海峡通行状态</h5>
        <p><strong>当前状态：</strong>{data['strait_status']['status']} | <strong>封锁天数：</strong>第{data['strait_status']['blockade_day']}天</p>
        <p><strong>通行数据：</strong>{data['strait_status']['daily_transit']}</p>
        <p><strong>关键事件：</strong></p>
        <ul>{strait_events}</ul>
        <p><strong>影响评估：</strong>{data['strait_status']['impact']}</p>
    </div>'''
    
    # 生成供应链HTML
    supply_html = "\n".join([
        f'''<div class="highlight-box">
            <h5>📦 {item['sector']}</h5>
            <p><strong>事件：</strong>{item['event']}</p>
            <p><strong>影响：</strong>{item['impact']}</p>
        </div>''' for item in data['supply_chain']
    ])
    
    # 生成投行讨论HTML
    bank_html = "\n".join([
        f'''<div class="highlight-box">
            <h5>🏦 {item['bank']}</h5>
            {f"<p><strong>发言人：</strong>{item['speaker']}</p>" if 'speaker' in item else ""}
            <p>{item['view']}</p>
            <p style="font-size:0.8rem;color:#64748b;">来源：{item['source']}</p>
        </div>''' for item in data['investment_banks']
    ])
    
    # 生成市场数据HTML
    market = data['market_data']
    market_html = f'''<div class="market-grid">
        <div class="market-card"><h5>🛢️ 布伦特原油</h5><p>{market['brent']}</p></div>
        <div class="market-card"><h5>🛢️ WTI原油</h5><p>{market['wti']}</p></div>
        <div class="market-card"><h5>📈 标普500</h5><p>{market['sp500']}</p></div>
        <div class="market-card"><h5>📈 纳斯达克</h5><p>{market['nasdaq']}</p></div>
        <div class="market-card"><h5>⚡ VIX波动率</h5><p>{market['vix']}</p></div>
        <div class="market-card"><h5>💱 美元指数</h5><p>{market['dxy']}</p></div>
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
            <h2>📰 美以伊冲突每日简报 ({data['date']})</h2>
            <p class="summary">冲突第{data['conflict_day']}天，霍尔木兹封锁第{data['blockade_day']}天。特朗普设定周二晚8点最后期限要求伊朗开放海峡，威胁打击发电厂和桥梁。伊朗最高领袖强硬回应将继续封锁。美以联军持续打击伊朗能源设施，伊朗导弹反击被拦截。全球供应链压力加剧，投行警告油价或达150美元。</p>
        </div>

        <!-- 1. 战局进展 -->
        <div class="section">
            <h3>⚔️ 战局进展</h3>
            {war_html}
        </div>

        <!-- 2. 各方表态 -->
        <div class="section">
            <h3>🎙️ 各方最新表态</h3>
            {statements_html}
        </div>

        <!-- 3. 海峡通行情况 -->
        <div class="section">
            <h3>🚢 霍尔木兹海峡通行情况</h3>
            {strait_html}
        </div>

        <!-- 4. 全球供应链 -->
        <div class="section">
            <h3>📦 全球供应链影响</h3>
            {supply_html}
        </div>

        <!-- 5. 海外投行讨论 -->
        <div class="section">
            <h3>🏦 海外投行观点</h3>
            {bank_html}
        </div>

        <!-- 市场数据 -->
        <div class="section">
            <h3>📊 市场数据速览</h3>
            {market_html}
            <p style="font-size:0.8rem;color:#64748b;margin-top:12px;">
                数据截止时间：{data['date']} 12:00 UTC+8 | 布伦特原油较战前上涨约50%
            </p>
        </div>

        <div class="footer">数据来源：路透社、彭博社、半岛电视台、CNN、华尔街日报等 | 仅供参考，不构成投资建议</div>
    </div>
</body>
</html>'''
    
    return html

def main():
    # 生成HTML
    html_content = generate_html()
    
    # 保存文件
    with open(r'D:\python_code\海湾以来-最新\briefing.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("简报更新完成！")
    print(f"日期: {LATEST_NEWS['date']}")
    print(f"冲突第{LATEST_NEWS['conflict_day']}天")
    print(f"封锁第{LATEST_NEWS['blockade_day']}天")
    print("\n内容板块:")
    print(f"  - 战局进展: {len(LATEST_NEWS['war_progress'])}条")
    print(f"  - 各方表态: {len(LATEST_NEWS['statements'])}条")
    print(f"  - 海峡通行: {len(LATEST_NEWS['strait_status']['key_events'])}个关键事件")
    print(f"  - 供应链: {len(LATEST_NEWS['supply_chain'])}个行业")
    print(f"  - 投行观点: {len(LATEST_NEWS['investment_banks'])}家机构")

if __name__ == "__main__":
    main()
