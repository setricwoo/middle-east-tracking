with open('data-tracking.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the pattern } followed by </script>
content = content.replace('});\n}\n</script>', '});\n</script>')
content = content.replace('}\n</script>', '</script>')

with open('data-tracking.html', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed')
print(f'Braces: {content.count("{")} open, {content.count("}")} close')
