import json

with open('isw_war_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

report = data.get('current_report', {})
print('=== V3 测试结果 ===')
print(f"标题: {report.get('title_zh')}")
print(f"Takeaways数量: {len(report.get('takeaways', []))}")
print(f"图表数量: {len(report.get('charts', []))}")
print()

print('--- Takeaways 示例 (前3条) ---')
for i, t in enumerate(report.get('takeaways', [])[:3], 1):
    zh = t.get('zh', '')
    print(f"{i}. {zh[:100]}...")
print()

print('--- 图表示例 (前3张) ---')
for i, c in enumerate(report.get('charts', [])[:3], 1):
    print(f"{i}. {c.get('title_zh')}")
    desc = c.get('description_zh', '')
    if desc:
        print(f"   描述: {desc[:80]}...")
    else:
        print(f"   上下文: {c.get('context', [])}")
    print()
