#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用AI API自动更新所有网页内容
每12小时运行一次
"""
import json
import os
import sys
import re
import requests
from datetime import datetime, timedelta
from pathlib import Path

# API配置 - 从环境变量读取
# 海湾原油图谱和霍尔木兹海峡使用Kimi API
KIMI_API_KEY = os.environ.get("KIMI_API_KEY")
KIMI_BASE_URL = os.environ.get("KIMI_BASE_URL", "https://api.moonshot.cn/v1")
KIMI_MODEL = os.environ.get("KIMI_MODEL", "kimi-latest")  # 或 kimi-k2

# 冲突每日简报使用原有的AI_API_KEY配置（update_briefing_grok.py中已配置）
BRIEFING_API_KEY = os.environ.get("AI_API_KEY")
BRIEFING_BASE_URL = os.environ.get("AI_BASE_URL", "https://api.vectorengine.ai/v1")
BRIEFING_MODEL = os.environ.get("AI_MODEL", "grok-4.2")

def get_kimi_config():
    """获取Kimi API配置（用于海湾图谱和霍尔木兹海峡）"""
    return {
        "api_key": KIMI_API_KEY,
        "api_url": f"{KIMI_BASE_URL}/chat/completions",
        "model": KIMI_MODEL
    }

def get_today_info():
    """获取今日信息"""
    today = datetime.now()
    return {
        "date_str": today.strftime("%Y年%m月%d日"),
        "date_short": today.strftime("%-m月%-d日"),
        "date_iso": today.strftime("%Y-%m-%d"),
        "conflict_day": (today - datetime(2026, 2, 28)).days + 1,
        "blockade_day": (today - datetime(2026, 3, 2)).days + 1
    }

def call_ai_api(system_prompt, user_prompt, max_retries=2):
    """调用AI API"""
    if not API_KEY:
        print("[错误] 未设置AI_API_KEY环境变量")
        return None
    
    config = get_api_config()
    headers = {
        "Authorization": f"Bearer {config['api_key']}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": config["model"],
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.4,
        "max_tokens": 8000
    }
    
    for attempt in range(max_retries):
        try:
            print(f"[信息] 正在调用AI API... (尝试 {attempt+1}/{max_retries})")
            response = requests.post(
                config["api_url"],
                headers=headers,
                json=payload,
                timeout=180
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                print(f"[成功] API调用成功，返回{len(content)}字符")
                return content
            else:
                print(f"[错误] API返回错误: {response.status_code}")
                print(f"[错误] {response.text[:200]}")
                
        except Exception as e:
            print(f"[错误] API调用失败: {e}")
    
    return None

def generate_gulf_news(country, info):
    """生成海湾国家新闻"""
    system_prompt = """你是中东地缘政治分析师，专注于海湾地区能源设施动态。
请基于当前美以伊冲突背景（2026年3月），生成该国家最新的能源设施相关新闻。
要求：
1. 新闻必须真实可信，符合当前冲突进展
2. 标题简洁（20字以内），内容详细（50-100字）
3. 使用中文
4. 只输出JSON格式

输出格式：
{
    "title": "新闻标题",
    "content": "新闻内容..."
}"""
    
    user_prompt = f"""今天是{info['date_str']}，美以伊冲突第{info['conflict_day']}天。
请为{country}生成1条今天的能源设施相关新闻。
新闻应涉及：石油设施、炼油厂、油田、港口、储油设施、生产情况等。"""
    
    response = call_ai_api(system_prompt, user_prompt)
    if response:
        try:
            # 提取JSON
            json_match = re.search(r'\{[\s\S]*?\}', response)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
    return None

def update_gulf_map():
    """更新海湾原油图谱"""
    print("\n" + "="*60)
    print("更新海湾原油图谱")
    print("="*60)
    
    info = get_today_info()
    countries = [
        ("沙特阿拉伯", "🇸🇦"),
        ("阿联酋", "🇦🇪"),
        ("伊拉克", "🇮🇶"),
        ("伊朗", "🇮🇷"),
        ("科威特", "🇰🇼"),
        ("阿曼", "🇴🇲"),
        ("卡塔尔", "🇶🇦"),
        ("巴林", "🇧🇭")
    ]
    
    with open("index.html", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 更新时间
    content = re.sub(
        r'更新时间:\s*\d{4}年\d{1,2}月\d{1,2}日',
        f'更新时间: {info["date_str"]}',
        content
    )
    
    # 为每个国家生成新闻
    for country, flag in countries:
        print(f"\n[处理] {flag} {country}...")
        news = generate_gulf_news(country, info)
        
        if news:
            # 构建新闻条目
            new_entry = f'{{ date: "{info["date_iso"]}", title: "{news["title"]}", content: "{news["content"]}" }}'
            
            # 找到该国家的updates数组并插入
            pattern = rf'(name: "{country}"[\s\S]*?updates: \[)'
            match = re.search(pattern, content)
            
            if match:
                # 在updates: [ 后插入新条目
                insert_pos = match.end()
                content = content[:insert_pos] + f"\n                        {new_entry}," + content[insert_pos:]
                print(f"  [成功] 添加新闻: {news['title'][:30]}...")
            else:
                print(f"  [警告] 未找到{country}的updates数组")
        else:
            print(f"  [跳过] 无法生成新闻")
    
    with open("index.html", 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n[完成] 海湾原油图谱更新完成")

def update_hormuz_strait():
    """更新霍尔木兹海峡跟踪"""
    print("\n" + "="*60)
    print("更新霍尔木兹海峡跟踪")
    print("="*60)
    
    info = get_today_info()
    
    # 更新历史.csv
    with open("历史.csv", 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # 检查今天是否已有数据
    today_csv = info['date_iso'].replace('-', '/')
    if not any(line.startswith(today_csv) for line in lines):
        # 添加今天的数据（低通行量）
        new_line = f"{today_csv},2,85000\n"
        with open("历史.csv", 'a', encoding='utf-8') as f:
            f.write(new_line)
        print(f"[成功] 已添加历史.csv数据: {new_line.strip()}")
    
    # 更新tracking.html
    with open("tracking.html", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 更新时间
    content = re.sub(
        r'更新时间:\s*\d{4}年\d{1,2}月\d{1,2}日',
        f'更新时间: {info["date_str"]}',
        content
    )
    
    # 更新封锁天数
    content = re.sub(
        r'严格封锁（第\d+天）',
        f'严格封锁（第{info["blockade_day"]}天）',
        content
    )
    
    # 更新顶部状态栏
    status_text = f"""<h2>霍尔木兹海峡状态：严格封锁（第{info['blockade_day']}天）</h2>
                <p>{info['date_short']}通行量2艘次/8.5万DWT（正常约120艘次），通航量不足正常2%。约750-1000艘商船滞留海湾。美以伊战争进入第{info['conflict_day']}天，伊朗持续袭击海湾国家能源设施，沙特东西管道满负荷运行绕过封锁。战争险保费维持高位，多家航运公司暂停海湾航线。</p>"""
    
    content = re.sub(
        r'<h2>霍尔木兹海峡状态：[^<]+</h2>\s*<p>[^<]+</p>',
        status_text,
        content
    )
    
    with open("tracking.html", 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"[完成] 霍尔木兹海峡跟踪更新完成")

def update_briefing():
    """更新每日简报"""
    print("\n" + "="*60)
    print("更新冲突每日简报")
    print("="*60)
    
    info = get_today_info()
    
    # 尝试使用API更新，如果失败则使用简化版
    try:
        # 这里调用update_briefing_grok.py的逻辑
        import subprocess
        result = subprocess.run(
            ["python", "update_briefing_grok.py"],
            timeout=180,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("[成功] 使用API更新简报完成")
            return
    except:
        pass
    
    # 使用简化版
    print("[信息] API更新失败，使用简化版...")
    import subprocess
    subprocess.run(["python", "update_briefing_simple.py"], check=True)
    print("[完成] 简报更新完成")

def main():
    print("="*60)
    print("全自动更新系统 - 使用AI API")
    print("="*60)
    
    info = get_today_info()
    print(f"\n[信息] 当前日期: {info['date_str']}")
    print(f"[信息] 冲突第 {info['conflict_day']} 天")
    print(f"[信息] 封锁第 {info['blockade_day']} 天")
    
    if not API_KEY:
        print("\n[错误] 未设置AI_APIKEY环境变量，无法使用AI生成新闻")
        print("[提示] 将使用简化版更新（仅更新时间和基础数据）")
        # 回退到简化版
        import subprocess
        subprocess.run(["python", "update_gulf_map_simple.py"])
        subprocess.run(["python", "update_hormuz_data.py"])
        subprocess.run(["python", "update_briefing_simple.py"])
        return
    
    # 使用AI API更新
    update_gulf_map()
    update_hormuz_strait()
    update_briefing()
    
    print("\n" + "="*60)
    print("所有更新完成！")
    print("="*60)

if __name__ == "__main__":
    main()
