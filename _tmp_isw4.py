import requests
urls = [
    'https://understandingwar.org/wp-content/uploads/2026/04/Iran-affiliated-Traffic-Through-the-Strait-of-Hormuz-April-15-2026-1024x576.webp',
    'https://understandingwar.org/wp-content/uploads/2026/04/Iran-affiliated-Traffic-Through-the-Strait-of-Hormuz-April-15-2026.webp',
    'https://understandingwar.org/wp-content/uploads/2026/04/Iranian-Linked-Vessels-Transiting-the-Strait-April-15-2026.webp',
    'https://understandingwar.org/wp-content/uploads/2026/04/Iranian-Linked-Vessels-Transiting-the-Strait-April-15-2026-1024x576.webp',
    'https://understandingwar.org/wp-content/uploads/2026/04/Israeli-Strikes-in-Lebanon-Between-April-14-2026-at-200-PM-ET-and-April-15-2026-at-200-PM-ET.webp',
    'https://understandingwar.org/wp-content/uploads/2026/04/Hezbollah-Attacks-in-Israel-and-Lebanon-Between-April-14-2026-at-200-PM-ET-and-April-15-2026-at-200-PM-ET.webp',
]
for u in urls:
    try:
        r = requests.head(u, timeout=10)
        print(f'{r.status_code} {u}')
    except Exception as e:
        print(f'ERR {u} {e}')
