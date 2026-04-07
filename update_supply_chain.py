#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修改 index.html 的供应链部分，从 supply-chain.json 加载数据
"""

import re

def read_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(filepath, content):
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def replace_supply_chain_section(html_content):
    """替换供应链部分为从JSON加载的动态版本"""
    
    # 找到供应链部分的起始和结束位置
    start_marker = '<!-- 供应链跟踪 -->'
    end_marker = '''        </div>
        
        <style>
        /* 供应链跟踪Tab样式 */'''
    
    start_idx = html_content.find(start_marker)
    end_idx = html_content.find(end_marker)
    
    if start_idx == -1 or end_idx == -1:
        print(f"未找到供应链部分的标记: start={start_idx}, end={end_idx}")
        return html_content
    
    # 新的供应链部分代码
    new_section = '''<!-- 供应链跟踪 -->
        <div class="section" id="supply-chain-section" style="padding: 0; overflow: hidden;">
            <div style="background: linear-gradient(135deg, #1e3a5f 0%, #2d5a87 100%); color: white; padding: 12px 24px; display: flex; justify-content: space-between; align-items: center;">
                <h3 style="margin: 0; font-size: 1rem; color: white;">🔗 供应链跟踪</h3>
                <span style="font-size: 0.75rem; opacity: 0.8;" id="supply-update-time">加载中...</span>
            </div>
            <div style="border-bottom: 1px solid #e2e8f0; background: #f8fafc; padding: 0 16px;">
                <button class="supply-tab active" onclick="switchSupplyTab('energy')">⚡ 能源设施损毁</button>
                <button class="supply-tab" onclick="switchSupplyTab('chain')">🏭 产业链影响</button>
            </div>
            <div class="supply-tab-content active" id="tab-energy" style="padding: 16px;">
                <div class="table-responsive">
                    <table class="supply-table" id="energy-table">
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
                        <tbody id="energy-tbody">
                            <!-- 数据将从 supply-chain.json 加载 -->
                        </tbody>
                    </table>
                </div>
            </div>
            <div class="supply-tab-content" id="tab-chain" style="padding: 16px;">
                <div class="table-responsive">
                    <table class="supply-table" id="chain-table">
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
                        <tbody id="chain-tbody">
                            <!-- 数据将从 supply-chain.json 加载 -->
                        </tbody>
                    </table>
                </div>
            </div>
            <p style="font-size: 0.75rem; color: #64748b; padding: 12px 24px; background: #f8fafc; margin: 0; border-top: 1px solid #e2e8f0;">
                注：本表数据来自 supply-chain.json，红色=已确认不可抗力/停产/关闭。
            </p>
        </div>
        
        
        <!-- 供应链数据加载脚本 -->
        <script>
        (function() {
            // 状态标签样式映射
            const statusClassMap = {
                '受损': 'status-damaged',
                '严重受损': 'status-severe',
                '受损/评估中': 'status-damaged',
                '受损/停产评估中': 'status-damaged',
                '受损/降负': 'status-damaged',
                '受损/起火': 'status-damaged',
                '受损/关闭': 'status-damaged',
                '摧毁': 'status-severe',
                '完全摧毁': 'status-severe',
                '严重损毁': 'status-severe',
                '严重损毁/停产': 'status-severe',
                '暂停运营': 'status-severe',
                '停产': 'status-unknown',
                '关闭': 'status-unknown',
                '关闭/减产': 'status-unknown',
                '关闭/修复中': 'status-unknown',
                '大幅减产': 'status-unknown',
                '降负荷运行': 'status-damaged',
                '火灾中': 'status-severe',
                '大火/损毁': 'status-severe',
                '转移中': 'status-unknown',
                '修复中': 'status-unknown',
                '实质性封锁': 'status-unknown',
                '高危/部分中断': 'status-damaged',
                '威胁中': 'status-unknown',
                '仍处封锁': 'status-unknown',
                '持续交火': 'status-unknown',
                '谈判中': 'status-unknown',
                '反复受损/部分关闭': 'status-damaged',
                '暂时关闭': 'status-damaged',
                '价格飙升': 'status-unknown',
                '供应削减': 'status-unknown',
                '间歇受损': 'status-damaged',
                '多设施受损': 'status-damaged',
                '运行受限': 'status-damaged',
                '吞吐量大幅下降': 'status-unknown'
            };
            
            function getStatusClass(status) {
                if (!status) return 'status-unknown';
                // 如果状态包含某些关键词，返回对应样式
                if (status.includes('受损') || status.includes('损毁') || status.includes('损坏')) return 'status-damaged';
                if (status.includes('严重') || status.includes('摧毁') || status.includes('大火') || status.includes('暂停')) return 'status-severe';
                if (status.includes('停产') || status.includes('关闭') || status.includes('封锁') || status.includes('威胁') || status.includes('转移') || status.includes('修复') || status.includes('减产') || status.includes('谈判') || status.includes('未知')) return 'status-unknown';
                return 'status-unknown';
            }
            
            function renderEnergyTable(data) {
                const tbody = document.getElementById('energy-tbody');
                if (!tbody || !data || !data.energy) {
                    console.error('能源表格或数据不存在');
                    return;
                }
                
                const html = data.energy.map(item => {
                    const statusClass = getStatusClass(item.status);
                    const eventText = Array.isArray(item.event) ? item.event.join('; ') : item.event;
                    return `<tr>
                        <td data-label="日期">${item.date || '-'}</td>
                        <td data-label="国家/地区">${item.region || '-'}</td>
                        <td data-label="设施名称" class="facility-name">${item.facility || '-'}</td>
                        <td data-label="设施类型">${item.type || '-'}</td>
                        <td data-label="所属企业">${item.owner || '-'}</td>
                        <td data-label="事件描述" class="event-desc">${eventText || '-'}</td>
                        <td data-label="当前状态"><span class="status-tag ${statusClass}">${item.status || '-'}</span></td>
                        <td data-label="影响评估">${item.impact || '-'}</td>
                        <td data-label="信息来源">${item.source || '-'}</td>
                    </tr>`;
                }).join('');
                
                tbody.innerHTML = html;
            }
            
            function renderChainTable(data) {
                const tbody = document.getElementById('chain-tbody');
                if (!tbody || !data || !data.chain) {
                    console.error('产业链表格或数据不存在');
                    return;
                }
                
                const html = data.chain.map(item => {
                    return `<tr>
                        <td data-label="日期">${item.date || '-'}</td>
                        <td data-label="国家/地区">${item.region || '-'}</td>
                        <td data-label="企业/机构">${item.company || '-'}</td>
                        <td data-label="行业/产品">${item.industry || '-'}</td>
                        <td data-label="事件描述" class="event-desc">${item.event || '-'}</td>
                        <td data-label="影响传导链">${item.transmission || '-'}</td>
                        <td data-label="停产/减产规模">${item.scale || '-'}</td>
                        <td data-label="对中国影响">${item.chinaImpact || '-'}</td>
                        <td data-label="恢复预期">${item.recovery || '-'}</td>
                        <td data-label="信息来源">${item.source || '-'}</td>
                    </tr>`;
                }).join('');
                
                tbody.innerHTML = html;
            }
            
            function loadSupplyChainData() {
                fetch('supply-chain.json')
                    .then(response => {
                        if (!response.ok) {
                            throw new Error('HTTP ' + response.status);
                        }
                        return response.json();
                    })
                    .then(data => {
                        renderEnergyTable(data);
                        renderChainTable(data);
                        
                        // 更新加载时间
                        const updateTime = document.getElementById('supply-update-time');
                        if (updateTime && data.fetchTime) {
                            const date = new Date(data.fetchTime);
                            updateTime.textContent = '更新: ' + date.toLocaleString('zh-CN');
                        }
                    })
                    .catch(error => {
                        console.error('加载供应链数据失败:', error);
                        const energyTbody = document.getElementById('energy-tbody');
                        const chainTbody = document.getElementById('chain-tbody');
                        const errorMsg = '<tr><td colspan="9" style="text-align:center;color:#dc2626;">数据加载失败，请稍后刷新重试</td></tr>';
                        if (energyTbody) energyTbody.innerHTML = errorMsg;
                        if (chainTbody) chainTbody.innerHTML = '<tr><td colspan="10" style="text-align:center;color:#dc2626;">数据加载失败，请稍后刷新重试</td></tr>';
                    });
            }
            
            // 页面加载完成后加载数据
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', loadSupplyChainData);
            } else {
                loadSupplyChainData();
            }
        })();
        </script>
'''
    
    # 替换旧的部分
    new_content = html_content[:start_idx] + new_section + html_content[end_idx:]
    
    return new_content

def main():
    filepath = r"D:\python_code\海湾以来-最新\index.html"
    
    print("读取 index.html...")
    html_content = read_file(filepath)
    
    print("替换供应链部分...")
    new_content = replace_supply_chain_section(html_content)
    
    print("保存文件...")
    write_file(filepath, new_content)
    
    print("完成！")

if __name__ == "__main__":
    main()
