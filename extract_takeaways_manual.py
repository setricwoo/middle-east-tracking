#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动解析HTML提取Key Takeaways
"""
import re
import json
from html import unescape

# 读取之前保存的HTML
with open('isw_report_full.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 移除script和style
content_clean = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
content_clean = re.sub(r'<style[^>]*>.*?</style>', '', content_clean, flags=re.DOTALL)

# 找到Key Takeaways部分
kt_pattern = r'Key Takeaways.*?(?=Toplines|US and Israeli|</article>)'
kt_match = re.search(kt_pattern, content_clean, re.DOTALL | re.IGNORECASE)

if kt_match:
    kt_section = kt_match.group(0)
    print("[找到] Key Takeaways 部分")
    
    # 提取所有段落
    paragraphs = re.findall(r'<p[^>]*>(.*?)</p>', kt_section, re.DOTALL)
    
    takeaways = []
    for p in paragraphs:
        # 清理HTML标签
        text = re.sub(r'<[^>]+>', ' ', p)
        text = unescape(text)
        text = re.sub(r'\s+', ' ', text).strip()
        
        # 过滤有效内容（长度大于100，不是导航文本）
        if len(text) > 100 and 'Skip to' not in text and 'Menu' not in text:
            takeaways.append(text)
    
    print(f"\n[提取] {len(takeaways)} 条Key Takeaways:\n")
    for i, tk in enumerate(takeaways, 1):
        print(f"{i}. {tk[:300]}...\n")
    
    # 保存
    result = {
        'takeaways_en': takeaways,
        'count': len(takeaways)
    }
    
    with open('isw_takeaways_extracted.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"[保存] 已保存到 isw_takeaways_extracted.json")
else:
    print("[错误] 未找到Key Takeaways部分")
