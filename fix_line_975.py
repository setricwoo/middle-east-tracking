with open('data-tracking.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Line 975 (index 974) should be </script> not }\n</script>
idx = 974  # line 975
if idx < len(lines):
    line = lines[idx]
    print(f'Line 975: {repr(line)}')
    if '}</script>' in line or line.strip() == '}':
        lines[idx] = '</script>\n'
        print('Fixed line 975')
    elif '}\n</script>' in line:
        lines[idx] = line.replace('}\n</script>', '</script>')
        print('Fixed line 975 (alternative)')

with open('data-tracking.html', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('Done')
