with open('data-tracking.html', 'r', encoding='utf-8') as f:
    content = f.read()

open_c = content.count('{')
close_c = content.count('}')
diff = open_c - close_c
print(f'Need to add {diff} closing braces')

# Add them before </script>
if diff > 0:
    # Find the last </script> and add braces before it
    idx = content.rfind('</script>')
    if idx > 0:
        braces = '}' * diff
        content = content[:idx] + braces + '\n' + content[idx:]
        with open('data-tracking.html', 'w', encoding='utf-8') as f:
            f.write(content)
        print('Added braces')

# Verify
with open('data-tracking.html', 'r', encoding='utf-8') as f:
    content = f.read()
print(f'After: {content.count("{")} open, {content.count("}")} close')
