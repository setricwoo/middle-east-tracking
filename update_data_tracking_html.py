#!/usr/bin/env python3
"""
更新 data-tracking.html 中的静态数据

将各个 JSON 文件的数据直接嵌入到 HTML 中，避免前端动态加载问题。
运行方式: python update_data_tracking_html.py
"""

import json
import re
from datetime import datetime
from pathlib import Path

# 配置
HTML_FILE = Path(__file__).parent / "data-tracking.html"
DATA_FILES = {
    "STATIC_STRAIT_DATA": "strait_data.json",
    "STATIC_MARKET_DATA": "market_data.json",
    "STATIC_LIQUIDITY_DATA": "liquidity_data.json",
    "STATIC_ISW_DATA": "isw_data.json",
}


def load_json_data(filename: str) -> dict | None:
    """加载 JSON 文件，如果不存在返回 None"""
    filepath = Path(__file__).parent / filename
    if not filepath.exists():
        print(f"  [跳过] {filename} 不存在")
        return None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"  [加载] {filename} 成功")
        return data
    except Exception as e:
        print(f"  [错误] {filename} 加载失败: {e}")
        return None


def sanitize_for_js(data):
    """清理数据，移除可能导致JS语法错误的特殊字符"""
    if isinstance(data, dict):
        # 移除body_html和summary字段（包含多行文本，会导致JS语法错误）
        if 'body_html' in data:
            del data['body_html']
        if 'summary' in data:
            del data['summary']
        return {k: sanitize_for_js(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_for_js(item) for item in data]
    elif isinstance(data, str):
        # 移除控制字符，将换行符替换为空格（避免JS字符串中的换行问题）
        result = ''.join(char if ord(char) >= 32 else ' ' for char in data)
        # 将反斜杠替换为正斜杠（Windows路径兼容）
        result = result.replace('\\', '/')
        # 移除可能导致问题的Unicode字符
        result = result.replace('\u2028', ' ').replace('\u2029', ' ')
        return result
    else:
        return data


def generate_static_data_js() -> str:
    """生成静态数据的 JavaScript 代码"""
    lines = ["    /* STATIC_DATA_START */"]

    for var_name, filename in DATA_FILES.items():
        data = load_json_data(filename)
        if data is not None:
            # 清理数据
            data = sanitize_for_js(data)
            # 生成JSON
            json_str = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
            lines.append(f"    let {var_name} = {json_str};")
        else:
            lines.append(f"    let {var_name} = null;")

    lines.append("    /* STATIC_DATA_END */")
    return "\n".join(lines)


def update_html():
    """更新 HTML 文件中的静态数据"""
    print(f"\n{'='*50}")
    print(f"更新 data-tracking.html 静态数据")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")

    # 读取 HTML 文件
    if not HTML_FILE.exists():
        print(f"[错误] {HTML_FILE} 不存在")
        return False

    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html_content = f.read()

    # 生成新的静态数据
    new_static_data = generate_static_data_js()

    # 使用正则替换静态数据区域
    pattern = r"/\* STATIC_DATA_START \*/.*?/\* STATIC_DATA_END \*/"
    if not re.search(pattern, html_content, re.DOTALL):
        print("[错误] 未找到静态数据标记，请检查 HTML 文件")
        return False

    new_html = re.sub(pattern, new_static_data, html_content, flags=re.DOTALL)

    # 写回文件
    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(new_html)

    # 统计文件大小变化
    old_size = len(html_content)
    new_size = len(new_html)
    print(f"\n[完成] HTML 文件已更新")
    print(f"  原大小: {old_size:,} 字节")
    print(f"  新大小: {new_size:,} 字节")
    print(f"  变化: {new_size - old_size:+,} 字节")

    return True


def reset_html():
    """重置HTML到模板状态（清空静态数据）"""
    print("重置HTML到模板状态...")

    if not HTML_FILE.exists():
        print(f"[错误] {HTML_FILE} 不存在")
        return False

    with open(HTML_FILE, "r", encoding="utf-8") as f:
        html_content = f.read()

    # 生成空的静态数据
    empty_data = "/* STATIC_DATA_START */let STATIC_STRAIT_DATA = null;let STATIC_MARKET_DATA = null;let STATIC_POLYMARKET_DATA = null;let STATIC_LIQUIDITY_DATA = null;let STATIC_ISW_DATA = null;/* STATIC_DATA_END */"

    pattern = r"/\* STATIC_DATA_START \*/.*?/\* STATIC_DATA_END \*/"
    if not re.search(pattern, html_content, re.DOTALL):
        print("[错误] 未找到静态数据标记")
        return False

    new_html = re.sub(pattern, empty_data, html_content, flags=re.DOTALL)

    with open(HTML_FILE, "w", encoding="utf-8") as f:
        f.write(new_html)

    print("[完成] HTML已重置")
    return True


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--reset":
        reset_html()
    else:
        update_html()
