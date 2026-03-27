import json
data = json.load(open('polymarket_real_data.json', encoding='utf-8'))
print('Events:', list(data.keys()))
midterm = data.get('balance-of-power-2026-midterms', {})
print(f"\nMidterm: {midterm.get('title', 'N/A')}")
for m in midterm.get('markets', []):
    q = m['question']
    prob = m['current_probability']
    hist_len = len(m['history'])
    print(f"  {q}: {prob}% ({hist_len} points)")
