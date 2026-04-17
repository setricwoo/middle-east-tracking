html = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>【华泰固收】中东地缘跟踪 - 美以伊冲突每日简报</title>
    <style>
        *{margin:0;padding:0;box-sizing:border-box;}
        body{font-family:'Segoe UI',system-ui,-apple-system,sans-serif;background:#f8fafc;color:#1e293b;line-height:1.8;}
        .header {
            background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%);
            color: white;
            padding: 12px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }
        .header-main {
            max-width: 1400px;
            margin: 0 auto;
            padding: 0 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
        }
        .header-left {
            position: absolute;
            left: 20px;
        }
        .header-left h1 {
            font-size: 1.1rem;
            font-weight: 600;
            margin: 0;
        }
        .header-center {
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            justify-content: center;
        }
        .nav-btn {
            color: rgba(255,255,255,0.85);
            text-decoration: none;
            padding: 6px 12px;
            border-radius: 6px;
            font-size: 0.85rem;
            transition: all 0.2s;
            white-space: nowrap;
        }
        .nav-btn:hover {
            background: rgba(255,255,255,0.15);
            color: white;
        }
        .nav-btn.active {
            background: rgba(255,255,255,0.2);
            color: white;
            font-weight: 500;
        }
        .container{max-width:900px;margin:0 auto;padding:24px 20px;}
        .briefing-header{background:linear-gradient(135deg,#fef3c7 0%,#fde68a 100%);border:1px solid #f59e0b;border-radius:12px;padding:24px;margin-bottom:24px;}
        .briefing-header h2{color:#92400e;font-size:1.4rem;margin-bottom:12px;}
        .briefing-header .summary{color:#78350f;font-size:0.95rem;line-height:1.8;}
        .section{background:#fff;border-radius:12px;padding:24px;margin-bottom:20px;box-shadow:0 1px 3px rgba(0,0,0,0.08);border:1px solid #e2e8f0;}
        .section h3{color:#1e40af;font-size:1.15rem;margin-bottom:16px;padding-bottom:10px;border-bottom:2px solid #e2e8f0;}
        .section p{color:#475569;font-size:0.95rem;margin-bottom:12px;text-align:justify;}
        .section ul{padding-left:20px;margin-bottom:12px;}
        .section li{color:#475569;font-size:0.95rem;margin-bottom:8px;}
        .highlight-box{background:#eff6ff;border-left:4px solid #3b82f6;padding:16px;border-radius:0 8px 8px 0;margin:16px 0;}
        .highlight-box.critical{background:#fef2f2;border-left-color:#dc2626;}
        .highlight-box.warning{background:#fffbeb;border-left-color:#f59e0b;}
        .highlight-box.statements{background:#f0fdf4;border-left-color:#16a34a;}
        .highlight-box h5{color:#1e40af;font-size:0.95rem;margin-bottom:10px;}
        .highlight-box.critical h5{color:#dc2626;}
        .highlight-box.warning h5{color:#b45309;}
        .highlight-box.statements h5{color:#166534;}
        .market-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin:16px 0;}
        .market-card{background:#f8fafc;border-radius:8px;padding:16px;border:1px solid #e2e8f0;}
        .market-card h5{color:#1e40af;font-size:0.9rem;margin-bottom:8px;}
        .market-card p{color:#475569;font-size:0.85rem;margin:0;}
        .footer{text-align:center;padding:24px;color:#64748b;font-size:0.8rem;border-top:1px solid #e2e8f0;margin-top:40px;}
        @media (max-width: 768px) {
            .market-grid{grid-template-columns:repeat(2,1fr);}
        }
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
        <!-- 标题区 -->
        <div class="briefing-header">
            <h2>每日简报 (2026年4月17日)</h2>
            <p class="summary">冲突第49天，霍尔木兹封锁第45天。<strong>过去24小时核心变化：特朗普称美伊"非常接近"达成协议；美军向中东增派超1万名士兵；巴基斯坦陆军参谋长赴德黑兰斡旋；以黎达成10天临时停火。</strong></p>
        </div>

        <!-- 1. 过去24小时重点 -->
        <div class="section">
            <h3>过去24小时重点</h3>
            
            <div class="highlight-box critical">
                <h5>美伊谈判：特朗普称"非常接近"达成协议，但伊朗否认</h5>
                <p><strong>时间：</strong>4月16日 | <strong>来源：</strong>White House / Reuters / ISW</p>
                <p>特朗普4月16日表示，美伊<strong>"非常接近"</strong>达成协议，伊朗<strong>"已同意几乎所有事情"</strong>，包括交出浓缩铀库存。他称若谈判在伊斯兰堡敲定，可能亲赴巴基斯坦签署协议。但伊朗外交部发言人巴加埃同日否认已就延长停火达成协议。IRGC附属媒体也否认路透社关于伊朗妥协的报道，显示伊朗谈判委员会内部存在严重分歧。</p>
            </div>

            <div class="highlight-box warning">
                <h5>美军向中东增派超1万名士兵</h5>
                <p><strong>时间：</strong>4月15-16日 | <strong>来源：</strong>Washington Post / CENTCOM</p>
                <p>《华盛顿邮报》报道，美国将向中东增派<strong>超过10,000名士兵</strong>，包括约<strong>6,000人</strong>随"乔治-H-W-布什"号航母打击群，以及约<strong>4,200人</strong>随"拳师"两栖戒备群和第11海军陆战队远征队（预计月底抵达）。这将使该地区美军总人数增至约<strong>6万人</strong>。凯恩与赫格塞思划定的封锁线从阿曼拉斯哈德延伸至伊朗-巴基斯坦边境。</p>
            </div>

            <div class="highlight-box">
                <h5>以黎达成10天临时停火</h5>
                <p><strong>时间：</strong>4月16日 17:00 ET生效 | <strong>来源：</strong>US State Department / ISW</p>
                <p>特朗普宣布以色列与黎巴嫩同意实施为期<strong>10天的临时停火</strong>。美国务院公布六项条款：以色列停止在黎巴嫩的进攻性军事行动；黎巴嫩政府采取有意义步骤防止真主党袭击；以黎可在双方同意下延长停火。真主党方面表示，只有在以色列完全停止军事行动的情况下才会遵守停火。</p>
            </div>
        </div>

        <!-- 2. 战局进展 -->
        <div class="section">
            <h3>战局进展</h3>
            
            <div class="highlight-box">
                <h5>伊朗导弹部队利用停火重建战术单位</h5>
                <p><strong>时间：</strong>4月16日 | <strong>来源：</strong>ISW / CNN</p>
                <p>国防部长赫格塞思承认，伊朗已开始挖掘被掩埋的导弹发射器，并试图恢复导弹部队战术和作战级单位的协调能力。卫星图像显示伊朗正在清理大不里士西南导弹基地和霍梅因导弹基地入口处的 debris。但在战略层面，重建被空袭摧毁的导弹工业设施（从最终组件装配到铝钢厂）将<strong>极其困难</strong>，所需时间远超2025年6月打击后的恢复期。</p>
            </div>

            <div class="highlight-box">
                <h5>真主党在停火前密集袭击以色列北部</h5>
                <p><strong>时间：</strong>4月15-16日 | <strong>来源：</strong>ISW</p>
                <p>在以黎停火生效前，真主党声称对以色列北部社区和以军基础设施发动了<strong>30次袭击</strong>，对黎巴嫩南部的以军发动了<strong>37次袭击</strong>。以军表示已完成对宾特朱拜勒的"围攻"，并摧毁了真主党大部分反舰导弹库存。</p>
            </div>
        </div>

        <!-- 3. 各方表态 -->
        <div class="section">
            <h3>各方最新表态</h3>
            
            <div class="highlight-box statements">
                <h5>美国/特朗普</h5>
                <p><strong>时间：</strong>4月16日 | <strong>来源：</strong>White House / ISW</p>
                <ul>
                    <li>特朗普：美伊"非常接近"达成协议，伊朗"已同意几乎所有事情"，包括交出浓缩铀库存</li>
                    <li>特朗普称可能亲赴<strong>巴基斯坦</strong>签署协议</li>
                    <li>美国务院公布以黎10天停火六项条款</li>
                </ul>
            </div>

            <div class="highlight-box statements">
                <h5>伊朗/官方</h5>
                <p><strong>时间：</strong>4月16日 | <strong>来源：</strong>ISW / Reuters</p>
                <ul>
                    <li><strong>外交部发言人巴加埃：</strong>否认已就延长停火达成协议</li>
                    <li><strong>IRGC附属媒体：</strong>否认路透社关于伊朗在海峡和核计划上妥协的所有报道</li>
                    <li><strong>谈判立场：</strong>美方要求铀浓缩暂停20年，伊朗回应最多暂停<strong>3-5年</strong></li>
                </ul>
            </div>

            <div class="highlight-box statements">
                <h5>中国/王毅</h5>
                <p><strong>时间：</strong>4月15日 | <strong>来源：</strong>ISW</p>
                <p>伊朗外长阿拉格齐与王毅通话，感谢中方缓和紧张局势的努力。王毅表示伊朗在霍尔木兹海峡的<strong>"权益必须得到尊重和保护"</strong>。中国约13.4%的海上进口石油来自伊朗，对封锁影响能源供应深感关切。</p>
            </div>
        </div>

        <!-- 4. 斡旋动态 -->
        <div class="section">
            <h3>国际斡旋动态</h3>
            
            <div class="highlight-box">
                <h5>巴基斯坦：陆军参谋长亲赴德黑兰调解</h5>
                <p><strong>时间：</strong>4月16日 | <strong>来源：</strong>Xinhua / ISW</p>
                <p>巴基斯坦陆军参谋长<strong>阿西姆-穆尼尔元帅</strong>率高级代表团访问德黑兰，会见伊朗谈判代表团团长议长<strong>加利巴夫</strong>，以及负责联合作战的<strong>Khatam ol Anbia总部指挥官阿里阿巴迪</strong>——显示巴方试图同时接触伊朗文官和军方决策层。巴基斯坦总理<strong>谢里夫</strong>已访问沙特，本周还将访问卡塔尔和土耳其，进行多方位穿梭外交。</p>
            </div>

            <div class="highlight-box">
                <h5>埃及：在方案中添加限制民兵条款</h5>
                <p><strong>来源：</strong>Indian Express / Reuters</p>
                <p>埃及参与美伊调解，在美方提出的方案中添加了要求<strong>伊朗限制对地区武装组织支持</strong>的条款。埃及官员将该方案描述为"全面协议"，旨在实现停火。</p>
            </div>
        </div>

        <!-- 5. 海峡通行情况 -->
        <div class="section">
            <h3>霍尔木兹海峡通行情况</h3>
            
            <div class="highlight-box warning">
                <h5>海峡封锁状态更新</h5>
                <p><strong>当前状态：</strong>美军封锁已有效停止伊朗海上贸易 | <strong>封锁天数：</strong>第45天</p>
                <p><strong>关键数据（4月15日14:00 - 4月16日14:00 ET）：</strong></p>
                <ul>
                    <li>至少<strong>4艘船只</strong>进入霍尔木兹海峡，<strong>2艘</strong>离开</li>
                    <li>CENTCOM宣布封锁已<strong>有效停止</strong>伊朗进出口海上贸易</li>
                    <li>伊朗4月13日起已暂停石化出口</li>
                    <li>伊朗考虑<strong>暂时暂停船运</strong>以避免测试封锁并降低谈判前紧张</li>
                </ul>
            </div>
        </div>

        <!-- 6. 全球供应链 -->
        <div class="section">
            <h3>全球供应链影响</h3>
            
            <div class="highlight-box">
                <h5>能源市场</h5>
                <p>油价维持高位但有所回落。WTI原油仍在<strong>91美元/桶以上</strong>，布伦特原油约<strong>96美元/桶</strong>。IMF警告中东战争将放缓全球经济增长，即使战争很快结束，全球增长也可能从2025年的3.4%降至今年的3.1%。</p>
            </div>

            <div class="highlight-box">
                <h5>航运与保险</h5>
                <p>战争险保费持续高企。美军划定从阿曼拉斯哈德到伊朗-巴基斯坦边境的对角线封锁线，对途经该区域的船只实施"登船、搜查和扣押"行动。红海航线同时面临胡塞武装威胁复燃风险。</p>
            </div>
        </div>

        <!-- 7. 海外观点 -->
        <div class="section">
            <h3>海外观点</h3>
            
            <div class="highlight-box">
                <h5>ISW评估</h5>
                <p><strong>来源：</strong>Institute for the Study of War, April 16</p>
                <p>ISW认为，伊朗利用霍尔木兹海峡地位索取让步的提议实际上是一种<strong>胁迫</strong>——接受此类要求将向伊朗表明其可以现在和未来都利用海峡胁迫美国。IRGC在谈判中的过大角色以及谈判委员会的内部不统一，使伊朗难以在这一进程中做出并执行决定。以黎停火是以色列的"善意姿态"，为谈判和平协议争取时间，但真主党的遵守意愿取决于以色列是否完全停止军事行动。</p>
            </div>
        </div>

        <!-- 市场数据 -->
        <div class="section">
            <h3>市场数据速览</h3>
            <div class="market-grid">
                <div class="market-card"><h5>布伦特原油</h5><p>96.00美元/桶 (+5.2%)</p></div>
                <div class="market-card"><h5>WTI原油</h5><p>91.50美元/桶 (+4.8%)</p></div>
                <div class="market-card"><h5>标普500</h5><p>约5,150点</p></div>
                <div class="market-card"><h5>纳斯达克</h5><p>约16,100点</p></div>
                <div class="market-card"><h5>VIX波动率</h5><p>约25</p></div>
                <div class="market-card"><h5>美元指数</h5><p>99.50</p></div>
            </div>
        </div>

        <div class="footer">数据来源：ISW、路透社、华盛顿邮报、白宫、新华社、印度快报等 | 仅供参考，不构成投资建议</div>
    </div>
</body>
</html>"""

with open('briefing.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('briefing.html updated successfully')
