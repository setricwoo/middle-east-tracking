#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
供应链跟踪更新脚本
从Excel读取能源设施损毁和产业链影响数据，更新到index.html
"""

import pandas as pd
import json
import re
from pathlib import Path
from datetime import datetime

# 路径配置
WORKDIR = Path(r"D:\python_code\海湾以来-最新")
EXCEL_PATH = Path(r"C:\Users\wujin\.qclaw\workspace\research\middle_east_monitor\中东地缘能源与产业链监控_20260330_v2.xlsx")
HTML_FILE = WORKDIR / "index.html"
DATA_FILE = WORKDIR / "supply_chain_data.json"

def read_excel_data():
    """读取Excel数据"""
    try:
        # 读取表1-能源设施损毁时间线
        df1 = pd.read_excel(EXCEL_PATH, sheet_name='表1-能源设施损毁时间线', header=1)
        df1.columns = ['日期', '国家/地区', '设施名称', '设施类型', '所属企业', '事件描述', '当前状态', '影响评估', '信息来源']
        df1 = df1.dropna(subset=['日期'])

        energy_facilities = []
        for _, row in df1.iterrows():
            energy_facilities.append({
                'date': str(row['日期'])[:10] if pd.notna(row['日期']) else '',
                'country': str(row['国家/地区']) if pd.notna(row['国家/地区']) else '',
                'facility': str(row['设施名称']) if pd.notna(row['设施名称']) else '',
                'type': str(row['设施类型']) if pd.notna(row['设施类型']) else '',
                'company': str(row['所属企业']) if pd.notna(row['所属企业']) else '',
                'event': str(row['事件描述']) if pd.notna(row['事件描述']) else '',
                'status': str(row['当前状态']) if pd.notna(row['当前状态']) else '',
                'impact': str(row['影响评估']) if pd.notna(row['影响评估']) else '',
                'source': str(row['信息来源']) if pd.notna(row['信息来源']) else ''
            })

        # 读取表2-产业链影响时间线
        df2 = pd.read_excel(EXCEL_PATH, sheet_name='表2-产业链影响时间线', header=1)
        df2.columns = ['日期', '国家/地区', '企业/机构', '行业/产品', '事件描述', '影响传导链', '停产/减产规模', '对中国影响', '恢复预期', '信息来源']
        df2 = df2.dropna(subset=['日期'])

        supply_chain = []
        for _, row in df2.iterrows():
            supply_chain.append({
                'date': str(row['日期'])[:10] if pd.notna(row['日期']) else '',
                'country': str(row['国家/地区']) if pd.notna(row['国家/地区']) else '',
                'company': str(row['企业/机构']) if pd.notna(row['企业/机构']) else '',
                'industry': str(row['行业/产品']) if pd.notna(row['行业/产品']) else '',
                'event': str(row['事件描述']) if pd.notna(row['事件描述']) else '',
                'chain': str(row['影响传导链']) if pd.notna(row['影响传导链']) else '',
                'scale': str(row['停产/减产规模']) if pd.notna(row['停产/减产规模']) else '',
                'china_impact': str(row['对中国影响']) if pd.notna(row['对中国影响']) else '',
                'recovery': str(row['恢复预期']) if pd.notna(row['恢复预期']) else '',
                'source': str(row['信息来源']) if pd.notna(row['信息来源']) else ''
            })

        return {
            'updated': datetime.now().strftime('%Y-%m-%d %H:%M'),
            'energy_facilities': energy_facilities,
            'supply_chain': supply_chain
        }
    except Exception as e:
        print(f"读取Excel失败: {e}")
        return None

def generate_supply_chain_html(data):
    """生成供应链跟踪HTML - 完全按照Excel列结构"""

    # 能源设施表格 - 表1-能源设施损毁时间线（9列）
    # 日期, 国家/地区, 设施名称, 设施类型, 所属企业, 事件描述, 当前状态, 影响评估, 信息来源
    energy_html = '''<div class="table-responsive">
            <table class="supply-table">
                <thead>
                    <tr>
                        <th>日期</th>
                        <th>国家/地区</th>
                        <th>设施名称</th>
                        <th>设施类型</th>
                        <th>所属企业</th>
                        <th>事件描述</th>
                        <th>当前状态</th>
                        <th>影响评估</th>
                        <th>信息来源</th>
                    </tr>
                </thead>
                <tbody>'''

    for item in data['energy_facilities'][:20]:  # 显示前20条
        energy_html += f'''
                    <tr>
                        <td data-label="日期">{item['date']}</td>
                        <td data-label="国家/地区">{item['country']}</td>
                        <td data-label="设施名称" class="facility-name">{item['facility']}</td>
                        <td data-label="设施类型">{item['type']}</td>
                        <td data-label="所属企业">{item['company']}</td>
                        <td data-label="事件描述" class="event-desc">{item['event']}</td>
                        <td data-label="当前状态"><span class="status-tag {get_status_class(item['status'])}">{item['status']}</span></td>
                        <td data-label="影响评估">{item['impact']}</td>
                        <td data-label="信息来源">{item['source']}</td>
                    </tr>'''

    energy_html += '''
                </tbody>
            </table>
        </div>'''

    # 产业链影响表格 - 表2-产业链影响时间线（10列）
    # 日期, 国家/地区, 企业/机构, 行业/产品, 事件描述, 影响传导链, 停产/减产规模, 对中国影响, 恢复预期, 信息来源
    chain_html = '''<div class="table-responsive">
            <table class="supply-table">
                <thead>
                    <tr>
                        <th>日期</th>
                        <th>国家/地区</th>
                        <th>企业/机构</th>
                        <th>行业/产品</th>
                        <th>事件描述</th>
                        <th>影响传导链</th>
                        <th>停产/减产规模</th>
                        <th>对中国影响</th>
                        <th>恢复预期</th>
                        <th>信息来源</th>
                    </tr>
                </thead>
                <tbody>'''

    for item in data['supply_chain'][:20]:  # 显示前20条
        chain_html += f'''
                    <tr>
                        <td data-label="日期">{item['date']}</td>
                        <td data-label="国家/地区">{item['country']}</td>
                        <td data-label="企业/机构">{item['company']}</td>
                        <td data-label="行业/产品">{item['industry']}</td>
                        <td data-label="事件描述" class="event-desc">{item['event']}</td>
                        <td data-label="影响传导链">{item['chain']}</td>
                        <td data-label="停产/减产规模">{item['scale']}</td>
                        <td data-label="对中国影响">{item['china_impact']}</td>
                        <td data-label="恢复预期">{item['recovery']}</td>
                        <td data-label="信息来源">{item['source']}</td>
                    </tr>'''

    chain_html += '''
                </tbody>
            </table>
        </div>'''

    return energy_html, chain_html

def get_status_class(status):
    """根据状态返回CSS类名"""
    status = str(status).lower()
    if '严重' in status or '受损' in status or '丧失' in status:
        return 'status-severe'
    elif '损坏' in status or '减产' in status or '中断' in status:
        return 'status-damaged'
    elif '恢复' in status or '正常' in status:
        return 'status-recovered'
    elif '谈判' in status or '进行' in status:
        return 'status-ongoing'
    else:
        return 'status-unknown'

def update_html(energy_html, chain_html, data):
    """更新index.html中的供应链跟踪部分"""

    # CSS样式（单独定义，避免f-string转义问题）
    supply_css = '''
        <style>
        /* 供应链跟踪Tab样式 */
        .supply-tab {
            padding: 10px 20px;
            cursor: pointer;
            border: none;
            background: none;
            font-size: 0.85rem;
            color: #64748b;
            border-bottom: 2px solid transparent;
            transition: all 0.2s;
        }
        .supply-tab:hover {
            color: #1e3a5f;
            background: #f1f5f9;
        }
        .supply-tab.active {
            color: #1e3a5f;
            border-bottom-color: #1e3a5f;
            background: #fff;
        }
        .supply-tab-content {
            display: none;
        }
        .supply-tab-content.active {
            display: block;
        }
        .table-responsive {
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
        }
        .supply-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.75rem;
        }
        .supply-table th {
            background: #f1f5f9;
            padding: 10px 8px;
            text-align: left;
            font-weight: 600;
            color: #334155;
            white-space: nowrap;
            border-bottom: 2px solid #e2e8f0;
        }
        .supply-table td {
            padding: 10px 8px;
            border-bottom: 1px solid #f1f5f9;
            vertical-align: top;
            line-height: 1.5;
        }
        .supply-table tr:hover {
            background: #fafbfc;
        }
        .supply-table .facility-name {
            font-weight: 500;
            color: #1e3a5f;
        }
        .supply-table .event-desc {
            max-width: 450px;
            color: #475569;
        }
        .status-tag {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.7rem;
            font-weight: 500;
        }
        .status-severe { background: #fee2e2; color: #991b1b; }
        .status-damaged { background: #fef3c7; color: #92400e; }
        .status-recovered { background: #dcfce7; color: #166534; }
        .status-ongoing { background: #dbeafe; color: #1e40af; }
        .status-unknown { background: #f1f5f9; color: #64748b; }

        /* 移动端适配 */
        @media (max-width: 768px) {
            .supply-table th, .supply-table td {
                padding: 8px 6px;
                font-size: 0.7rem;
            }
            .supply-table .event-desc {
                max-width: 350px;
            }
            .supply-tab {
                padding: 8px 12px;
                font-size: 0.75rem;
            }
        }
        </style>'''

    supply_script = '''
        <script>
        function switchSupplyTab(tabName) {
            document.querySelectorAll('.supply-tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.supply-tab-content').forEach(c => c.classList.remove('active'));
            event.target.classList.add('active');
            document.getElementById('tab-' + tabName).classList.add('active');
        }
        </script>'''

    # 完整的供应链跟踪HTML
    supply_chain_section = f'''
        <!-- 供应链跟踪 -->
        <div class="section" id="supply-chain-section" style="padding: 0; overflow: hidden;">
            <div style="background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%); color: white; padding: 12px 24px; display: flex; justify-content: space-between; align-items: center;">
                <h3 style="margin: 0; font-size: 1rem; color: white;">🔗 供应链跟踪</h3>
                <span style="font-size: 0.75rem; opacity: 0.8;">更新: {data['updated']}</span>
            </div>
            <div style="border-bottom: 1px solid #e2e8f0; background: #f8fafc; padding: 0 16px;">
                <button class="supply-tab active" onclick="switchSupplyTab('energy')">⚡ 能源设施损毁</button>
                <button class="supply-tab" onclick="switchSupplyTab('chain')">🏭 产业链影响</button>
            </div>
            <div class="supply-tab-content active" id="tab-energy" style="padding: 16px;">
                {energy_html}
            </div>
            <div class="supply-tab-content" id="tab-chain" style="padding: 16px;">
                {chain_html}
            </div>
        </div>
        {supply_css}
        {supply_script}'''

    # 读取原HTML
    with open(HTML_FILE, 'r', encoding='utf-8') as f:
        html = f.read()

    # 查找插入位置：在.footer之后，</div>(container关闭)之前
    if '<!-- 供应链跟踪 -->' in html:
        # 已存在，替换整个供应链跟踪部分
        pattern = r'<!-- 供应链跟踪 -->.*?</script>\s*</div>\s*</div>'
        html = re.sub(pattern, supply_chain_section.strip() + '\n    </div>', html, flags=re.DOTALL)
        print("已更新现有的供应链跟踪部分")
    else:
        # 在.footer的</div>之后插入（container内部）
        footer_pattern = r'(<div class="footer">.*?</div>)'
        html = re.sub(footer_pattern, r'\1\n' + supply_chain_section, html, flags=re.DOTALL)
        print("已添加新的供应链跟踪部分")

    # 写入文件
    with open(HTML_FILE, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"HTML已更新: {HTML_FILE}")

def main():
    print("=" * 60)
    print("供应链跟踪更新器")
    print("=" * 60)

    # 读取Excel数据
    print("\n正在读取Excel数据...")
    data = read_excel_data()

    if not data:
        print("读取数据失败")
        return 1

    print(f"读取到 {len(data['energy_facilities'])} 条能源设施数据")
    print(f"读取到 {len(data['supply_chain'])} 条产业链影响数据")

    # 保存JSON数据
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"数据已保存: {DATA_FILE}")

    # 生成HTML
    print("\n正在生成HTML...")
    energy_html, chain_html = generate_supply_chain_html(data)

    # 更新HTML文件
    update_html(energy_html, chain_html, data)

    print("\n" + "=" * 60)
    print("完成!")
    print("=" * 60)
    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())
