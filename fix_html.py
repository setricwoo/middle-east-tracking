#!/usr/bin/env python3
"""删除旧的静态数据区域"""
import re

with open('data-tracking.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到所有静态数据区域
pattern = r'/\* STATIC_DATA_START \*/.*?/\* STATIC_DATA_END \*/'

matches = list(re.finditer(pattern, content, re.DOTALL))
print(f"找到 {len(matches)} 个静态数据区域")

if len(matches) >= 2:
    # 删除第二个（body末尾的）
    second_match = matches[1]
    start = second_match.start()
    end = second_match.end()

    # 向前找<script>标签
    script_start = content.rfind('<script>', 0, start)
    # 向后找</script>标签
    script_end = content.find('</script>', end)

    if script_start != -1 and script_end != -1:
        new_content = content[:script_start] + content[script_end + len('</script>'):]
        with open('data-tracking.html', 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"删除了 {script_end + len('</script>') - script_start} 字节")
    else:
        print("未找到script标签")
else:
    print("静态数据区域少于2个，无需删除")
