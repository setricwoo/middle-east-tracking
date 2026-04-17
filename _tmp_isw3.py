import requests
urls = [
    'https://understandingwar.org/wp-content/uploads/2026/04/Traffic-Through-the-Strait-of-Hormuz-April-15-2026.webp',
    'https://understandingwar.org/wp-content/uploads/2026/04/Iran-affiliated-Traffic-Through-the-Strait-of-Hormuz-April-15-2026.webp',
    'https://understandingwar.org/wp-content/uploads/2026/04/Hezbollah-Attacks-in-Israel-and-Lebanon-April-15-2026.webp',
    'https://understandingwar.org/wp-content/uploads/2026/04/Lebanon-ISR-Airstikes-April-15-2026.webp',
    'https://understandingwar.org/wp-content/uploads/2026/04/Israeli-Strikes-in-Lebanon-April-15-2026.webp',
]
for u in urls:
    try:
        r = requests.head(u, timeout=10)
        print(f'{r.status_code} {u}')
    except Exception as e:
        print(f'ERR {u} {e}')
