#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import shutil
import subprocess
import sys
import os

# 备份原始文件
shutil.copy('update_briefing_grok.py', 'update_briefing_backup.py')

# 读取并修改
with open('update_briefing_grok.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 添加强制要求
marker = "【参考条目类型（根据最新情况灵活选择，不限于以下）】"
insertion = """【必须包含的关键条目（本次更新强制要求）】
- **伊朗议会批准海峡通行费**：伊朗议会已正式通过对霍尔木兹海峡征收通行费的政策，作为对美以经济反制的核心手段。必须在conflict_progress中添加专门条目，详细分析这一政策的战略意图、实施方式、对全球航运成本的影响，以及美以可能的反制措施。
- **深度博弈阶段特征**：当前冲突已进入深度博弈阶段，双方在经济、军事、外交多条战线展开拉锯。分析各方筹码、博弈均衡点，以及可能打破均衡的触发因素。

"""

if marker in content:
    content = content.replace(marker, insertion + marker)
    
    # 写入修改
    with open('update_briefing_grok.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("[信息] 已添加强制要求：伊朗议会通行费 + 深度博弈")
    print("[信息] 正在运行脚本...")
    print("="*60)
    
    # 运行
    try:
        result = subprocess.run([sys.executable, 'update_briefing_grok.py'], 
                              timeout=180)
    except Exception as e:
        print(f"[错误] {e}")
    
    print("="*60)
    # 恢复
    shutil.copy('update_briefing_backup.py', 'update_briefing_grok.py')
    print("[信息] 已恢复原始脚本")
    
else:
    print("[错误] 未找到标记，无法修改")

# 清理
if os.path.exists('update_briefing_backup.py'):
    os.remove('update_briefing_backup.py')
