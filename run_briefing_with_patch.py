#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
临时运行update_briefing_grok.py，并在提示词中添加伊朗议会海峡通行费信息
"""

import re
import subprocess
import sys

# 读取原始脚本
with open('update_briefing_grok.py', 'r', encoding='utf-8') as f:
    original_content = f.read()

# 创建修改版本
modified_content = original_content.replace(
    '当前态势：布伦特原油已突破100美元/桶，伊朗向沙特发射导弹，冲突开始外溢，全球能源市场面临供应危机',
    '''当前态势：布伦特原油已突破100美元/桶，伊朗向沙特发射导弹，冲突开始外溢，全球能源市场面临供应危机
- 特别重要动态（必须纳入分析）：伊朗议会已正式批准对通过霍尔木兹海峡的船只征收通行费，作为对美国和以色列制裁的经济反制手段。这一政策标志着伊朗从被动防御转向主动控制全球能源运输咽喉，试图通过"过路费"机制增加谈判筹码并削弱美以经济制裁效果。
- 当前处于深度博弈阶段：双方在军事、经济、外交多条战线展开拉锯，伊朗通过代理人网络、核设施威胁、海峡控制等多重手段增加杠杆；美以则通过精准打击、经济制裁、外交孤立施压。各方都在为可能的谈判积累筹码，但目前仍无实质性对话窗口。'''
)

# 保存修改版本
with open('update_briefing_grok.py', 'w', encoding='utf-8') as f:
    f.write(modified_content)

print("[信息] 已临时添加'伊朗议会海峡通行费'和'深度博弈阶段'提示词")
print("[信息] 正在运行更新脚本...")
print("="*60)

try:
    # 运行修改后的脚本
    result = subprocess.run([sys.executable, 'update_briefing_grok.py'], 
                          capture_output=True, text=True, encoding='utf-8', timeout=180)
    print(result.stdout)
    if result.stderr:
        print("[错误输出]", result.stderr)
finally:
    # 恢复原始脚本
    with open('update_briefing_grok.py', 'w', encoding='utf-8') as f:
        f.write(original_content)
    print("="*60)
    print("[信息] 已恢复原始脚本")
