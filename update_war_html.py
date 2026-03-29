import re
import json

# 读取新数据
with open('new_isw_data.json', 'r', encoding='utf-8') as f:
    new_data = f.read().strip()

# 修复 Windows 反斜杠路径导致的 JSON 问题
data_obj = json.loads(new_data)
for chart in data_obj.get('current_report', {}).get('charts', []):
    if 'screenshot' in chart and chart['screenshot']:
        chart['screenshot'] = chart['screenshot'].replace('\\', '/')

# 重新序列化
new_data = json.dumps(data_obj, ensure_ascii=False, separators=(',', ':'))

# 读取HTML文件
with open('war-situation.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 替换 STATIC_ISW_DATA 的内容
pattern = r'(let STATIC_ISW_DATA = ).*?(;\s*</script>)'
replacement = r'\1' + new_data + r'\2'
new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# 写回文件
with open('war-situation.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Updated successfully!")
print(f"New data has {len(new_data)} characters")

# 验证
with open('war-situation.html', 'r', encoding='utf-8') as f:
    verify = f.read()
    if 'march-28-2026' in verify.lower():
        print("Verification: March 28 data is now in the file")
    else:
        print("Warning: May not have updated correctly")
