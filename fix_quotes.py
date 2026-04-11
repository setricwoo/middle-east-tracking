import re

with open('war-situation.html', 'r', encoding='utf-8') as f:
    content = f.read()

original = content

# 中文左双引号 U+201C -> '
content = content.replace('\u201c', "'")
# 中文右双引号 U+201D -> '
content = content.replace('\u201d', "'")

if content != original:
    with open('war-situation.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Fixed Chinese quotation marks (replaced with single quotes)')
else:
    print('No changes made')
