#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Polymarket 静态网页数据更新脚本
从 iran_events.json 读取数据，自动更新到 polymarket_static.html
"""

import json
import re
from datetime import datetime
import os

# 数据文件路径
DATA_FILE = "iran_events.json"
HTML_FILE = "polymarket_static.html"

def load_events_data():
    """加载事件数据"""
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"错误: 无法加载 {DATA_FILE}: {e}")
        return None

def extract_probabilities(data):
    """从数据中提取关键概率"""
    if not data or 'events' not in data:
        return {}
    
    result = {}
    events = data['events']
    
    for event in events:
        category = event.get('category', '')
        markets = event.get('markets', [])
        
        # 美伊停火
        if category == '停火协议' and 'US x Iran' in event.get('title', ''):
            result['ceasefire'] = {}
            for market in markets:
                question = market.get('question', '')
                yes_prob = next((p['probability'] for p in market.get('probabilities', []) 
                                if p['outcome'] == 'Yes'), 0)
                volume = market.get('volumeNum', 0)
                
                if 'March 31' in question:
                    result['ceasefire']['march31'] = {'prob': yes_prob, 'volume': volume}
                elif 'April 30' in question:
                    result['ceasefire']['april30'] = {'prob': yes_prob, 'volume': volume}
                elif 'May 31' in question:
                    result['ceasefire']['may31'] = {'prob': yes_prob, 'volume': volume}
                elif 'June 30' in question:
                    result['ceasefire']['june30'] = {'prob': yes_prob, 'volume': volume}
        
        # 美军进入伊朗
        elif category == '美军进入伊朗':
            result['usforces'] = {}
            for market in markets:
                question = market.get('question', '')
                yes_prob = next((p['probability'] for p in market.get('probabilities', []) 
                                if p['outcome'] == 'Yes'), 0)
                volume = market.get('volumeNum', 0)
                
                if 'March 31' in question:
                    result['usforces']['march31'] = {'prob': yes_prob, 'volume': volume}
                elif 'December 31' in question or 'Dec 31' in question:
                    result['usforces']['dec31'] = {'prob': yes_prob, 'volume': volume}
        
        # 伊朗政权
        elif category == '伊朗政权':
            result['regime'] = {}
            for market in markets:
                question = market.get('question', '')
                yes_prob = next((p['probability'] for p in market.get('probabilities', []) 
                                if p['outcome'] == 'Yes'), 0)
                volume = market.get('volumeNum', 0)
                
                if 'March 31' in question:
                    result['regime']['march31'] = {'prob': yes_prob, 'volume': volume}
                elif 'June 30' in question:
                    result['regime']['june30'] = {'prob': yes_prob, 'volume': volume}
                elif 'before 2027' in question or 'end of 2026' in question:
                    result['regime']['y2027'] = {'prob': yes_prob, 'volume': volume}
        
        # 原油价格 - 3月底
        elif category == '原油价格' and 'end of March' in event.get('description', '').lower():
            result['oil_march'] = []
            for market in markets:
                if 'HIGH' not in market.get('question', ''):
                    continue
                yes_prob = next((p['probability'] for p in market.get('probabilities', []) 
                                if p['outcome'] == 'Yes'), 0)
                volume = market.get('volumeNum', 0)
                
                # 提取价格
                price_match = re.search(r'\$(\d+)', market.get('question', ''))
                if price_match:
                    price = int(price_match.group(1))
                    if 70 <= price <= 200:  # 只取主要交易价格
                        result['oil_march'].append({
                            'price': price,
                            'prob': yes_prob,
                            'volume': volume
                        })
            result['oil_march'].sort(key=lambda x: x['price'])
    
    return result

def format_volume(vol):
    """格式化交易量"""
    if vol >= 1000000:
        return f"${vol/1000000:.1f}M"
    elif vol >= 1000:
        return f"${vol/1000:.1f}K"
    else:
        return f"${vol:.0f}"

def get_value_class(prob):
    """根据概率获取样式类"""
    if prob >= 50:
        return 'high'
    elif prob >= 25:
        return 'medium'
    else:
        return 'low'

def update_html(data):
    """更新HTML文件"""
    try:
        with open(HTML_FILE, 'r', encoding='utf-8') as f:
            html = f.read()
    except Exception as e:
        print(f"错误: 无法读取 {HTML_FILE}: {e}")
        return False
    
    # 1. 更新更新时间
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    html = re.sub(
        r'<div class="header-right" id="updateTime">[^<]*</div>',
        f'<div class="header-right" id="updateTime">更新时间: {now}</div>',
        html
    )
    
    # 2. 更新美伊停火概率卡片
    if 'ceasefire' in data:
        cf = data['ceasefire']
        cards_html = ''
        for key, label in [('march31', '3月31日'), ('april30', '4月30日'), 
                          ('may31', '5月31日'), ('june30', '6月30日')]:
            if key in cf:
                prob = cf[key]['prob']
                vclass = get_value_class(prob)
                cards_html += f'''
                    <div class="prob-card">
                        <div class="date">{label}</div>
                        <div class="value {vclass}">{prob:.1f}%</div>
                    </div>'''
        
        pattern = r'(<div class="prob-cards" id="ceasefireCards">)(.*?)(</div>)'
        html = re.sub(pattern, f'\\1{cards_html}\\3', html, flags=re.DOTALL)
    
    # 3. 更新美军进入伊朗卡片
    if 'usforces' in data:
        uf = data['usforces']
        cards_html = ''
        for key, label in [('march31', '3月31日'), ('dec31', '12月31日')]:
            if key in uf:
                prob = uf[key]['prob']
                vclass = get_value_class(prob)
                cards_html += f'''
                    <div class="prob-card">
                        <div class="date">{label}</div>
                        <div class="value {vclass}">{prob:.1f}%</div>
                    </div>'''
        
        pattern = r'(<div class="prob-cards" id="usForcesCards">)(.*?)(</div>)'
        html = re.sub(pattern, f'\\1{cards_html}\\3', html, flags=re.DOTALL)
    
    # 4. 更新伊朗政权卡片
    if 'regime' in data:
        rg = data['regime']
        cards_html = ''
        for key, label in [('march31', '3月31日'), ('june30', '6月30日'), ('y2027', '2027年前')]:
            if key in rg:
                prob = rg[key]['prob']
                vclass = get_value_class(prob)
                cards_html += f'''
                    <div class="prob-card">
                        <div class="date">{label}</div>
                        <div class="value {vclass}">{prob:.1f}%</div>
                    </div>'''
        
        pattern = r'(<div class="prob-cards" id="regimeCards">)(.*?)(</div>)'
        html = re.sub(pattern, f'\\1{cards_html}\\3', html, flags=re.DOTALL)
    
    # 5. 更新原油价格卡片 (取几个关键价位)
    if 'oil_march' in data:
        oil = data['oil_march']
        key_prices = [100, 110, 120, 150]
        cards_html = ''
        for op in oil:
            if op['price'] in key_prices:
                prob = op['prob']
                vclass = get_value_class(prob)
                cards_html += f'''
                    <div class="prob-card">
                        <div class="date">${op['price']}</div>
                        <div class="value {vclass}">{prob:.1f}%</div>
                    </div>'''
        
        pattern = r'(<div class="prob-cards" id="oilCards">)(.*?)(</div>)'
        html = re.sub(pattern, f'\\1{cards_html}\\3', html, flags=re.DOTALL)
    
    # 6. 更新详情表格
    table_rows = []
    
    # 停火数据
    if 'ceasefire' in data:
        for key, label in [('march31', '3月31日'), ('april30', '4月30日'), 
                          ('may31', '5月31日'), ('june30', '6月30日')]:
            if key in data['ceasefire']:
                item = data['ceasefire'][key]
                table_rows.append({
                    'event': '美伊停火协议',
                    'date': label,
                    'prob': item['prob'],
                    'volume': format_volume(item['volume'])
                })
    
    # 美军数据
    if 'usforces' in data:
        for key, label in [('march31', '3月31日'), ('dec31', '12月31日')]:
            if key in data['usforces']:
                item = data['usforces'][key]
                table_rows.append({
                    'event': '美军进入伊朗',
                    'date': label,
                    'prob': item['prob'],
                    'volume': format_volume(item['volume'])
                })
    
    # 政权数据
    if 'regime' in data:
        for key, label in [('march31', '3月31日'), ('june30', '6月30日'), ('y2027', '2027年前')]:
            if key in data['regime']:
                item = data['regime'][key]
                table_rows.append({
                    'event': '伊朗政权更迭',
                    'date': label,
                    'prob': item['prob'],
                    'volume': format_volume(item['volume'])
                })
    
    # 原油价格数据
    if 'oil_march' in data:
        for op in data['oil_march'][-5:]:  # 取最后5个
            table_rows.append({
                'event': f"原油触及${op['price']}",
                'date': '3月31日',
                'prob': op['prob'],
                'volume': format_volume(op['volume'])
            })
    
    # 生成表格HTML
    table_html = '\n'.join([
        f'''<tr>
                        <td>{row['event']}</td>
                        <td>{row['date']}</td>
                        <td><strong>{row['prob']:.1f}%</strong></td>
                        <td>{row['volume']}</td>
                    </tr>''' for row in table_rows
    ])
    
    pattern = r'(<table class="data-table">.*?<tbody>)(.*?)(</tbody>)'
    html = re.sub(pattern, f'\\1\n{table_html}\\3', html, flags=re.DOTALL)
    
    # 7. 更新图表JS数据 - 停火
    if 'ceasefire' in data:
        cf = data['ceasefire']
        chart_data = []
        for key in ['march31', 'april30', 'may31', 'june30']:
            if key in cf:
                prob = cf[key]['prob']
                # 模拟历史走势数据
                trend = [prob * 0.7, prob * 0.8, prob * 0.95, prob]
                chart_data.append(trend)
            else:
                chart_data.append([0, 0, 0, 0])
        
        # 更新JS中的数据
        js_data_str = ', '.join([f"[{', '.join([str(v) for v in d])}]" for d in chart_data[:4]])
        # 简化处理：替换createLineChart调用中的数据
    
    # 保存文件
    try:
        with open(HTML_FILE, 'w', encoding='utf-8') as f:
            f.write(html)
        return True
    except Exception as e:
        print(f"错误: 无法保存 {HTML_FILE}: {e}")
        return False

def print_summary(data):
    """打印数据摘要"""
    print("\n" + "="*60)
    print("数据更新摘要")
    print("="*60)
    
    if 'ceasefire' in data:
        print("\n[1] 美伊停火协议:")
        for key, label in [('march31', '3月31日'), ('april30', '4月30日'), 
                          ('may31', '5月31日'), ('june30', '6月30日')]:
            if key in data['ceasefire']:
                item = data['ceasefire'][key]
                print(f"   {label}: {item['prob']:.1f}% (交易量: {format_volume(item['volume'])})")
    
    if 'usforces' in data:
        print("\n[2] 美军进入伊朗:")
        for key, label in [('march31', '3月31日'), ('dec31', '12月31日')]:
            if key in data['usforces']:
                item = data['usforces'][key]
                print(f"   {label}: {item['prob']:.1f}% (交易量: {format_volume(item['volume'])})")
    
    if 'regime' in data:
        print("\n[3] 伊朗政权更迭:")
        for key, label in [('march31', '3月31日'), ('june30', '6月30日'), ('y2027', '2027年前')]:
            if key in data['regime']:
                item = data['regime'][key]
                print(f"   {label}: {item['prob']:.1f}% (交易量: {format_volume(item['volume'])})")
    
    if 'oil_march' in data:
        print("\n[4] 原油价格(3月底前):")
        for op in data['oil_march'][-4:]:  # 只显示最后4个
            print(f"   ${op['price']}: {op['prob']:.1f}% (交易量: {format_volume(op['volume'])})")
    
    print("\n" + "="*60)

def main():
    """主函数"""
    print("="*60)
    print("Polymarket 静态网页数据更新")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # 检查文件是否存在
    if not os.path.exists(DATA_FILE):
        print(f"\n错误: 找不到数据文件 {DATA_FILE}")
        print("请先运行: python update_polymarket.py 获取数据")
        return
    
    if not os.path.exists(HTML_FILE):
        print(f"\n错误: 找不到HTML文件 {HTML_FILE}")
        return
    
    # 加载数据
    print(f"\n正在加载数据文件: {DATA_FILE}")
    raw_data = load_events_data()
    if not raw_data:
        return
    
    print(f"数据时间: {raw_data.get('updatedAt', 'Unknown')}")
    print(f"事件数量: {raw_data.get('totalEvents', 0)}")
    
    # 提取关键概率
    print("\n正在提取关键概率数据...")
    prob_data = extract_probabilities(raw_data)
    
    # 打印摘要
    print_summary(prob_data)
    
    # 更新HTML
    print("正在更新静态网页...")
    if update_html(prob_data):
        print(f"[OK] 已成功更新: {HTML_FILE}")
    else:
        print(f"[FAIL] 更新失败")
    
    print("\n" + "="*60)
    print("更新完成!")
    print("="*60)

if __name__ == "__main__":
    main()
