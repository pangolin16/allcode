"""Run on your machine: python3 debug_vejprty.py"""
import requests, urllib3, json, unicodedata

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def normalize(text):
    if not text: return ""
    text = text.lower().strip()
    text = unicodedata.normalize('NFD', text)
    return ''.join(c for c in text if unicodedata.category(c) != 'Mn')

r = requests.get("https://data.mpsv.cz/od/soubory/volna-mista/volna-mista.json",
                 timeout=60, verify=False)
items = r.json()["polozky"]

# Find ALL items that contain "vejprty" anywhere in their raw JSON
print("Scanning for all Vejprty-related items...\n")
found = []
for item in items:
    raw = json.dumps(item, ensure_ascii=False).lower()
    if "vejprty" in raw:
        found.append(item)

print(f"Found {len(found)} items containing 'vejprty' in raw JSON\n")

for i, item in enumerate(found):
    misto = item.get("mistoVykonuPrace") or {}
    print(f"{'='*60}")
    print(f"ITEM {i} | portalId: {item.get('portalId')}")
    print(f"  obec id    : {(misto.get('obec') or {}).get('id')}")
    print(f"  adresaText : {misto.get('adresaText')}")
    for j, p in enumerate(misto.get("pracoviste") or []):
        adresa = p.get("adresa") or {}
        print(f"  pracoviste[{j}].nazev        : {p.get('nazev')}")
        print(f"  pracoviste[{j}].adresa (full):")
        print(json.dumps(adresa, ensure_ascii=False, indent=4))
    print()

# Also find what obec ID the 2 FOUND items use — that's the Vejprty obec ID
print("\n--- Obec IDs across all found items ---")
for item in found:
    misto = item.get("mistoVykonuPrace") or {}
    obec = (misto.get("obec") or {}).get("id")
    for p in (misto.get("pracoviste") or []):
        adresa_obec = ((p.get("adresa") or {}).get("obec") or {}).get("id")
        print(f"  portalId={item.get('portalId')} | misto.obec={obec} | adresa.obec={adresa_obec}")
