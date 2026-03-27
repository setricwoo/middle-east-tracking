import json
with open('strait_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('=== 海峡数据更新结果 ===')
print(f"更新时间: {data.get('updated', 'N/A')}")
print()

jin10 = data.get('jin10', {})
print('--- 金十数据 ---')
print(f"综合通行压力: {jin10.get('industry_pressure', {}).get('total', 'N/A')}%")
print(f"航行中: {jin10.get('ship_counts', {}).get('sailing', 'N/A')}艘")
print(f"锚泊/停靠: {jin10.get('ship_counts', {}).get('anchored', 'N/A')}艘")
print(f"海域内总计: {jin10.get('ship_counts', {}).get('total_in_area', 'N/A')}艘")
print()

print('--- 视频/图片 ---')
video = jin10.get('video_url', 'N/A')
snapshot = jin10.get('snapshot_url', 'N/A')
print(f"视频URL: {video[:60] if video else 'N/A'}...")
print(f"快照URL: {snapshot[:60] if snapshot else 'N/A'}...")
