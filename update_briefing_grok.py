#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
美以伊冲突每日简报 - AI API 自动更新脚本（仅更新内容，不修改布局）
"""

import json
import os
import sys
import re
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# ============ 配置区域 ============
CONFIG = {
    "api_key": "sk-9XSaf4XwU4DefoKqpuZWVZ5OrZbzmw6YsksHaqo7VcDw3ZF1",
    "api_type": "grok",
    "base_url": "https://api.vectorengine.ai/v1",
    "model": "grok-4.2",
    "max_tokens": 50000,
    "temperature": 0.4,
    "briefing_file": "briefing.html",
}

CUSTOM_HEADERS = {}

def get_api_config():
    """获取API配置"""
    config = CONFIG.copy()
    if os.environ.get("AI_API_KEY"):
        config["api_key"] = os.environ.get("AI_API_KEY")
    if os.environ.get("AI_BASE_URL"):
        config["base_url"] = os.environ.get("AI_BASE_URL")
    if os.environ.get("AI_MODEL"):
        config["model"] = os.environ.get("AI_MODEL")
    config["api_url"] = f"{config['base_url']}/chat/completions"
    return config

def get_today_info():
    """获取今日信息"""
    today = datetime.now()
    date_str = today.strftime("%Y年%m月%d日")
    conflict_start = datetime(2026, 2, 28)
    conflict_day = (today - conflict_start).days + 1
    blockade_start = datetime(2026, 3, 2)
    blockade_day = (today - blockade_start).days + 1
    return {
        "date": date_str,
        "date_iso": today.strftime("%Y-%m-%d"),
        "conflict_day": conflict_day,
        "blockade_day": max(0, blockade_day),
    }

def call_api(config, system_prompt, user_prompt):
    """调用API"""
    if not config["api_key"]:
        print("[错误] 未设置API密钥")
        return None
    
    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json",
        **CUSTOM_HEADERS
    }
    
    payload = {
        "model": config["model"],
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": config["temperature"],
        "max_tokens": config["max_tokens"]
    }
    
    try:
        response = requests.post(
            config["api_url"],
            headers=headers,
            json=payload,
            timeout=120
        )
        
        if response.status_code == 429:
            print(f"[错误] API请求频率限制(HTTP 429)，请稍后重试")
            return None
        elif response.status_code != 200:
            print(f"[错误] API返回错误: HTTP {response.status_code}")
            return None
        
        result = response.json()
        return result.get("choices", [{}])[0].get("message", {}).get("content", "")
        
    except requests.exceptions.Timeout:
        print("[错误] API请求超时")
        return None
    except Exception as e:
        print(f"[错误] API请求失败: {e}")
        return None

def parse_json_response(text):
    """解析JSON响应"""
    if not text:
        return None
    
    try:
        if "```json" in text:
            match = re.search(r'```json\s*(\{[\s\S]*?\})\s*```', text)
            if match:
                return json.loads(match.group(1))
        
        if "```" in text:
            match = re.search(r'```\s*(\{[\s\S]*?\})\s*```', text)
            if match:
                return json.loads(match.group(1))
        
        match = re.search(r'(\{[\s\S]*\})', text)
        if match:
            return json.loads(match.group(1))
        
        return json.loads(text)
        
    except json.JSONDecodeError as e:
        print(f"[错误] JSON解析失败: {e}")
        return None

def generate_briefing_with_ai(config, info):
    """使用AI API生成简报内容"""
    
    system_prompt = """你是华泰固收研究所的中东地缘政治首席分析师。

【任务】生成美以伊冲突每日简报，以JSON格式输出。

【输出格式 - 严格遵守】
{
  "summary": "简报摘要（200字以内）",
  "conflict_progress": [
    {"title": "标题", "content": "详细内容...", "type": "military|damage|statements|reaction"}
  ],
  "positions": {"us": "...", "israel": "...", "iran": "...", "others": "..."},
  "timeline": [{"time": "时间", "event": "事件", "type": "类型"}],
  "market_data": {"oil": "...", "equity": "...", "bond": "...", "fx": "...", "volatility": "..."},
  "bank_views": "投行观点汇总",
  "analysis": {
    "geopolitical": "地缘政治分析（500字）",
    "outlook": "后续预判（400字）",
    "impact": "全球影响（500字）",
    "strategy": "投资建议（400字）"
  },
  "watch_points": ["要点1", "要点2"],
  "news": [{"title": "标题", "source": "来源", "url": "链接", "summary": "摘要"}]
}"""

    user_prompt = f"""请生成{info['date']}（美以伊冲突第{info['conflict_day']}天）的每日简报。

要求：
1. 基于最新公开信息
2. 内容真实准确，不虚构数据
3. 严格按JSON格式输出
4. 深度分析部分要详细展开

请直接输出JSON，不要添加其他说明文字。"""

    print(f"[任务1/2] 正在调用AI API生成简报...")
    print(f"[信息] 日期: {info['date']}")
    print(f"[信息] 冲突第{info['conflict_day']}天")
    print(f"[信息] 模型: {config['model']}")
    print(f"[信息] 预计需要30-60秒，请耐心等待...")
    
    content = call_api(config, system_prompt, user_prompt)
    
    if not content:
        return None
    
    print("[成功] API响应接收完成")
    print(f"[信息] 响应内容长度: {len(content)}字符")
    
    data = parse_json_response(content)
    
    if data:
        data["date"] = info["date"]
        data["conflict_day"] = info["conflict_day"]
        data["blockade_day"] = info["blockade_day"]
    
    return data

def generate_content_html(data, info):
    """生成内容HTML（仅内容部分，不包含head和body标签）"""
    
    # 冲突进展
    progress_html = ""
    for item in data.get("conflict_progress", []):
        type_class = item.get("type", "normal")
        progress_html += f'<div class="highlight-box {type_class}"><h5>{item.get("title", "")}</h5><p>{item.get("content", "")}</p></div>'
    
    # 各方表态
    positions = data.get("positions", {})
    positions_html = "<h4>各方最新表态</h4><ul>"
    if "us" in positions: positions_html += f'<li><strong>🇺🇸 美国：</strong>{positions["us"]}</li>'
    if "israel" in positions: positions_html += f'<li><strong>🇮🇱 以色列：</strong>{positions["israel"]}</li>'
    if "iran" in positions: positions_html += f'<li><strong>🇮🇷 伊朗：</strong>{positions["iran"]}</li>'
    if "others" in positions: positions_html += f'<li><strong>🌍 国际社会：</strong>{positions["others"]}</li>'
    positions_html += "</ul>"
    
    # 时间线
    timeline_items = data.get("timeline", [])
    mid = len(timeline_items) // 2 + len(timeline_items) % 2
    left_col = timeline_items[:mid]
    right_col = timeline_items[mid:]
    
    def make_timeline_html(items):
        html = ""
        for item in items:
            type_class = item.get("type", "normal")
            html += f'<div class="timeline-item {type_class}"><div class="timeline-time">{item.get("time", "")}</div><div class="timeline-content">{item.get("event", "")}</div></div>'
        return html
    
    timeline_html = f'<div class="timeline-two-col"><div class="timeline-col">{make_timeline_html(left_col)}</div><div class="timeline-col">{make_timeline_html(right_col)}</div></div>'
    
    # 市场数据
    market_data = data.get("market_data", {})
    market_html = '<div class="market-grid">'
    if "oil" in market_data:
        market_html += f'<div class="market-card"><h5>🛢️ 原油</h5><p>{market_data["oil"]}</p></div>'
    if "equity" in market_data:
        market_html += f'<div class="market-card"><h5>📈 股市</h5><p>{market_data["equity"]}</p></div>'
    if "bond" in market_data:
        market_html += f'<div class="market-card"><h5>📉 债市</h5><p>{market_data["bond"]}</p></div>'
    if "fx" in market_data:
        market_html += f'<div class="market-card"><h5>💱 外汇</h5><p>{market_data["fx"]}</p></div>'
    if "volatility" in market_data:
        market_html += f'<div class="market-card"><h5>⚡ 波动率</h5><p>{market_data["volatility"]}</p></div>'
    market_html += "</div>"
    
    # 投行观点
    bank_views = data.get("bank_views", "")
    bank_html = f'<div class="highlight-box"><h5>🏦 投行观点汇总</h5><p>{bank_views}</p></div>' if bank_views else ""
    
    # 深度分析
    analysis = data.get("analysis", {})
    analysis_html = ""
    if "geopolitical" in analysis:
        analysis_html += f'<h4>🌍 地缘政治深度分析</h4><p>{analysis["geopolitical"]}</p>'
    if "outlook" in analysis:
        analysis_html += f'<h4>🔮 后续进展预判</h4><p>{analysis["outlook"]}</p>'
    if "impact" in analysis:
        analysis_html += f'<h4>💥 全球经济影响</h4><p>{analysis["impact"]}</p>'
    if "strategy" in analysis:
        analysis_html += f'<div class="highlight-box"><h5>💡 投资策略建议</h5><p>{analysis["strategy"]}</p></div>'
    
    # 关注要点
    watch_points = data.get("watch_points", [])
    watch_html = "<h4>📌 关键关注要点</h4><ul>"
    for point in watch_points:
        watch_html += f'<li>{point}</li>'
    watch_html += "</ul>"
    
    # 新闻
    news_html = ""
    for item in data.get("news", []):
        news_html += f'<a href="{item.get("url", "#")}" target="_blank" class="news-item"><div class="news-title">{item.get("title", "")}</div><div class="news-source">{item.get("source", "")} · {info["date"]}</div><div class="news-summary">{item.get("summary", "")}</div></a>'
    
    # 构建完整内容HTML
    html = f'''<div class="container">
        <div class="briefing-header">
            <h2>📰 美以伊冲突每日简报 ({info['date']})</h2>
            <p class="summary">{data.get("summary", "")}</p>
        </div>

        <div class="section">
            <h3>📍 冲突最新进展</h3>
            {progress_html}
            {positions_html}
        </div>

        <div class="section">
            <h3>⏱️ 关键时间线</h3>
            {timeline_html}
        </div>

        <div class="section">
            <h3>🔍 深度分析</h3>
            {analysis_html}
            {watch_html}
        </div>

        <div class="section">
            <h3>📊 市场影响分析</h3>
            {market_html}
            {bank_html}
        </div>

        <div class="section">
            <h3>📰 最新新闻</h3>
            <div class="news-list">{news_html}</div>
        </div>

        <div class="footer">数据来源：路透社、彭博社、半岛电视台、财联社、新华社等 | 仅供参考，不构成投资建议</div>
    </div>'''
    
    return html

def update_html_content(file_path, content_html, info):
    """更新HTML文件中的内容（保留原有布局和样式）"""
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            original_html = f.read()
    except FileNotFoundError:
        print(f"[错误] 文件不存在: {file_path}")
        return False
    
    # 更新header-right中的日期
    updated_html = re.sub(
        r'<div class="header-right">.*?</div>',
        f'<div class="header-right">更新时间: {info["date"]}</div>',
        original_html
    )
    
    # 替换container部分（从<div class="container">到</body>之前）
    pattern = r'<div class="container">.*?</div>\s*<div class="footer">.*?</div>\s*</div>'
    
    if re.search(pattern, updated_html, re.DOTALL):
        # 如果找到旧的container结构，替换它
        updated_html = re.sub(pattern, content_html.strip(), updated_html, flags=re.DOTALL)
    else:
        # 尝试另一种模式：从<div class="container">到</body>
        pattern2 = r'<div class="container">.*?</body>'
        if re.search(pattern2, updated_html, re.DOTALL):
            updated_html = re.sub(pattern2, content_html.strip() + '\n</body>', updated_html, flags=re.DOTALL)
        else:
            print("[警告] 无法找到内容区域，尝试备用方案")
            # 备用：直接在</body>前插入
            updated_html = updated_html.replace('</body>', content_html.strip() + '\n</body>')
    
    # 写入文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_html)
    
    return True

def main():
    """主函数"""
    print("=" * 60)
    print("美以伊冲突每日简报 - AI API 更新工具")
    print("特点：仅更新内容，保留页面布局")
    print("=" * 60)
    print()
    
    config = get_api_config()
    info = get_today_info()
    
    print(f"[日期] {info['date']}")
    print(f"[冲突] 第{info['conflict_day']}天")
    print(f"[封锁] 第{info['blockade_day']}天")
    print()
    
    # 生成简报内容
    data = generate_briefing_with_ai(config, info)
    
    if not data:
        print("\n[失败] 无法生成简报")
        return 1
    
    print("\n[成功] 简报内容生成完成")
    
    # 生成内容HTML
    print("\n[任务2/2] 正在更新网页文件...")
    content_html = generate_content_html(data, info)
    
    # 更新HTML文件
    if update_html_content(config["briefing_file"], content_html, info):
        print(f"[成功] 已更新: {config['briefing_file']}")
    else:
        print(f"[失败] 无法更新: {config['briefing_file']}")
        return 1
    
    print("\n" + "=" * 60)
    print("简报更新完成!")
    print(f"文件位置: {config['briefing_file']}")
    print("=" * 60)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
