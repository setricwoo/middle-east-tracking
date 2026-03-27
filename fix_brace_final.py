with open('data-tracking.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f'Total lines: {len(lines)}')
print('Last 10 lines:')
for i in range(max(0, len(lines)-10), len(lines)):
    print(f'{i+1}: {repr(lines[i])}')

# Find line with just } before </script>
for i in range(len(lines)-1, -1, -1):
    line = lines[i].strip()
    if line == '}':
        print(f'\nFound lone }} at line {i+1}, removing...')
        del lines[i]
        break

with open('data-tracking.html', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('\nFixed!')
