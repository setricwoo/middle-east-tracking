with open('data-tracking.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Check counts
open_c = content.count('{')
close_c = content.count('}')
print(f'Before: {open_c} open, {close_c} close, diff: {open_c - close_c}')

# Find where to add the closing brace
if open_c > close_c:
    # Find the last </script>
    idx = content.rfind('</script>')
    if idx > 0:
        # Add } before </script>
        content = content[:idx] + '}\n' + content[idx:]
        with open('data-tracking.html', 'w', encoding='utf-8') as f:
            f.write(content)
        print('Added } before </script>')

with open('data-tracking.html', 'r', encoding='utf-8') as f:
    content = f.read()
print(f'After: {content.count("{")} open, {content.count("}")} close')
