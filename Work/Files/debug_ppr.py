"""Run: python3 debug_ppr.py"""
import requests, urllib3, json
from collections import Counter
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

r = requests.get("https://data.mpsv.cz/od/soubory/volna-mista/volna-mista.json",
                 timeout=60, verify=False)
items = r.json()["polozky"]

counter = Counter()
samples = {}

for item in items:
    ppr = item.get("pracovnePravniVztahy") or []
    if not isinstance(ppr, list):
        ppr = [ppr]
    for entry in ppr:
        if isinstance(entry, dict):
            eid   = entry.get("id", "")
            nazev = entry.get("nazev", "")
            key   = f"{eid} | {nazev}"
            counter[key] += 1
            samples[key] = entry

print(f"Total unique pracovnePravniVztahy values:\n")
for key, count in counter.most_common():
    print(f"  {count:6}x  {key}")

print("\nFull sample objects:")
for key, obj in samples.items():
    print(f"  {json.dumps(obj, ensure_ascii=False)}")
