import json

with open('strait_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print('strait_data.json:')
print(f"  updated: {data.get('updated', 'N/A')}")

jin10 = data.get('jin10', {})
print(f"  航行中: {jin10.get('ship_counts', {}).get('sailing', 'N/A')}")
print(f"  锚泊: {jin10.get('ship_counts', {}).get('anchored', 'N/A')}")
print(f"  压力系数: {jin10.get('industry_pressure', {}).get('total', 'N/A')}")
