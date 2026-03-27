#!/usr/bin/env python3
"""
生成静态数据跟踪网页 - 方法二：保留原HTML结构，只注入数据
"""

import json
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

WORKDIR = Path(__file__).parent.resolve()
BEIJING_TZ = ZoneInfo("Asia/Shanghai")


def load_json(filename):
    """加载 JSON 文件"""
    try:
        with open(WORKDIR / filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"加载 {filename} 失败: {e}")
        return None


def inject_strait_data(html, data):
    """注入海峡通行数据到 HTML"""
    if not data or 'jin10' not in data:
        return html
    
    jin10 = data['jin10']
    sc = jin10.get('ship_counts', {})
    ip = jin10.get('industry_pressure', {})
    
    # 更新时间
    html = re.sub(
        r'id="strait-update-time"[^>]*>[^<]*</span>',
        f'id="strait-update-time" style="font-size: 0.75rem; color: #94a3b8;">更新: {jin10.get("updated", "--")[:16].replace("T", " ")}</span>',
        html
    )
    
    # 船只数据
    html = re.sub(
        r'id="jin10-hormuz-passing"[^>]*>[^<]*</span>',
        f'id="jin10-hormuz-passing" style="font-size: 2.5rem; font-weight: 700; color: #fa8c16; line-height: 1;">{sc.get("hormuz_passing", "--")}</span>',
        html
    )
    
    total_in_area = sc.get('total_in_area', 0)
    html = re.sub(
        r'id="jin10-total-ships"[^>]*>[^<]*</span>',
        f'id="jin10-total-ships" style="font-size: 1.8rem; font-weight: 700; color: #262626;">{total_in_area:,}</span>',
        html
    )
    
    html = re.sub(
        r'id="jin10-sailing"[^>]*>[^<]*</div>',
        f'id="jin10-sailing" style="color: #1890ff;">{sc.get("sailing", "--")}艘</div>',
        html
    )
    
    html = re.sub(
        r'id="jin10-anchored"[^>]*>[^<]*</div>',
        f'id="jin10-anchored" style="color: #f5222d;">{sc.get("anchored", "--")}艘</div>',
        html
    )
    
    # 压力系数
    total_pressure = ip.get('total', 0)
    html = re.sub(
        r'id="jin10-total-pressure"[^>]*>[^<]*</span>',
        f'id="jin10-total-pressure" style="font-size: 2rem; font-weight: 800; color: #cf1322; line-height: 1;">{total_pressure}</span>',
        html
    )
    
    # 风险等级
    if total_pressure >= 95:
        risk_level, risk_color = "极高风险", "#7f1d1d"
    elif total_pressure >= 80:
        risk_level, risk_color = "高风险", "#cf1322"
    elif total_pressure >= 60:
        risk_level, risk_color = "中等风险", "#fa8c16"
    else:
        risk_level, risk_color = "低风险", "#52c41a"
    
    html = re.sub(
        r'id="jin10-pressure-level"[^>]*>[^<]*</div>',
        f'id="jin10-pressure-level" style="padding: 4px 12px; background: {risk_color}; color: white; border-radius: 12px; font-size: 0.75rem; font-weight: 500;">{risk_level}</div>',
        html
    )
    
    # 各品类数据
    cat_map = {
        'oil': 'jin10-oil',
        'lng': 'jin10-lng', 
        'lpg': 'jin10-lpg',
        'fertilizer': 'jin10-fertilizer',
        'aluminum': 'jin10-aluminum',
        'methanol': 'jin10-methanol'
    }
    
    for key, elem_id in cat_map.items():
        value = ip.get(key, {}).get('value', 0)
        display_value = f"{value:.1f}" if value else "--"
        
        # 替换数值
        html = re.sub(
            rf'id="{elem_id}"[^>]*>[^<]*</span>',
            f'id="{elem_id}" style="font-size: 1.1rem; font-weight: 700; color: #262626;">{display_value}</span>%',
            html
        )
        
        # 替换进度条宽度
        bar_width = f"{value}%" if value else "0%"
        html = re.sub(
            rf'id="{elem_id}-bar"[^>]*style="[^"]*width:[^;]*;',
            f'id="{elem_id}-bar" style="height: 100%; width: {bar_width};',
            html
        )
    
    # 视频和快照
    video_url = jin10.get('video_url', '')
    snapshot_url = jin10.get('snapshot_url', '')
    
    if video_url:
        html = re.sub(
            r'<source[^>]*src="[^"]*"[^>]*>',
            f'<source src="{video_url}" type="video/mp4">',
            html
        )
    
    if snapshot_url:
        html = re.sub(
            r'id="strait-snapshot"[^>]*src="[^"]*"',
            f'id="strait-snapshot" src="{snapshot_url}"',
            html
        )
    
    return html


def generate_static_html():
    """生成静态 HTML"""
    
    # 读取原始 HTML
    with open(WORKDIR / "data-tracking.html", "r", encoding="utf-8") as f:
        html = f.read()
    
    # 加载数据
    strait_data = load_json("strait_data.json")
    
    # 注入数据
    if strait_data:
        html = inject_strait_data(html, strait_data)
        print("OK 海峡通行数据已注入")
    
    # 移除动态加载脚本，保留图表初始化
    # 找到 <script> 标签开始的位置
    script_start = html.find('<script>')
    if script_start > 0:
        # 保留到 </body> 之前的所有内容
        body_end = html.find('</body>')
        if body_end > 0:
            # 保留原始脚本，但移除数据获取部分
            pass  # 暂时保留所有脚本
    
    # 更新页面标题时间
    now = datetime.now(BEIJING_TZ).strftime("%Y-%m-%d %H:%M")
    html = re.sub(
        r'id="page-update-time"[^>]*>[^<]*</div>',
        f'id="page-update-time">更新: {now}</div>',
        html
    )
    
    # 保存静态 HTML
    output_file = WORKDIR / "data-tracking-static.html"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"\n静态 HTML 已生成: {output_file}")
    print(f"生成时间: {now}")
    
    return output_file


if __name__ == "__main__":
    generate_static_html()
