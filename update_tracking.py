# -*- coding: utf-8 -*-
import re

with open('tracking.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 更新第一个情报卡片标题
old_title = '伊朗新领袖强确表态：继续封锁海峡'
new_title = '伊朗行动：已击中10余艘商船'

if old_title in content:
    content = content.replace(old_title, new_title)
    print(f'已更新标题: {new_title}')
else:
    print('未找到旧标题')

# 更新第一个情报卡片内容
old_content = '3月12日伊朗新任最高领袖穆杰塔巴·哈梅内伊发表首份声明，强调"封锁霍尔木兹海峡的战略杠杆必须持续运用"，并警告可能"开辟新战线"。美国防长赫格塞思3月13日证实穆杰塔巴在空袭中受伤，可能已经毁容。'
new_content = '2月28日至3月11日，伊朗已在霍尔木兹海峡附近打击了10余艘商船。3月11日，至少三艘货轮被"不明发射物"击中。3月13日伊朗革命卫队向美军第五舰队发起"真实承诺-4"行动，用超重型导弹袭击以色列及美军基地。'

if old_content in content:
    content = content.replace(old_content, new_content)
    print('已更新第一卡片内容')
else:
    print('未找到旧内容')

with open('tracking.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('更新完成')
