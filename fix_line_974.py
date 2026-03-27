with open('data-tracking.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Line 974 (index 973) should be </script>
idx = 973  # line 974
if idx < len(lines):
    line = lines[idx]
    print(f'Line 974: {repr(line)}')
    if '}</script>' in line:
        lines[idx] = '</script>\n'
        print('Fixed!')

with open('data-tracking.html', 'w', encoding='utf-8') as f:
    f.writelines(lines)

# Verify
with open('data-tracking.html', 'r', encoding='utf-8') as f:
    content = f.read()
print(f'Braces: {content.count("{")} open, {content.count("}")} close')
