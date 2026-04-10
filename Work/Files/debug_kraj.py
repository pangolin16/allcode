"""Run: python3 debug_kraj.py"""
import requests, urllib3, json
from collections import Counter
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

r = requests.get("https://data.mpsv.cz/od/soubory/volna-mista/volna-mista.json",
                 timeout=60, verify=False)
items = r.json()["polozky"]

counter = Counter()
samples = {}

for item in items:
    misto = item.get("mistoVykonuPrace") or {}
    for p in (misto.get("pracoviste") or []):
        adresa = (p.get("adresa") or {})
        kraj = adresa.get("kraj")
        if isinstance(kraj, dict):
            kid = kraj.get("id","")
            counter[kid] += 1
            samples[kid] = kraj

print(f"Total kraj values:\n")
for key, count in counter.most_common():
    print(f"  {count:6}x  {key}")

print("\nFull sample objects:")
for key, obj in samples.items():
    print(f"  {json.dumps(obj, ensure_ascii=False)}")
