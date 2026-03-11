#!/usr/bin/env python3
"""
将 Polymarket 数据嵌入 HTML 文件
生成一个可以直接双击打开的单文件版本
"""

import json
import re

def build_embedded_html():
    # 读取数据
    try:
        with open('iran_top20.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
    except:
        print("错误: 找不到 iran_top20.json，请先运行 update_polymarket_data.py")
        return
    
    # 读取 HTML 模板
    try:
        with open('polymarket.html', 'r', encoding='utf-8') as f:
            html = f.read()
    except:
        print("错误: 找不到 polymarket.html")
        return
    
    # 将 fetch 代码替换为直接嵌入数据
    json_data = json.dumps(data, ensure_ascii=False)
    
    # 替换 loadMarketData 函数
    old_script = '''    <script>
        // 加载市场数据
        async function loadMarketData() {
            try {
                const response = await fetch('iran_top20.json');
                const data = await response.json();
                
                // 更新时间
                const updateTime = new Date(data.updatedAt);
                document.getElementById('update-time').textContent = updateTime.toLocaleString('zh-CN');
                
                // 渲染市场卡片
                renderMarketCards(data.markets);
                
                // 更新图表
                updateTrendChart(data.markets);
                
            } catch (error) {
                console.error('加载数据失败:', error);
                document.getElementById('market-grid').innerHTML = `
                    <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: #dc2626;">
                        加载数据失败，请稍后刷新重试
                    </div>
                `;
            }
        }'''
    
    new_script = f'''    <script>
        // 嵌入的市场数据（更新时间: {data['updatedAt'][:19]}）
        const EMBEDDED_DATA = {json_data};
        
        // 加载市场数据
        async function loadMarketData() {{
            try {{
                const data = EMBEDDED_DATA;
                
                // 更新时间
                const updateTime = new Date(data.updatedAt);
                document.getElementById('update-time').textContent = updateTime.toLocaleString('zh-CN');
                
                // 渲染市场卡片
                renderMarketCards(data.markets);
                
                // 更新图表
                updateTrendChart(data.markets);
                
            }} catch (error) {{
                console.error('加载数据失败:', error);
                document.getElementById('market-grid').innerHTML = `
                    <div style="grid-column: 1 / -1; text-align: center; padding: 40px; color: #dc2626;">
                        加载数据失败，请稍后刷新重试
                    </div>
                `;
            }}
        }}'''
    
    html = html.replace(old_script, new_script)
    
    # 保存新文件
    output_file = 'polymarket_standalone.html'
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"[OK] 已生成: {output_file}")
    print("特点: 数据已嵌入 HTML，可以直接双击打开，无需服务器")
    print("提示: 重新运行此脚本可更新数据")

if __name__ == '__main__':
    build_embedded_html()
