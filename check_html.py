with open('data-tracking.html', 'r', encoding='utf-8') as f:
    content = f.read()
print(f'Braces: {content.count("{")} open, {content.count("}")} close')
print(f'Ends correctly: {content.strip().endswith("</html>")}')
print(f'File size: {len(content)} bytes')
