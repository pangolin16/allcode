"""Run: python3 debug_smennost.py"""
import requests, urllib3, json
from collections import Counter
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

r = requests.get("https://data.mpsv.cz/od/soubory/volna-mista/volna-mista.json",
                 timeout=60, verify=False)
items = r.json()["polozky"]

counter = Counter()
samples = {}

for item in items:
    smennost = item.get("smennost")
    if smennost is None:
        key = "None"
        counter[key] += 1
    elif isinstance(smennost, list):
        for entry in smennost:
            if isinstance(entry, dict):
                eid = entry.get("id", "")
                key = eid
                counter[key] += 1
                samples[key] = entry
    elif isinstance(smennost, dict):
        eid = smennost.get("id", "")
        counter[eid] += 1
        samples[eid] = smennost
    else:
        counter[str(smennost)] += 1

print("All smennost values:\n")
for key, count in counter.most_common():
    print(f"  {count:6}x  {key}")

print("\nFull sample objects:")
for key, obj in samples.items():
    print(f"  {json.dumps(obj, ensure_ascii=False)}")
