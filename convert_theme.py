#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将 polymarket.html (深色主题) 转换为 polymarket_static.html (浅色主题)
并添加统一的导航栏
"""

import re
from datetime import datetime

def convert_theme():
    """转换主题"""

    # 读取原始文件
    try:
        with open("polymarket.html", 'r', encoding='utf-8') as f:
            html = f.read()
    except Exception as e:
        print(f"无法读取 polymarket.html: {e}")
        return False

    # ==================== 颜色映射 ====================
    color_replacements = {
        # 背景色
        'background-color: #0f172a': 'background-color: #f8fafc',
        'background-color: #1e293b': 'background-color: #ffffff',
        'bg-slate-900': 'bg-white',
        'bg-slate-800': 'bg-gray-50',
        'bg-slate-900/95': 'bg-white/95',
        'bg-slate-700': 'bg-gray-200',
        'bg-blue-900/30': 'bg-blue-50',
        'bg-gray-900': 'bg-gray-50',

        # 文字颜色
        'text-white': 'text-slate-800',
        'text-slate-300': 'text-slate-600',
        'text-slate-400': 'text-slate-500',
        'text-slate-500': 'text-slate-400',
        'text-blue-400': 'text-blue-600',
        'text-blue-200': 'text-blue-800',

        # 边框颜色
        'border-slate-700': 'border-slate-200',
        'border-slate-600': 'border-slate-300',
        'border-blue-700/50': 'border-blue-200',

        # 卡片背景
        'linear-gradient(135deg, #1e293b 0%, #0f172a 100%)': 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)',
        'border: 1px solid #334155': 'border: 1px solid #e2e8f0',

        # 图表颜色保持不变（蓝、绿、橙、红）
    }

    # 应用颜色替换
    for old, new in color_replacements.items():
        html = html.replace(old, new)

    # ==================== 替换导航栏 ====================
    old_nav = '''    <!-- Navigation -->
    <nav class="bg-white/95 backdrop-blur border-b border-slate-200 sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div class="flex items-center justify-between h-16">
                <div class="flex items-center space-x-4">
                    <span class="text-xl font-bold text-blue-600">Polymarket Iran</span>
                    <span class="text-xs text-slate-500">实时预测市场数据</span>
                </div>
                <div class="flex items-center space-x-6 text-sm">
                    <a href="index.html" class="text-slate-600 hover:text-blue-600 transition">首页</a>
                    <a href="briefing.html" class="text-slate-600 hover:text-blue-600 transition">简报</a>
                    <a href="tracking.html" class="text-slate-600 hover:text-blue-600 transition">追踪</a>
                    <a href="news.html" class="text-slate-600 hover:text-blue-600 transition">新闻</a>
                </div>
            </div>
        </div>
    </nav>'''

    new_nav = '''    <!-- 统一导航栏 -->
    <div class="header">
        <div class="header-main">
            <div class="header-left">
                <span class="header-icon">📊</span>
                <h1>中东地缘跟踪</h1>
            </div>
            <div class="header-center">
                <a href="index.html" class="nav-btn">🗺️ 地图</a>
                <a href="news.html" class="nav-btn">📰 新闻</a>
                <a href="briefing.html" class="nav-btn">📋 简报</a>
                <a href="tracking.html" class="nav-btn">⚡ 跟踪</a>
                <a href="polymarket_static.html" class="nav-btn active">📈 预测</a>
            </div>
            <div class="header-right" id="updateTime">更新时间: ''' + datetime.now().strftime('%Y-%m-%d %H:%M') + '''</div>
        </div>
    </div>'''

    html = html.replace(old_nav, new_nav)

    # ==================== 添加统一的CSS样式 ====================
    additional_css = '''
    <style>
        /* 统一导航栏样式 */
        .header {
            background: #fff;
            padding: 0;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            border-bottom: 1px solid #e2e8f0;
            position: sticky;
            top: 0;
            z-index: 100;
        }
        .header-main {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 24px;
            max-width: 1200px;
            margin: 0 auto;
        }
        .header-left {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .header-icon {
            font-size: 1.8rem;
            color: #1e40af;
        }
        .header h1 {
            font-size: 1.3rem;
            color: #1e40af;
            font-weight: 600;
        }
        .header-center {
            display: flex;
            gap: 4px;
            background: #e2e8f0;
            padding: 4px;
            border-radius: 8px;
        }
        .nav-btn {
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
        }
        .nav-btn:hover {
            background: rgba(255,255,255,0.5);
            color: #1e40af;
        }
        .nav-btn.active {
            background: #fff;
            color: #1e40af;
            font-weight: 600;
            box-shadow: 0 1px 2px rgba(0,0,0,0.1);
        }
        .header-right {
            font-size: 0.8rem;
            color: #94a3b8;
            background: #f1f5f9;
            padding: 6px 12px;
            border-radius: 6px;
        }

        /* 调整主容器 */
        .max-w-7xl {
            max-width: 1200px !important;
        }

        /* 卡片样式调整 */
        .card {
            background: #fff !important;
            border: 1px solid #e2e8f0 !important;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        }

        /* 移动端适配 */
        @media (max-width: 768px) {
            .header-main {
                flex-wrap: wrap;
                padding: 8px 12px;
            }
            .header-center {
                order: 3;
                width: 100%;
                margin-top: 8px;
                justify-content: center;
            }
            .nav-btn {
                padding: 6px 10px;
                font-size: 0.75rem;
            }
        }
    </style>'''

    # 在 </style> 后添加新样式
    html = html.replace('</style>', additional_css + '</style>')

    # 更新标题
    html = html.replace(
        '<title>Polymarket 伊朗相关预测市场 | 实时追踪</title>',
        '<title>【华泰固收】中东地缘跟踪 - Polymarket预测市场</title>'
    )

    # 保存文件
    try:
        with open("polymarket_static.html", 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"[OK] 已生成: polymarket_static.html")
        return True
    except Exception as e:
        print(f"保存失败: {e}")
        return False


def main():
    print("=" * 60)
    print("转换 polymarket.html 为浅色主题版本")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    if convert_theme():
        print("\n转换完成！")
        print("请在浏览器中打开 polymarket_static.html 查看效果")
    else:
        print("\n转换失败")


if __name__ == "__main__":
    main()
