import requests, re
url = 'https://understandingwar.org/research/middle-east/iran-update-special-report-april-15-2026/'
headers = {'User-Agent': 'Mozilla/5.0'}
resp = requests.get(url, headers=headers, timeout=30)
imgs = re.findall(r'https://understandingwar[^\s\"\'<>]+\.(?:webp|png|jpg|jpeg)', resp.text)
seen = set()
for img in imgs:
    if img not in seen:
        seen.add(img)
        print(img)
