#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ISW 战事更新抓取器 V3
改进点：
1. 完整提取所有 Key Takeaways（支持多种格式）
2. 提取所有图表（地图、柱状图、折线图等）
3. 图表配文参考正文做解读，不仅标题翻译
"""

import asyncio
import json
import os
import re
import time
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from playwright.async_api import async_playwright

WORKDIR = Path(__file__).parent.resolve()
DATA_FILE = WORKDIR / "isw_data.json"
WAR_DATA_FILE = WORKDIR / "isw_war_data.json"
SCREENSHOT_DIR = WORKDIR / "isw_screenshots"
BEIJING_TZ = ZoneInfo("Asia/Shanghai")

ISW_INDEX_URL = "https://understandingwar.org/backgrounder/iran-updates"
MONTHS_EN = ['january', 'february', 'march', 'april', 'may', 'june', 
             'july', 'august', 'september', 'october', 'november', 'december']

# 扩展术语翻译映射（全面版）
TERM_MAP = {
    # 国家/地区
    'US': '美国', 'USA': '美国', 'United States': '美国',
    'Iran': '伊朗', 'Iranian': '伊朗',
    'Israel': '以色列', 'Israeli': '以色列',
    'UAE': '阿联酋', 'United Arab Emirates': '阿联酋',
    'Saudi Arabia': '沙特阿拉伯',
    'Kuwait': '科威特',
    'Bahrain': '巴林',
    'Qatar': '卡塔尔',
    'Oman': '阿曼',
    'Iraq': '伊拉克',
    'Syria': '叙利亚',
    'Lebanon': '黎巴嫩',
    'Yemen': '也门',
    'Jordan': '约旦',
    'Turkey': '土耳其',
    'Russia': '俄罗斯',
    'China': '中国',
    'UK': '英国', 'United Kingdom': '英国',
    'France': '法国',
    'Germany': '德国',
    
    # 组织/军队
    'CENTCOM': '美国中央司令部',
    'IRGC': '伊斯兰革命卫队',
    'Islamic Revolutionary Guards Corps': '伊斯兰革命卫队',
    'IRGC Ground Force': '伊斯兰革命卫队地面部队',
    'IRGC Navy': '伊斯兰革命卫队海军',
    'IRGC Aerospace Force': '伊斯兰革命卫队航空航天部队',
    'IDF': '以色列国防军',
    'Israel Defense Forces': '以色列国防军',
    'IAF': '以色列空军',
    'Hezbollah': '真主党',
    'Hamas': '哈马斯',
    'Houthi': '胡塞武装',
    'Houthis': '胡塞武装',
    'ISW': '战争研究所',
    'ISW-CTP': '战争研究所-关键威胁项目',
    'CTP': '关键威胁项目',
    'UKMTO': '英国海上贸易行动中心',
    'UN': '联合国',
    'NATO': '北约',
    'EU': '欧盟',
    'combined force': '美以联军',
    'US and Israeli forces': '美以联军',
    'US-Israeli force': '美以联军',
    
    # 领导人
    'Khamenei': '哈梅内伊',
    'Ayatollah Khamenei': '哈梅内伊最高领袖',
    'Ghalibaf': '加利巴夫',
    'Trump': '特朗普',
    'Netanyahu': '内塔尼亚胡',
    'Biden': '拜登',
    'Mojtaba Khamenei': 'Mojtaba 哈梅内伊',
    'Alireza Tangsiri': '阿里雷扎·坦格里西',
    'Tangsiri': '坦格里西',
    
    # 武器装备
    'drone': '无人机',
    'UAV': '无人机',
    'missile': '导弹',
    'ballistic missile': '弹道导弹',
    'cruise missile': '巡航导弹',
    'hypersonic missile': '高超音速导弹',
    'anti-ship missile': '反舰导弹',
    'surface-to-air missile': '防空导弹',
    'SAM': '防空导弹',
    'rocket': '火箭弹',
    'artillery': '火炮',
    'tank': '坦克',
    'fighter jet': '战斗机',
    'warplane': '战机',
    'aircraft': '飞机',
    'carrier': '航母',
    'submarine': '潜艇',
    'warship': '军舰',
    'vessel': '船只',
    'tanker': '油轮',
    'container ship': '集装箱船',
    'cargo ship': '货船',
    'merchant vessel': '商船',
    'feeder tanker': '支线油轮',
    
    # 军事术语
    'strike': '打击',
    'attack': '攻击',
    'target': '目标',
    'launch': '发射',
    'base': '基地',
    'facility': '设施',
    'military': '军事',
    'defense': '防御',
    'retaliatory': '报复性',
    'retaliation': '报复',
    'offensive': '进攻',
    'operation': '行动',
    'maneuver': '演习',
    'deployment': '部署',
    'interception': '拦截',
    'intercepted': '拦截',
    'shot down': '击落',
    'destroyed': '摧毁',
    'damaged': '损坏',
    'disabled': '瘫痪',
    'degraded': '削弱',
    'neutralized': '消灭',
    'casualties': '伤亡',
    'casualty': '伤亡',
    'killed': '死亡',
    'wounded': '受伤',
    'captured': '被俘',
    'surrendered': '投降',
    'evacuated': '撤离',
    'withdrew': '撤退',
    'withdrawal': '撤退',
    'ceasefire': '停火',
    'truce': '休战',
    
    # 地缘政治
    'war': '战争',
    'conflict': '冲突',
    'crisis': '危机',
    'tension': '紧张局势',
    'escalation': '升级',
    'de-escalation': '降级',
    'peace': '和平',
    'negotiation': '谈判',
    'diplomatic': '外交',
    'sanction': '制裁',
    'embargo': '禁运',
    'blockade': '封锁',
    'invasion': '入侵',
    'occupation': '占领',
    'annexation': '吞并',
    'sovereignty': '主权',
    'territory': '领土',
    'airspace': '领空',
    'waters': '水域',
    'border': '边境',
    
    # 地理
    'Gulf': '海湾',
    'Middle East': '中东',
    'Strait of Hormuz': '霍尔木兹海峡',
    'Persian Gulf': '波斯湾',
    'Gulf of Oman': '阿曼湾',
    'Indian Ocean': '印度洋',
    'Red Sea': '红海',
    'Mediterranean': '地中海',
    'Diego Garcia': '迭戈加西亚',
    'Tehran': '德黑兰',
    'Jerusalem': '耶路撒冷',
    'Tel Aviv': '特拉维夫',
    'Beirut': '贝鲁特',
    'Damascus': '大马士革',
    'Baghdad': '巴格达',
    'Riyadh': '利雅得',
    'Abu Dhabi': '阿布扎比',
    'Doha': '多哈',
    'Sanaa': '萨那',
    'Amman': '安曼',
    'Ankara': '安卡拉',
    'Moscow': '莫斯科',
    'Mashhad': '马什哈德',
    'Khorasan Razavi': '呼罗珊·拉扎维省',
    'Khorasan': '呼罗珊',
    'Bandar Abbas': '阿巴斯港',
    'Hormozgan': '霍尔木兹甘省',
    
    # 经济/能源
    'oil': '石油',
    'crude oil': '原油',
    'gas': '天然气',
    'LNG': '液化天然气',
    'LPG': '液化石油气',
    'petroleum': '石油',
    'fuel': '燃料',
    'energy': '能源',
    'shipping': '航运',
    'tanker traffic': '油轮通行',
    'supply chain': '供应链',
    'global market': '全球市场',
    'price': '价格',
    'inflation': '通胀',
    'economy': '经济',
    'trade': '贸易',
    
    # 核相关
    'nuclear': '核',
    'uranium': '铀',
    'enrichment': '浓缩',
    'nuclear program': '核计划',
    'nuclear facility': '核设施',
    'nuclear weapon': '核武器',
    'atomic': '原子',
    'radioactive': '放射性',
    
    # 情报/侦察
    'intelligence': '情报',
    'surveillance': '监视',
    'reconnaissance': '侦察',
    'satellite': '卫星',
    'radar': '雷达',
    'air defense system': '防空系统',
    'missile defense': '导弹防御',
    'early warning': '预警',
    'command and control': '指挥控制',
    
    # 设施
    'headquarters': '总部',
    'compound': '大院',
    'barracks': '营房',
    'depot': '仓库',
    'arsenal': '军火库',
    'airfield': '机场',
    'port': '港口',
    'naval base': '海军基地',
    'military base': '军事基地',
    'production site': '生产基地',
    'industrial site': '工业设施',
    'research facility': '研究设施',
    
    # 动词/动作
    'reported': '据报道',
    'claimed': '声称',
    'confirmed': '确认',
    'denied': '否认',
    'announced': '宣布',
    'stated': '表示',
    'added': '补充说',
    'noted': '指出',
    'emphasized': '强调',
    'warned': '警告',
    'threatened': '威胁',
    'pledged': '承诺',
    'vowed': '发誓',
    'continued': '继续',
    'resumed': '恢复',
    'expanded': '扩大',
    'increased': '增加',
    'decreased': '减少',
    'maintained': '保持',
    'conducted': '进行',
    'carried out': '执行',
    'initiated': '发起',
    'prepared': '准备',
    'began': '开始',
    'started': '开始',
    'ended': '结束',
    'completed': '完成',
    
    # 状态/描述
    'ongoing': '正在进行',
    'active': '活跃',
    'intense': '激烈',
    'severe': '严重',
    'critical': '关键',
    'strategic': '战略',
    'tactical': '战术',
    'significant': '重大',
    'substantial': '大量',
    'limited': '有限',
    'partial': '部分',
    'complete': '完全',
    'total': '总计',
    'effective': '有效',
    'successful': '成功',
    'unsuccessful': '失败',
    
    # 常见短语
    'according to': '根据',
    'based on': '基于',
    'in response to': '作为对...的回应',
    'in order to': '为了',
    'as well as': '以及',
    'in addition to': '除...之外',
    'due to': '由于',
    'because of': '因为',
    'as a result': '结果',
    'therefore': '因此',
    'however': '然而',
    'meanwhile': '与此同时',
    'furthermore': '此外',
    'moreover': '而且',
    'nevertheless': '尽管如此',
    'although': '虽然',
    'despite': '尽管',
    'instead': '反而',
    'otherwise': '否则',
    'for example': '例如',
    'such as': '例如',
    'including': '包括',
    'excluding': '不包括',
}


def apply_term_translation(text):
    """应用术语翻译"""
    if not text:
        return text
    result = text
    for en, zh in sorted(TERM_MAP.items(), key=lambda x: -len(x[0])):
        result = re.sub(r'\b' + re.escape(en) + r'\b', zh, result, flags=re.IGNORECASE)
    return result


def post_process_translation(text):
    """翻译后处理，修正常见错误（增强版）"""
    if not text:
        return text
    
    # 修正常见的翻译错误
    corrections = {
        # 修正不自然的被动表达
        '被击落': '击落',
        '被摧毁': '摧毁',
        '被损坏': '损坏',
        '被拦截': '拦截',
        '被发射': '发射',
        '被攻击': '遭袭',
        '被打击': '遭打击',
        '被袭击': '遭袭',
        '被瞄准': '被锁定',
        '被针对': '针对',
        
        # 修正语序问题
        '和以色列美国': '美国和以色列',
        '和美国以色列': '美国和以色列',
        '伊朗和以色列美国': '伊朗、以色列和美国',
        '美国伊朗': '美国和伊朗',
        '伊朗以色列': '伊朗和以色列',
        '以色列伊朗': '以色列和伊朗',
        
        # 修正重复
        '美国美国': '美国',
        '伊朗伊朗': '伊朗',
        '以色列以色列': '以色列',
        '伊斯兰革命卫队伊斯兰革命卫队': '伊斯兰革命卫队',
        
        # 修正标点
        ' ,': '，',
        ' .': '。',
        ' ;': '；',
        ' :': '：',
        ' ?': '？',
        ' !': '！',
        
        # 修正量词
        '一个导弹': '一枚导弹',
        '一个无人机': '一架无人机',
        '一个火箭': '一枚火箭',
        '一个基地': '一处基地',
        '一个设施': '一处设施',
        '一个营地': '一处营地',
        '一个指挥中心': '一处指挥中心',
        
        # 修正军事术语
        '联合部队': '美以联军',
        'combined force': '美以联军',
        '罢工': '打击',
        '罢工战争': '战争中的打击行动',
        '战争中的打击': '战争中的打击行动',
        '东北': '东北方向',
        '北部以色列': '以色列北部',
        '南部以色列': '以色列南部',
        '北以色列部': '以色列北部',
        '南以色列部': '以色列南部',
        '黎巴嫩南部': '黎巴嫩南部',
        '南黎巴嫩': '黎巴嫩南部',
        
        # 修正动词
        '进行袭击': '发动袭击',
        '进行打击': '实施打击',
        '宣布日': '宣布',
        '声称': '宣称',
        
        # 修正组织名
        '公司伊斯兰革命卫队': '伊斯兰革命卫队',
        '政府已将': '已将',
        '伊斯兰革命卫队政府': '伊斯兰革命卫队',
        
        # 修正人名地名
        'Alireza Tangsiri': '阿里雷扎·坦格里西',
        'Bandar Abbas': '阿巴斯港',
        'Mashhad': '马什哈德',
        'Khorasan Razavi': '呼罗珊·拉扎维',
        
        # 修正时间表达
        '下午2点': '14:00',
        '下午2点至': '14:00至',
        
        # 修正其他
        '很高的黎巴嫩': '很高的',
        '袭击率': '袭击频率',
        '运营中断': '行动中断',
        
        # 修正军事术语
        '做了打击': '实施打击',
        '做了攻击': '发动攻击',
        '做了回应': '作出回应',
        
        # 修正时间表达
        '在3月': '3月',
        '在2026年': '2026年',
        '在星期': '星期',
        
        # 修正介词
        '针对对': '针对',
        '关于于': '关于',
        
        # 修正其他
        '等等': '等',
        '等等等等': '等',
        '省省': '省',
        '宣称至': '宣称，截至',
        '死亡伊斯兰革命卫队': '击毙伊斯兰革命卫队',
        '它死亡': '击毙',
        '继续有针对': '继续针对',
        '的干扰': '，以干扰',
        '3以色列国防军宣布月26日': '以色列国防军3月26日宣布',
        '3月26黎巴嫩日': '3月26日',
        '对以及': '对',
        '以色列南部目标的袭击频率很高黎巴嫩': '以色列南部和黎巴嫩南部目标的袭击频率很高',
    }
    
    for wrong, correct in corrections.items():
        text = text.replace(wrong, correct)
    
    # 修正连续标点
    text = re.sub(r'[，,]+', '，', text)
    text = re.sub(r'[。.]+', '。', text)
    text = re.sub(r'[;；]+', '；', text)
    
    # 修正空格（中文中不应该有空格）
    text = re.sub(r'([\u4e00-\u9fa5])\s+([\u4e00-\u9fa5])', r'\1\2', text)
    
    return text.strip()


def translate_text(text):
    """翻译英文到中文（带后处理）"""
    if not text or not text.strip():
        return text
    
    text = text.strip()
    
    # 短文本直接术语翻译，不调用API
    if len(text) < 80:
        result = apply_term_translation(text)
        return post_process_translation(result)
    
    # 先应用术语翻译
    text = apply_term_translation(text)
    
    max_len = 500
    if len(text) > max_len:
        # 按句子分割，保持上下文
        sentences = text.replace('. ', '.|').replace('! ', '!|').replace('? ', '?|').split('|')
        translated_parts = []
        current_chunk = ""
        
        for sent in sentences:
            if len(current_chunk) + len(sent) > max_len:
                if current_chunk:
                    # 翻译前先进行术语翻译
                    chunk_to_translate = apply_term_translation(current_chunk)
                    result = _translate_api(chunk_to_translate)
                    result = apply_term_translation(result)  # 再次确保术语正确
                    result = post_process_translation(result)  # 后处理
                    translated_parts.append(result)
                current_chunk = sent
            else:
                current_chunk += " " + sent if current_chunk else sent
        
        if current_chunk:
            chunk_to_translate = apply_term_translation(current_chunk)
            result = _translate_api(chunk_to_translate)
            result = apply_term_translation(result)
            result = post_process_translation(result)
            translated_parts.append(result)
        
        result = " ".join(translated_parts)
    else:
        result = _translate_api(text)
        result = apply_term_translation(result)
        result = post_process_translation(result)
    
    return result


def _translate_api(text):
    """调用 MyMemory API 翻译"""
    for attempt in range(2):
        try:
            encoded = urllib.parse.quote(text[:500])
            url = f"https://api.mymemory.translated.net/get?q={encoded}&langpair=en|zh-CN"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}, method='GET')
            res = json.loads(urllib.request.urlopen(req, timeout=10).read())
            if res.get("responseStatus") == 200:
                translated = res["responseData"]["translatedText"]
                if "MYMEMORY WARNING" not in translated:
                    return translated
        except Exception:
            if attempt < 1:
                time.sleep(1)
    return text


def clean_title(title):
    """清理标题 - 改进版"""
    if not title:
        return title
    
    months = ['January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'September', 'October', 'November', 'December']
    result = title
    
    # 翻译标题关键词
    result = re.sub(r'\bIran Update\b', '伊朗局势更新', result, flags=re.IGNORECASE)
    result = re.sub(r'\bSpecial Report\b', '特别报告', result, flags=re.IGNORECASE)
    
    # 转换日期格式 "March 26, 2026" -> "2026年3月26日"
    for i, month in enumerate(months, 1):
        # 匹配 "March 26, 2026" 或 "March 26 2026"
        pattern = r'\b' + month + r'\s+(\d{1,2}),?\s*(\d{4})\b'
        def replace_date(m):
            day = m.group(1)
            year = m.group(2)
            return f'{year}年{i}月{day}日'
        result = re.sub(pattern, replace_date, result, flags=re.IGNORECASE)
    
    # 清理多余空格和逗号
    result = re.sub(r'\s*,\s*', ' ', result)
    result = re.sub(r'\s+', ' ', result)
    
    return result.strip()


def parse_date(url):
    """从URL解析日期"""
    match = re.search(r'(january|february|march|april|may|june|july|august|september|october|november|december)-(\d{1,2})-(\d{4})', url.lower())
    if match:
        month_name, day, year = match.groups()
        month_num = MONTHS_EN.index(month_name) + 1
        return f"{year}-{month_num:02d}-{int(day):02d}"
    return datetime.now(BEIJING_TZ).strftime("%Y-%m-%d")


# ========== V3 改进：提取所有 Takeaways（支持多种格式）==========

async def extract_takeaways_v3(page):
    """V3: 完整提取 Key Takeaways，支持多种格式"""
    return await page.evaluate("""
        () => {
            const results = [];
            
            // 1. 标准格式：找 Key Takeaways 标题后的列表
            const allElements = Array.from(document.querySelectorAll('*'));
            for (let i = 0; i < allElements.length; i++) {
                const el = allElements[i];
                const text = el.textContent.trim();
                
                // 匹配各种 takeaway 标题变体
                if (/^(key\s+takeaway|key\s+points|highlights|executive\s+summary|summary)/i.test(text)) {
                    console.log('Found takeaway heading:', text);
                    
                    // 方法1：找直接相邻的列表
                    let nextEl = el.nextElementSibling;
                    while (nextEl) {
                        if (nextEl.tagName === 'OL' || nextEl.tagName === 'UL') {
                            const items = Array.from(nextEl.querySelectorAll(':scope > li'))
                                .map(li => li.textContent.trim())
                                .filter(t => t.length > 10);
                            if (items.length > 0) {
                                console.log('Found list with', items.length, 'items');
                                results.push(...items);
                                return results;
                            }
                        }
                        if (nextEl.tagName.match(/^H[1-6]$/)) break;
                        nextEl = nextEl.nextElementSibling;
                    }
                    
                    // 方法2：找父容器内的所有列表项
                    const parent = el.closest('div, section, article, .field-item');
                    if (parent) {
                        // 先找直接子列表
                        let lists = parent.querySelectorAll(':scope > ol, :scope > ul');
                        if (lists.length === 0) {
                            // 再找嵌套列表
                            lists = parent.querySelectorAll('ol, ul');
                        }
                        
                        for (const list of lists) {
                            // 确保列表在标题之后
                            if (el.compareDocumentPosition(list) & Node.DOCUMENT_POSITION_FOLLOWING) {
                                const items = Array.from(list.querySelectorAll(':scope > li'))
                                    .map(li => li.textContent.trim())
                                    .filter(t => t.length > 10 && t.length < 2000);
                                if (items.length > 0) {
                                    console.log('Found parent list with', items.length, 'items');
                                    results.push(...items);
                                    if (results.length >= 2) return results;
                                }
                            }
                        }
                    }
                }
            }
            
            // 2. 回退：找文章开头的第一个有序列表（通常是takeaways）
            if (results.length === 0) {
                const contentSelectors = [
                    '.entry-content ol',
                    '.post-content ol', 
                    'article ol',
                    '.field-item ol',
                    '#main-content ol',
                    '.content ol'
                ];
                
                for (const selector of contentSelectors) {
                    const ol = document.querySelector(selector);
                    if (ol) {
                        // 获取所有列表项（包括嵌套列表的项）
                        const allItems = [];
                        const directItems = ol.querySelectorAll(':scope > li');
                        
                        for (const li of directItems) {
                            const text = li.textContent.trim();
                            // 清理多余空白
                            const cleanText = text.replace(/\s+/g, ' ');
                            if (cleanText.length > 20 && cleanText.length < 1500) {
                                allItems.push(cleanText);
                            }
                        }
                        
                        if (allItems.length > 0) {
                            console.log('Fallback: found ol with', allItems.length, 'items');
                            results.push(...allItems);
                            break;
                        }
                    }
                }
            }
            
            // 3. 最终回退：找任何包含 "Iran" 或 "strike" 的列表项
            if (results.length === 0) {
                const allLists = document.querySelectorAll('ol li, ul li');
                for (const li of allLists) {
                    const text = li.textContent.trim();
                    if (/iran|strike|attack|missile|military/i.test(text) && 
                        text.length > 30 && text.length < 1000) {
                        results.push(text);
                        if (results.length >= 10) break;
                    }
                }
            }
            
            // 去重并返回
            const unique = [];
            const seen = new Set();
            for (const item of results) {
                const key = item.substring(0, 50);
                if (!seen.has(key)) {
                    seen.add(key);
                    unique.push(item);
                }
            }
            
            return unique.slice(0, 20);
        }
    """)


# ========== V3 改进：提取所有图表类型 ==========

async def extract_all_charts_v3(page, article_date):
    """V3: 提取所有图表，只截取图片本身（无留白）"""
    SCREENSHOT_DIR.mkdir(exist_ok=True)
    captured = []
    
    # 获取所有图片元素
    images_data = await page.evaluate("""
        () => {
            const results = [];
            const imgs = document.querySelectorAll('img');
            const year = new Date().getFullYear().toString();
            
            imgs.forEach((img, idx) => {
                const src = img.src || '';
                if (!src.includes('wp-content/uploads')) return;
                if (!src.includes(year)) return;
                
                // 排除非图表图片
                const exclude = /headshot|avatar|author|profile|logo|babel|print|icon|button|social/i;
                if (exclude.test(src)) return;
                
                // V3: 扩展图表检测
                const isChart = /map|chart|strike|launch|iran|israel|saudi|bahrain|uae|hezbollah|graph|plot|diagram|timeline|assessment|damage/i.test(src);
                if (!isChart) return;
                
                const rect = img.getBoundingClientRect();
                if (rect.width < 250 || rect.height < 150) return;
                
                // V3: 获取更丰富的上下文（前后段落）
                let contextBefore = [];
                let contextAfter = [];
                let captionText = '';
                
                // 找图片标题/说明
                const figure = img.closest('figure');
                if (figure) {
                    const caption = figure.querySelector('figcaption');
                    if (caption) captionText = caption.textContent.trim();
                }
                
                // 找前面的段落文本（最多3段）
                let prevEl = img.previousElementSibling;
                let count = 0;
                while (prevEl && count < 3) {
                    if (prevEl.tagName === 'P' && prevEl.textContent.trim().length > 20) {
                        contextBefore.unshift(prevEl.textContent.trim());
                        count++;
                    }
                    prevEl = prevEl.previousElementSibling;
                }
                
                // 找后面的段落文本（最多2段）
                let nextEl = img.nextElementSibling;
                count = 0;
                while (nextEl && count < 2) {
                    if (nextEl.tagName === 'P' && nextEl.textContent.trim().length > 20) {
                        contextAfter.push(nextEl.textContent.trim());
                        count++;
                    }
                    nextEl = nextEl.nextElementSibling;
                }
                
                results.push({
                    index: idx,
                    src: src,
                    alt: img.alt || '',
                    caption: captionText,
                    contextBefore: contextBefore,
                    contextAfter: contextAfter,
                    width: rect.width,
                    height: rect.height,
                    top: rect.top + window.scrollY,
                    left: rect.left + window.scrollX,
                    viewportTop: rect.top,
                    viewportLeft: rect.left,
                });
            });
            
            return results;
        }
    """)
    
    print(f"[发现] {len(images_data)} 张图表")
    
    for idx, img_data in enumerate(images_data):
        try:
            safe_name = f"chart_{article_date}_{idx:02d}.png"
            screenshot_path = SCREENSHOT_DIR / safe_name
            
            # 滚动到图片位置并等待
            await page.evaluate(f"window.scrollTo(0, {img_data['top'] - 100})")
            await asyncio.sleep(1.5)
            
            # 重新获取图片位置（滚动后可能变化）
            updated_rect = await page.evaluate(f"""
                () => {{
                    const imgs = document.querySelectorAll('img');
                    let target = null;
                    for (let img of imgs) {{
                        if (img.src === '{img_data['src']}') {{
                            target = img;
                            break;
                        }}
                    }}
                    if (!target) return null;
                    const rect = target.getBoundingClientRect();
                    return {{
                        x: rect.left,
                        y: rect.top,
                        width: rect.width,
                        height: rect.height
                    }};
                }}
            """)
            
            if not updated_rect or updated_rect['width'] < 100:
                print(f"  [跳过] 图片 {idx} 不在可视区域")
                continue
            
            # 确保坐标在有效范围内
            viewport = page.viewport_size
            viewport_width = viewport['width']
            viewport_height = viewport['height']
            if updated_rect['y'] < 0 or updated_rect['y'] > viewport_height:
                # 再次滚动
                await page.evaluate(f"window.scrollBy(0, {updated_rect['y'] - 50})")
                await asyncio.sleep(0.5)
                updated_rect = await page.evaluate(f"""
                    () => {{
                        const imgs = document.querySelectorAll('img');
                        let target = null;
                        for (let img of imgs) {{
                            if (img.src === '{img_data['src']}') {{
                                target = img;
                                break;
                            }}
                        }}
                        if (!target) return null;
                        const rect = target.getBoundingClientRect();
                        return {{
                            x: Math.max(0, rect.left),
                            y: Math.max(0, rect.top),
                            width: rect.width,
                            height: rect.height
                        }};
                    }}
                """)
                if not updated_rect:
                    continue
            
            # V3改进：只截取图片本身
            clip = {
                'x': max(0, updated_rect['x']),
                'y': max(0, updated_rect['y']),
                'width': min(updated_rect['width'], viewport_width - max(0, updated_rect['x'])),
                'height': min(updated_rect['height'], viewport_height - max(0, updated_rect['y']))
            }
            
            if clip['width'] < 100 or clip['height'] < 100:
                print(f"  [跳过] 图片 {idx} 裁剪区域太小")
                continue
            
            await page.screenshot(
                path=str(screenshot_path),
                clip=clip,
                full_page=False
            )
            
            if screenshot_path.exists() and screenshot_path.stat().st_size > 15000:
                # V3: 生成更丰富的图表信息
                info = generate_chart_info_v3(img_data)
                
                captured.append({
                    'original_url': img_data['src'],
                    'screenshot': str(screenshot_path.relative_to(WORKDIR)).replace('\\', '/'),
                    'title_zh': info['title'],
                    'description_zh': info['description'],
                    'full_analysis': info['full_analysis'],
                    'context': info['tags'],
                    'caption_en': img_data['caption'],
                })
                print(f"  [截图] {safe_name} ({img_data['width']:.0f}x{img_data['height']:.0f}) - {info['title']}")
            else:
                screenshot_path.unlink(missing_ok=True)
                
        except Exception as e:
            print(f"  [失败] 截图 {idx}: {e}")
    
    return captured


def generate_chart_info_v3(img_data):
    """V3: 生成丰富的图表标题和描述"""
    src = img_data['src'].lower()
    alt = img_data['alt'].lower()
    caption = img_data['caption']
    context_before = img_data.get('contextBefore', [])
    context_after = img_data.get('contextAfter', [])
    
    # 图表类型检测
    chart_types = {
        'map': '态势地图',
        'bar': '数据统计图',
        'chart-bar': '数据统计图',
        'line': '趋势分析图',
        'graph': '趋势分析图',
        'timeline': '时间线图',
        'pie': '比例分析图',
        'strike': '军事打击示意图',
        'launch': '发射行动示意图',
        'damage': '损坏评估分析图',
    }
    
    chart_type = '分析图表'
    for key, value in chart_types.items():
        if key in src or key in alt:
            chart_type = value
            break
    
    # 主题检测（扩展更多主题）
    themes = {
        'diego garcia': ('迭戈加西亚基地打击', ['印度洋战区', '战略打击', '导弹袭击']),
        'us-and-israeli': ('美以联军行动', ['美以联军', '伊朗境内', '军事打击', '战略目标']),
        'iranian-and-axis': ('伊朗及盟友行动', ['伊朗军事', '报复打击', '地区冲突', '代理人战争']),
        'saudi': ('沙特方向威胁', ['沙特阿拉伯', '导弹威胁', '地区安全']),
        'bahrain': ('巴林方向威胁', ['巴林', '导弹威胁', '海湾国家']),
        'uae': ('阿联酋方向威胁', ['阿联酋', '导弹威胁', '能源设施']),
        'hezbollah': ('真主党袭击', ['黎巴嫩', '真主党', '对以袭击', '北部边境']),
        'ground force': ('地面部队部署', ['伊朗陆军', '地面部署', '边境态势']),
        'air defense': ('防空系统布局', ['防空', '导弹拦截', '雷达覆盖']),
        'nuclear': ('核设施分布', ['核计划', '浓缩铀', '国际关注']),
        'oil': ('石油设施安全', ['石油', '能源设施', '经济命脉']),
        'infrastructure': ('基础设施目标', ['关键设施', '战略目标', '工业基础']),
        'hormuz': ('霍尔木兹海峡', ['海上通道', '航运安全', '战略水道']),
        'red sea': ('红海航线', ['航运危机', '胡塞武装', '国际贸易']),
    }
    
    theme_title = '战场态势'
    theme_tags = ['ISW战略分析']
    
    for key, (title, tags) in themes.items():
        if key in src or key in alt or (caption and key in caption.lower()):
            theme_title = title
            theme_tags = tags
            break
    
    # 生成详细描述
    description = generate_rich_description(chart_type, theme_title, caption, context_before, context_after)
    
    return {
        'title': f"{theme_title}{chart_type}",
        'description': description['brief'],
        'full_analysis': description['full'],
        'tags': theme_tags,
    }


def generate_rich_description(chart_type, theme, caption, context_before, context_after):
    """生成丰富的图表描述，包括简要版和完整分析版"""
    
    # 整合所有上下文
    all_context = context_before + context_after
    
    # 翻译caption
    caption_zh = ''
    if caption and len(caption) > 10:
        caption_zh = translate_text(caption)
    
    # 翻译关键上下文（选择最相关的段落）
    context_parts = []
    for ctx in all_context[:2]:  # 最多取2段
        if len(ctx) > 30:
            # 提取关键信息
            keywords = ['iran', 'israel', 'strike', 'attack', 'missile', 'military', 
                       'damage', 'destroyed', 'launch', 'base', 'force', 'operation']
            if any(k in ctx.lower() for k in keywords):
                translated = translate_text(ctx[:300])  # 限制长度
                context_parts.append(translated)
    
    # 简要描述（用于列表展示）
    brief_parts = []
    if caption_zh and len(caption_zh) > 10:
        brief_parts.append(caption_zh[:150])
    elif context_parts:
        brief_parts.append(context_parts[0][:150])
    else:
        brief_parts.append(f"ISW发布的{chart_type}，展示{theme}相关战略态势")
    
    brief = ' | '.join(brief_parts)
    
    # 完整分析（用于详情弹窗）
    full_analysis = []
    
    # 添加标题
    full_analysis.append(f"【{theme}分析】")
    
    # 添加说明
    if caption_zh:
        full_analysis.append(f"\n图表说明：{caption_zh}")
    
    # 添加背景信息
    if context_parts:
        full_analysis.append(f"\n背景信息：")
        for i, part in enumerate(context_parts[:2], 1):
            full_analysis.append(f"{i}. {part}")
    
    # 添加分析要点
    full_analysis.append(f"\n战略要点：")
    full_analysis.append(f"• 该{chart_type.replace('图', '')}反映了当前{theme}的实时态势")
    full_analysis.append(f"• 数据来源：ISW（战争研究所）基于公开情报分析")
    full_analysis.append(f"• 更新时间：{datetime.now(BEIJING_TZ).strftime('%Y年%m月%d日')}")
    
    return {
        'brief': brief,
        'full': '\n'.join(full_analysis)
    }


# ========== 其他辅助函数 ==========

async def find_article_url(page):
    """查找最新文章URL"""
    now = datetime.now(BEIJING_TZ)
    
    for days_back in range(7):
        d = now - timedelta(days=days_back)
        month = MONTHS_EN[d.month - 1]
        url = f"https://understandingwar.org/backgrounder/iran-update-special-report-{month}-{d.day}-{d.year}"
        
        for candidate in [url, url + "/"]:
            try:
                resp = await page.goto(candidate, wait_until="domcontentloaded", timeout=15000)
                if resp and resp.status < 400:
                    length = await page.evaluate("document.body.innerText.length")
                    if length > 1000:
                        return candidate
            except:
                pass
        await asyncio.sleep(0.3)
    
    try:
        await page.goto(ISW_INDEX_URL, wait_until="domcontentloaded", timeout=30000)
        await asyncio.sleep(2)
        return await page.evaluate("""
            () => {
                const links = Array.from(document.querySelectorAll('a[href]'));
                for (const a of links) {
                    if (/iran-update.*20\\d\\d/.test(a.href)) return a.href;
                }
                return null;
            }
        """)
    except:
        return None


async def fetch_isw_v3():
    """V3 主抓取函数"""
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1400, "height": 900},
            ignore_https_errors=True,
        )
        await context.add_init_script("Object.defineProperty(navigator,'webdriver',{get:()=>undefined})")
        page = await context.new_page()
        
        print("[查找] 最新文章...")
        url = await find_article_url(page)
        if not url:
            print("[错误] 未找到文章")
            await browser.close()
            return None
        
        print(f"[找到] {url}")
        
        await page.goto(url, wait_until="load", timeout=45000)
        await asyncio.sleep(3)
        
        date = parse_date(url)
        
        title = await page.evaluate("""
            () => {
                const h1 = document.querySelector('h1.entry-title, h1.post-title, h1');
                return h1 ? h1.textContent.trim() : document.title.split('|')[0].trim();
            }
        """)
        
        # V3: 提取所有 Takeaways
        print("[提取] Key Takeaways (V3)...")
        takeaways_en = await extract_takeaways_v3(page)
        print(f"[提取] {len(takeaways_en)} 条")
        
        # 翻译
        print("[翻译] 内容...")
        takeaways = []
        for text in takeaways_en:
            zh = translate_text(text)
            takeaways.append({"en": text, "zh": zh})
            time.sleep(0.2)
        
        # V3: 提取所有图表
        print("[截图] 所有图表 (V3)...")
        charts = await extract_all_charts_v3(page, date)
        print(f"[截图] {len(charts)} 张")
        
        await browser.close()
        
        return {
            "url": url,
            "title": title,
            "title_zh": clean_title(title),
            "date": date,
            "takeaways": takeaways,
            "charts": charts,
        }


def save_v3(data):
    """V3 保存数据"""
    now = datetime.now(BEIJING_TZ)
    
    existing = {"updated": "", "articles": []}
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except:
            pass
    
    record = {
        **data,
        "fetched": now.strftime("%Y-%m-%dT%H:%M:%S"),
        "takeaways_en": [t["en"] for t in data["takeaways"]],
        "takeaways_zh": [t["zh"] for t in data["takeaways"]],
    }
    
    articles = [a for a in existing.get("articles", []) if a["url"] != data["url"]]
    articles.insert(0, record)
    existing["articles"] = articles[:30]
    existing["updated"] = now.strftime("%Y-%m-%dT%H:%M:%S")
    
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    
    # V3: war-situation 格式，包含描述
    war_data = {
        "updated": now.isoformat(),
        "source_url": data["url"],
        "current_report": {
            "url": data["url"],
            "title": data["title"],
            "title_zh": data["title_zh"],
            "date": data["date"],
            "takeaways": data["takeaways"],
            "charts": [
                {
                    "url": c["screenshot"],
                    "title": "",
                    "title_zh": c["title_zh"],
                    "description_zh": c.get("description_zh", ""),
                    "context": c.get("context", []),
                }
                for c in data["charts"]
            ],
        },
        "history": [
            {
                "date": a.get("date", ""),
                "title": a.get("title", ""),
                "title_zh": clean_title(a.get("title", "")),
                "url": a.get("url", ""),
            }
            for a in articles[1:4]
        ],
    }
    
    with open(WAR_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(war_data, f, ensure_ascii=False, indent=2)
    
    print(f"[保存] {DATA_FILE}")
    print(f"[保存] {WAR_DATA_FILE}")
    
    # V3 新增：嵌入数据到 war-situation.html
    embed_data_to_html(war_data)


def embed_data_to_html(war_data):
    """将数据嵌入 war-situation.html"""
    html_file = WORKDIR / "war-situation.html"
    
    try:
        with open(html_file, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 准备嵌入的JSON数据（压缩格式）
        json_data = json.dumps(war_data, ensure_ascii=False, separators=(',', ':'))
        
        # 使用字符串分割安全替换（避免正则特殊字符问题）
        start_marker = 'let STATIC_ISW_DATA = '
        end_marker = ';'
        
        start_idx = content.find(start_marker)
        if start_idx != -1:
            # 找到JSON数据的起始位置
            data_start = start_idx + len(start_marker)
            # 找到结束的分号（考虑嵌套大括号）
            brace_count = 0
            data_end = data_start
            for i, char in enumerate(content[data_start:]):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        data_end = data_start + i + 1
                        break
            
            # 替换数据部分
            new_content = content[:data_start] + json_data + content[data_end:]
            
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(new_content)
            
            print(f"[嵌入] 数据已嵌入 {html_file}")
        else:
            print(f"[警告] 未找到 STATIC_ISW_DATA 变量，请确保HTML文件包含该变量")
            
    except Exception as e:
        print(f"[错误] 嵌入HTML失败: {e}")


async def main():
    print("=" * 60)
    print("ISW 战事更新抓取器 V3")
    print("改进：完整提取Takeaways + 所有图表类型 + 正文解读")
    print("=" * 60)
    
    data = await fetch_isw_v3()
    if data:
        save_v3(data)
        print(f"\n[完成] {data['title_zh']}")
        print(f"  日期: {data['date']}")
        print(f"  Takeaways: {len(data['takeaways'])}")
        print(f"  图表: {len(data['charts'])}")
        for c in data['charts'][:5]:
            print(f"    - {c['title_zh']}")
    else:
        print("[失败]")
    
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
