"""Run this on your machine: python3 debug_loc.py"""
import requests, urllib3, json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

r = requests.get("https://data.mpsv.cz/od/soubory/volna-mista/volna-mista.json",
                 timeout=60, verify=False)
items = r.json()["polozky"]

print(f"Total: {len(items)} items\n")

for i, item in enumerate(items[:5]):
    print(f"\n{'='*60}")
    print(f"ITEM {i}")

    print("\n-- mistoVykonuPrace (full) --")
    print(json.dumps(item.get("mistoVykonuPrace"), ensure_ascii=False, indent=2))

    print("\n-- kontaktniPracoviste (full) --")
    print(json.dumps(item.get("kontaktniPracoviste"), ensure_ascii=False, indent=2))
