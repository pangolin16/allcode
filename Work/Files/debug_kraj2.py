"""Run: python3 debug_kraj2.py"""
import requests, urllib3, json
from collections import defaultdict
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

r = requests.get("https://data.mpsv.cz/od/soubory/volna-mista/volna-mista.json",
                 timeout=60, verify=False)
items = r.json()["polozky"]

# For each kraj ID collect sample location text (dodatekAdresy or nazev after " - ")
samples = defaultdict(set)

for item in items:
    misto = item.get("mistoVykonuPrace") or {}
    for p in (misto.get("pracoviste") or []):
        adresa = p.get("adresa") or {}
        kraj = adresa.get("kraj") or {}
        kid = kraj.get("id", "")
        if not kid:
            continue
        # collect any readable location hint
        hint = (adresa.get("dodatekAdresy") or "").strip()
        if not hint:
            nazev = (p.get("nazev") or "")
            if " - " in nazev:
                hint = nazev.rsplit(" - ", 1)[-1].strip()
        if hint and len(samples[kid]) < 5:
            samples[kid].add(hint)

for kid in sorted(samples, key=lambda k: int(k.split("/")[1])):
    print(f"{kid:12}  {sorted(samples[kid])}")
