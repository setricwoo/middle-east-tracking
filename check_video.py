import json
import re

# 检查HTML中的视频URL
with open('tracking.html', 'r', encoding='utf-8') as f:
    content = f.read()

match = re.search(r'"video_url": "([^"]+)"', content)
if match:
    html_video = match.group(1)
    print(f'HTML中的视频URL: {html_video}')
else:
    html_video = None
    print('未在HTML中找到视频URL')

# 检查JSON中的视频URL
with open('jin10_strait_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

json_video = data.get('video_url')
print(f'JSON中的视频URL: {json_video}')

# 对比
if html_video and json_video:
    if html_video == json_video:
        print('\n✅ 视频URL一致')
    else:
        print('\n❌ 视频URL不一致!')
        print(f'  HTML: {html_video}')
        print(f'  JSON: {json_video}')
