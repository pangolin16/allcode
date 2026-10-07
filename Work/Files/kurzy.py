#!/usr/bin/env python3
"""
Stažení a seskupení rekvalifikačních kurzů z up.gov.cz (jen standardní knihovna).

  python kurzy.py probe   # stáhne 3 záznamy a ukáže strukturu odpovědi
  python kurzy.py fetch   # stáhne všechny kurzy do kurzy_raw.json
  python kurzy.py build   # vytvoří kurzy_seznam.csv a kurzy_seznam.txt
  python kurzy.py build --only-open   # jen kurzy s aspoň jedním neuzavřeným termínem

Volby:  --full      pošle příznaky opt* jako true (výchozí je false, přesně jako zachycený požadavek)
        --url URL   jiná adresa endpointu
"""
import csv
import json
import os
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.request
import uuid
from collections import Counter, defaultdict

URL = "https://up.gov.cz/api/rekvalifikace/rest/kurz/query-ex?v=rekvv2"
PAGE_SIZE = 100          # kolik záznamů na jeden dotaz (server může omezit)
DELAY = 0.7              # pauza mezi dotazy v sekundách – šetrné k serveru
RAW_FILE = "kurzy_raw.json"

# Názvy polí v odpovědi. Po kroku "probe" je případně upravte podle skutečných klíčů.
NAME_KEYS = ["nazev", "nazevKurzu", "name"]
CATEGORY_KEYS = ["kategorie", "kategorieNazev", "obor", "oblast"]

# Sloučení kategorií do vašich ~9 oborů: "Název oboru": ["klíčové slovo v kategorii", ...]
# Když zůstane prázdné, skupinou je původní kategorie z úřadu práce.
GROUPS = {
    # "Administrativa, ekonomie, účetnictví": ["administrativ", "ekonom", "ucetnic"],
}


# ---------------------------------------------------------------- stahování
def make_payload(start, count, full=False):
    flags = ["KurzIds", "DruhKurzu", "NazevKurzu", "KodKurzu", "StavKurzu",
             "StavZajmu", "NazevVzdelavatele", "IcoVzdelavatele", "Kategorie",
             "Akreditace", "FormaVzdelavaniIds", "Termin", "Cena", "JazykIds",
             "MistoKonani", "TypKurzuIds"]
    payload = {"opt" + f: full for f in flags}
    payload["pagination"] = {"start": start, "count": count, "order": ["-id"]}
    return payload


def post(url, payload):
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"), method="POST",
        headers={
            "User-Agent": "Mozilla/5.0 (kurzy.py; osobni analyza nabidky kurzu)",
            "Accept": "application/json",
            "Accept-Language": "cs",
            "Content-Type": "application/json",
            "Origin": "https://up.gov.cz",
            "Referer": "https://up.gov.cz/vyhledani-rekvalifikacniho-kurzu",
            "x-client-session-id": str(uuid.uuid4()).upper(),
        })
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:800]
        sys.exit(f"\nServer vrátil HTTP {e.code}.\nOdpověď serveru:\n{body}")


def split_response(resp):
    """Vrátí (seznam_záznamů, celkový_počet_nebo_None) bez ohledu na obal odpovědi."""
    if isinstance(resp, list):
        return resp, None
    lists = [v for v in resp.values() if isinstance(v, list) and v and isinstance(v[0], dict)]
    records = max(lists, key=len) if lists else []
    total = None
    for k in ("total", "totalCount", "count", "celkem", "pocet", "pocetZaznamu", "totalElements"):
        if isinstance(resp.get(k), int):
            total = resp[k]
            break
    return records, total


def fetch_all(url, full):
    out, start, total, last_sig = [], 0, None, None
    while True:
        resp = post(url, make_payload(start, PAGE_SIZE, full))
        records, t = split_response(resp)
        total = t if t is not None else total
        if not records:
            break
        sig = json.dumps(records[0], sort_keys=True)
        if sig == last_sig:      # server ignoruje "start" -> ochrana proti nekonečné smyčce
            print("Server vrací stále stejnou stránku, končím.")
            break
        last_sig = sig
        out.extend(records)
        start += len(records)
        print(f"Staženo {len(out)}" + (f" / {total}" if total else ""))
        if total and len(out) >= total:
            break
        time.sleep(DELAY)
    return out


def probe(url, full):
    print(f"===== opt* = {full} =====")
    resp = post(url, make_payload(0, 3, full))
    print(json.dumps(resp, ensure_ascii=False, indent=2)[:6000])


# ---------------------------------------------------------------- zpracování
def strip_accents(s):
    s = unicodedata.normalize("NFKD", s.lower())
    return "".join(c for c in s if not unicodedata.combining(c))


def _gender_pair(m):
    a, b = m.group(1), m.group(2)
    return a if len(os.path.commonprefix([a.lower(), b.lower()])) >= 4 else m.group(0)


def short_title(name):
    """'(027478) Specialista/specialistka marketingu - ON-LINE ...' -> 'Specialista marketingu'."""
    s = re.sub(r"^\s*\(\d+\)\s*", "", name)                       # číslo kurzu na začátku
    s = re.split(r"\s+[-–—]\s+|:\s", s, maxsplit=1)[0]            # dovětek za " - " nebo ": "
    s = re.sub(r"(\w+)/(\w+)", _gender_pair, s)                   # specialista/specialistka
    return s.strip()


def normalize(name):
    """Klíč pro sloučení stejných profesí: bez diakritiky, závorek, počtu hodin a slova 'kurz'."""
    s = strip_accents(short_title(name))
    s = re.sub(r"\(.*?\)|\[.*?\]", " ", s)
    s = re.sub(r"\b\d+\s*(hodin|hodiny|hod|h)\b", " ", s)
    s = re.sub(r"\b(rekvalifikacni\s+)?kurz(y)?\b|\bonline\b|\bprezencne\b", " ", s)
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def to_text(v):
    if v is None:
        return ""
    if isinstance(v, dict):
        for k in ("nazev", "name", "popis", "hodnota", "text"):
            if v.get(k):
                return str(v[k])
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, list):
        return "; ".join(filter(None, (to_text(x) for x in v)))
    return str(v)


def find_key(record, candidates, hint):
    low = {k.lower(): k for k in record}
    for c in candidates:
        if c.lower() in low:
            return low[c.lower()]
    for k in record:  # záloha: klíč obsahující nápovědu, ale ne údaje o vzdělavateli
        if hint in k.lower() and "vzdelav" not in k.lower():
            return k
    return None


def group_of(category):
    cat = strip_accents(category)
    for group, keywords in GROUPS.items():
        if any(strip_accents(k) in cat for k in keywords):
            return group
    return category or "(bez kategorie)"


def open_terms(r):
    return [t for t in (r.get("aktualniTerminy") or []) if not t.get("uzavreny") and not t.get("zruseny")]


def build(only_open=False):
    with open(RAW_FILE, encoding="utf-8") as f:
        records = json.load(f)
    if only_open:
        records = [r for r in records if open_terms(r)]
    nk = find_key(records[0], NAME_KEYS, "nazev")
    ck = find_key(records[0], CATEGORY_KEYS, "kategor")
    if not nk:
        sys.exit("Nenašel jsem pole s názvem kurzu. Klíče: " + ", ".join(records[0]) +
                 "\nUpravte NAME_KEYS na začátku skriptu.")
    print(f"Pole názvu: {nk} | pole kategorie: {ck or '(žádné - zatím bez kategorií)'}")

    agg = defaultdict(lambda: {"names": Counter(), "cats": set(), "providers": set(), "prices": []})
    for r in records:
        name = to_text(r.get(nk)).strip()
        if not name:
            continue
        cv = r.get(ck) if ck else None
        categories = [to_text(c) for c in cv] if isinstance(cv, list) else [to_text(cv)]
        for cat in categories or [""]:
            a = agg[(group_of(cat), normalize(name))]
            a["names"][short_title(name)] += 1
            a["cats"].add(cat)
            a["providers"].add((r.get("osoba") or {}).get("id"))
            a["prices"] += [t["cena"] for t in open_terms(r) if t.get("cena") is not None]

    rows = []
    for (group, _), a in agg.items():
        best = a["names"].most_common(1)[0][0]
        best = re.sub(r"\s*\(.*?\)", "", best)
        best = re.sub(r"^(rekvalifikační\s+)?kurz\s*[-:]?\s*", "", best, flags=re.I).strip() or best
        rows.append([group, "; ".join(sorted(c for c in a["cats"] if c)), best,
                     sum(a["names"].values()), len(a["providers"]),
                     int(min(a["prices"])) if a["prices"] else ""])
    rows.sort(key=lambda x: (x[0].lower(), x[2].lower()))

    with open("kurzy_seznam.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["skupina", "kategorie_ouradu", "profese", "pocet_nabidek", "pocet_vzdelavatelu", "cena_od_kc"])
        w.writerows(rows)
    with open("kurzy_seznam.txt", "w", encoding="utf-8") as f:
        current = None
        for group, _, prof, n, p, price in rows:
            if group != current:
                f.write(f"\n{group}\n")
                current = group
            f.write(f"  - {prof} ({n}x, {p} vzděl.)\n")
    print(f"Kurzů: {len(records)} | unikátních profesí: {len(rows)} | skupin: {len({r[0] for r in rows})}")
    print("Uloženo: kurzy_seznam.csv, kurzy_seznam.txt")


if __name__ == "__main__":
    args = sys.argv[1:]
    url = args[args.index("--url") + 1] if "--url" in args else URL
    full = "--full" in args
    cmd = args[0] if args else ""
    if cmd == "probe":
        probe(url, full)
    elif cmd == "fetch":
        data = fetch_all(url, full)
        with open(RAW_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        print(f"Uloženo {len(data)} záznamů do {RAW_FILE}")
    elif cmd == "build":
        build(only_open="--only-open" in args)
    else:
        print(__doc__)