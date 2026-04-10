"""
Custom search tool for Urad prace CR job listings
Uses the official JSON data source from data.mpsv.cz
"""

import requests
from typing import List, Dict, Optional
import urllib3
import unicodedata
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def _normalize(text: str) -> str:
    """Lowercase + strip diacritics: Praha == praha == PRAHA"""
    if not text:
        return ""
    text = text.lower().strip()
    text = unicodedata.normalize('NFD', text)
    return ''.join(c for c in text if unicodedata.category(c) != 'Mn')


def _extract(value) -> str:
    """Pull a plain string from str / dict {'nazev':...} / list"""
    if value is None:
        return ""
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, dict):
        for k in ("nazev", "name", "Nazev"):
            if value.get(k):
                return str(value[k]).strip()
        for v in value.values():
            if isinstance(v, str) and v.strip():
                return v.strip()
        return ""
    if isinstance(value, list):
        return ", ".join(_extract(i) for i in value if _extract(i))
    return str(value).strip()


def _extract_location(misto, obec_lookup=None):
    """
    Returns (display, search_text) from mistoVykonuPrace.

    display     - clean city name shown to the user
    search_text - ALL raw text from every address field, used for filtering.
                  This catches cities that appear only inside street address
                  strings like "Delnicka 1253/37, 43191 Vejprty" where the
                  city is not in dodatekAdresy but is in the full address.
    """
    if not isinstance(misto, dict):
        return "", ""
    if obec_lookup is None:
        obec_lookup = {}

    display_candidates = []
    all_text_parts = []

    for pracoviste in (misto.get("pracoviste") or []):
        if not isinstance(pracoviste, dict):
            continue

        nazev = (pracoviste.get("nazev") or "").strip()
        # Add workplace name to search text only if it contains a city hint
        # (after " - "), not the whole string — avoids "Litvínovská s.r.o." etc.
        if " - " in nazev:
            city_hint = nazev.rsplit(" - ", 1)[-1].strip()
            import re as _re2
            if city_hint and not _re2.search(r'(s\.r\.o|a\.s|spol|ltd|gmbh|inc)', city_hint, _re2.IGNORECASE):
                all_text_parts.append(city_hint)

        adresa = pracoviste.get("adresa") or {}

        # Add city-level fields to search text ONLY — NOT ulice (street name).
        # Including street names causes false matches, e.g. street "Litvínovská"
        # in Praha 9 matching the city filter "Litvínov".
        # Safe fields: dodatekAdresy (usually city), psc (postal code)
        for field in ("dodatekAdresy", "psc"):
            val = _extract(adresa.get(field))
            if val:
                all_text_parts.append(val)

        # Display source 1: dodatekAdresy — strip noise prefixes
        dodatek = (adresa.get("dodatekAdresy") or "").strip()
        if dodatek:
            clean = re.sub(r'(?i)^(okres|mesto|m\u011bsto|obec|cast obce|\u010d\xe1st obce)\s+', '', dodatek).strip()
            if clean:
                display_candidates.append(clean)

        # Display source 2: city after " - " in pracoviste.nazev
        if " - " in nazev:
            after_dash = nazev.rsplit(" - ", 1)[-1].strip()
            if after_dash and not re.search(r'(?i)\b(s\.r\.o|a\.s|spol|ltd|gmbh|inc)\b', after_dash):
                clean = re.sub(r'(?i)^(okres|mesto|m\u011bsto|obec)\s+', '', after_dash).strip()
                if clean:
                    display_candidates.append(clean)

    # Fallback: if we have no display name yet, try resolving adresa.obec.id
    # via the lookup built from other items in the dataset.
    # e.g. "Obec/563404" -> "Vejprty" (learned from a sibling item)
    if not display_candidates and obec_lookup:
        for pracoviste in (misto.get("pracoviste") or []):
            if not isinstance(pracoviste, dict):
                continue
            adresa = pracoviste.get("adresa") or {}
            obec_id = (adresa.get("obec") or {}).get("id") or ""
            if obec_id and obec_id in obec_lookup:
                city = obec_lookup[obec_id]
                display_candidates.append(city)
                all_text_parts.append(city)
                break

    # Also always add obec ID itself to search text so it can be matched
    # even if the lookup doesn't have it yet
    for pracoviste in (misto.get("pracoviste") or []):
        if not isinstance(pracoviste, dict):
            continue
        adresa = pracoviste.get("adresa") or {}
        obec_id = (adresa.get("obec") or {}).get("id") or ""
        if obec_id:
            all_text_parts.append(obec_id)

    # Deduplicate display
    seen = set()
    unique = []
    for c in display_candidates:
        key = _normalize(c)
        if key not in seen:
            seen.add(key)
            unique.append(c)

    return ", ".join(unique), " ".join(all_text_parts)


def _to_int(value) -> int:
    if value is None:
        return 0
    try:
        return int(str(value).replace("\xa0", "").replace(" ", "").replace(",", ""))
    except (ValueError, TypeError):
        return 0


class UradPraceSearcher:

    def __init__(self):
        self.data_url = "https://data.mpsv.cz/od/soubory/volna-mista/volna-mista.json"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
        })
        self.all_jobs: List[Dict] = []
        self._load_data()

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    def _load_data(self):
        print("\nLoading job data...")
        try:
            r = self.session.get(self.data_url, timeout=60, verify=False)
            print(f"  HTTP {r.status_code} | {len(r.content):,} bytes")

            if r.status_code != 200:
                print("  Failed to load data.")
                return

            data = r.json()
            items = data.get("polozky") if isinstance(data, dict) else data

            if not isinstance(items, list) or not items:
                print(f"  ERROR: no polozky list.")
                return

            print(f"  Parsing {len(items):,} items...")

            # Pass 1: build obec_id -> city_name lookup from items that have text.
            # e.g. "Obec/563404" -> "Vejprty" (learned from an item whose
            # dodatekAdresy = "Vejprty" and adresa.obec.id = "Obec/563404")
            obec_lookup = {}
            for it in items:
                if not isinstance(it, dict):
                    continue
                misto = it.get("mistoVykonuPrace") or {}
                for p in (misto.get("pracoviste") or []):
                    if not isinstance(p, dict):
                        continue
                    adresa = p.get("adresa") or {}
                    obec_id = (adresa.get("obec") or {}).get("id") or ""
                    if not obec_id:
                        continue
                    # Collect candidate city names from text fields
                    dodatek = (adresa.get("dodatekAdresy") or "").strip()
                    if dodatek and obec_id not in obec_lookup:
                        # Strip full street addresses — only keep short values
                        import re as _re
                        clean = _re.sub(r'(?i)^(okres|mesto|m\u011bsto|obec|cast obce)\s+', '', dodatek).strip()
                        # Reject if it looks like a street address (contains digits)
                        if clean and not any(c.isdigit() for c in clean):
                            obec_lookup[obec_id] = clean

            print(f"  Built obec lookup: {len(obec_lookup):,} entries")

            # Pass 2: parse all items, passing the lookup for ID resolution
            parsed = [self._parse_item(i, obec_lookup) for i in items if isinstance(i, dict)]
            self.all_jobs = [j for j in parsed if j["title"]]

            # Quick location sanity check
            with_loc = sum(1 for j in self.all_jobs if j["location"])
            print(f"  Loaded {len(self.all_jobs):,} jobs ({with_loc:,} have a location).")

            if self.all_jobs:
                s = self.all_jobs[0]
                print(f"  Sample: {s['title']} | {s['employer']} | location={s['location']!r} | {s['salary']}")

            # Show first 5 extracted locations so you can verify
            print("  Location samples:")
            for j in self.all_jobs[:5]:
                print(f"    {j['location']!r}")

        except Exception as e:
            import traceback
            print(f"  Error loading data: {e}")
            traceback.print_exc()

    def _parse_item(self, item: dict, obec_lookup: dict = None) -> Dict:
        title    = _extract(item.get("pozadovanaProfese") or item.get("nazevPozice") or item.get("pozice"))
        employer = _extract(item.get("zamestnavatel") or item.get("nazevFirmy"))
        location, location_search = _extract_location(item.get("mistoVykonuPrace"), obec_lookup or {})

        salary_from = _to_int(item.get("mesicniMzdaOd") or item.get("mzdaOd"))
        salary_to   = _to_int(item.get("mesicniMzdaDo") or item.get("mzdaDo"))

        if salary_from and salary_to:
            salary_text = f"{salary_from} - {salary_to} Kc/mesic"
        elif salary_from:
            salary_text = f"Od {salary_from} Kc/mesic"
        elif salary_to:
            salary_text = f"Do {salary_to} Kc/mesic"
        else:
            salary_text = ""

        education = _extract(item.get("minPozadovaneVzdelani") or item.get("pozadovaneVzdelani") or item.get("vzdelani"))

        # CS-ISCO — profeseCzIsco is {"id": "CzIsco/44110", "nazev": "Knihovnici"}
        isco_raw  = item.get("profeseCzIsco") or {}
        isco_id   = (isco_raw.get("id") or "") if isinstance(isco_raw, dict) else str(isco_raw)
        isco_code = isco_id.replace("CzIsco/", "").strip()

        # portalId is the integer (e.g. 67186345); id is "VolneMisto/67186345"
        portal_id = item.get("portalId") or ""
        job_id    = str(portal_id)
        # urlAdresa is the direct link when present
        url_adresa = (item.get("urlAdresa") or "").strip()
        posted    = str(item.get("datumVlozeni") or "")[:10]
        desc      = _extract(item.get("upresnujiciInformace") or item.get("popis") or "")[:500]
        ppr       = item.get("pracovnePravniVztahy") or []
        if not isinstance(ppr, list):
            ppr = [ppr]
        job_type = _extract(ppr[0] if ppr else {})
        # All contract type IDs as a list (JSON-serializable)
        # e.g. ["plny", "sluzebni"]
        ppr_ids  = [
            e.get("id", "").replace("PracovnepravniVztah/", "").strip()
            for e in ppr if isinstance(e, dict) and e.get("id")
        ]

        # Region (kraj) — from adresa.kraj.id inside pracoviste
        kraj_id = ""
        misto_raw = item.get("mistoVykonuPrace") or {}
        for _p in (misto_raw.get("pracoviste") or []):
            _kraj = ((_p.get("adresa") or {}).get("kraj") or {})
            if _kraj.get("id"):
                kraj_id = _kraj["id"]
                break

        smennost_raw = item.get("smennost")
        if isinstance(smennost_raw, list):
            shift_ids = [e.get("id","").split("/")[-1] for e in smennost_raw if isinstance(e,dict) and e.get("id")]
        elif isinstance(smennost_raw, dict) and smennost_raw.get("id"):
            shift_ids = [smennost_raw["id"].split("/")[-1]]
        else:
            shift_ids = []

        return {
            "id":          job_id,
            "title":       title,
            "employer":    employer,
            "location":    location,
            "location_search": location_search,
            "salary":      salary_text,
            "salary_from": salary_from,
            "salary_to":   salary_to,
            "type":        job_type,
            "ppr_ids":     ppr_ids,
            "shift_ids":   shift_ids,
            "kraj_id":     kraj_id,
            "posted":      posted,
            "education":   education,
            "isco_code":   isco_code,
            "url":         f"https://up.gov.cz/volna-mista-v-cr#/volna-mista-detail/{job_id}" if job_id else "#",
            "description": desc,
        }

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search_jobs(self,
                    keyword: Optional[str] = None,
                    location: Optional[str] = None,
                    limit: int = 20,
                    exclude_driver_license: bool = False,
                    min_salary: Optional[int] = None,
                    max_salary: Optional[int] = None,
                    education: Optional[str] = None,
                    exclude_isco: Optional[str] = None,
                    full_time_only: bool = False,
                    exclude_shifts: Optional[list] = None,
                    regions: Optional[list] = None) -> List[Dict]:

        print(f"\nSearch: kw={keyword!r} loc={location!r} sal={min_salary}-{max_salary} "
              f"driver_excl={exclude_driver_license} edu={education!r}")

        if not self.all_jobs:
            print("No jobs cached - reloading...")
            self._load_data()

        jobs = self.all_jobs.copy()

        # KEYWORD: title-only to avoid false matches in descriptions
        if keyword:
            kw = _normalize(keyword)
            jobs = [j for j in jobs if kw in _normalize(j["title"])]
            print(f"  after keyword (title only): {len(jobs):,}")

        # LOCATION: normalised substring match
        if location:
            loc = _normalize(location)
            before = len(jobs)
            # Use whole-word matching so "Most" doesn't match "Mostkovice",
            # "Kněžmost", "Horní Moštěnice", etc.
            # Lookbehind + lookahead ensure the query is not part of a larger word.
            import re as _re
            loc_pattern = _re.compile(r'(?<![a-z0-9])' + _re.escape(loc) + r'(?![a-z0-9])')
            jobs = [j for j in jobs if loc_pattern.search(_normalize(j["location_search"] or j["location"]))]
            print(f"  after location '{location}': {len(jobs):,} (was {before:,})")
            if len(jobs) == 0:
                print("  WARNING: 0 matches. Sample stored locations:")
                for j in self.all_jobs[:10]:
                    print(f"    {j['location']!r}")

        # SALARY: filter on job floor (salary_from), not ceiling
        if min_salary or max_salary:
            jobs = self._filter_salary(jobs, min_salary, max_salary)
            print(f"  after salary:               {len(jobs):,}")

        if exclude_driver_license:
            jobs = self._filter_driver_license(jobs)
            print(f"  after driver filter:        {len(jobs):,}")

        if education:
            jobs = self._filter_education(jobs, education)
            print(f"  after education:            {len(jobs):,}")

        if exclude_isco:
            jobs = self._filter_isco(jobs, exclude_isco)
            print(f"  after ISCO exclusion:       {len(jobs):,}")

        if full_time_only:
            jobs = self._filter_full_time_only(jobs)
            print(f"  after full-time filter:     {len(jobs):,}")

        if exclude_shifts:
            jobs = self._filter_shifts(jobs, exclude_shifts)
            print(f"  after shift filter:         {len(jobs):,}")

        if regions:
            jobs = self._filter_regions(jobs, regions)
            print(f"  after region filter:        {len(jobs):,}")

        print(f"  => {len(jobs):,} results (returning up to {limit})")
        return jobs[:limit]

    # ------------------------------------------------------------------
    # Filters
    # ------------------------------------------------------------------

    @staticmethod
    def _filter_salary(jobs, min_sal, max_sal):
        result = []
        for job in jobs:
            s_from = job["salary_from"]
            s_to   = job["salary_to"]
            if s_from == 0 and s_to == 0:
                continue
            floor = s_from if s_from > 0 else s_to
            if min_sal and floor < min_sal:
                continue
            if max_sal and floor > max_sal:
                continue
            result.append(job)
        return result

    @staticmethod
    def _filter_driver_license(jobs):
        bad = ["ridic", "ridicka", "ridicsky", "prukaz", "vozidlo", "kamion", "autobus"]
        return [j for j in jobs if not any(kw in _normalize(j["title"]) for kw in bad)]

    @staticmethod
    def _filter_education(jobs, education):
        edu_map = {
            "basic":      ["zakladni"],
            "vocational": ["vycucen", "stredni odborne", "sou"],
            "secondary":  ["maturita", "stredni s maturitou"],
            "higher":     ["vyssi odborne", "vos"],
            "bachelor":   ["bakalar", "bc."],
            "master":     ["magistr", "mgr.", "ing."],
            "phd":        ["doktor", "ph.d.", "phd"],
        }
        kws = edu_map.get(education)
        if not kws:
            return jobs
        return [j for j in jobs
                if any(kw in _normalize(j["education"] + " " + j["title"]) for kw in kws)]

    @staticmethod
    def _filter_isco(jobs: List[Dict], exclude_isco: str) -> List[Dict]:
        """
        Exclude jobs whose CS-ISCO code is in the exclusion set.

        exclude_isco accepts any combination of:
          - Newline-separated (paste from spreadsheet):  "72241\n72242\n72243"
          - Comma-separated:                             "72241,72242,72243"
          - Range notation:                              "11110-35229"
          - Mixed:                                       "11110-35229\n72241\n73152"

        Jobs with no ISCO code at all are always kept.
        """
        if not exclude_isco:
            return jobs

        excluded: set = set()

        # Split on newlines and commas to get individual tokens
        tokens = [t.strip() for t in exclude_isco.replace(",", "\n").splitlines() if t.strip()]

        for token in tokens:
            if "-" in token:
                # Range like "11110-35229"
                parts = token.split("-", 1)
                try:
                    start = int(parts[0].strip())
                    end   = int(parts[1].strip())
                    for code in range(start, end + 1):
                        excluded.add(str(code))
                except ValueError:
                    pass  # skip malformed range
            else:
                excluded.add(token)

        # Expand for 4-digit <-> 5-digit equivalence.
        # Some categories have both a 4-digit code (e.g. 7533) and a 5-digit
        # code (e.g. 75330) referring to the same occupation group.
        #
        # Rule 1: if a 5-digit code is excluded (e.g. 51201),
        #         also exclude its 4-digit parent (5120).
        # Rule 2: if a 4-digit code is excluded (e.g. 5120),
        #         also exclude any 5-digit child found in actual job data
        #         (51201, 51202, ...) by checking the prefix.
        #
        # We do this by matching on prefix at filter time rather than
        # pre-expanding (which would require knowing all possible codes).
        # Save what the user actually entered before adding ancestor prefixes.
        # We need this to avoid over-matching: entering 54141 adds ancestor 541,
        # but that must NOT cause unrelated code 5412 to be excluded.
        user_entered = frozenset(excluded)

        # Add 4-digit and 3-digit ancestors so jobs catalogued under a broader
        # code are also caught (e.g. 32211 -> also exclude job listed as 3221 or 322).
        four_digit  = {c[:4] for c in user_entered if len(c) == 5 and c.isdigit()}
        three_digit = {c[:3] for c in user_entered if len(c) >= 4 and c.isdigit()}
        excluded |= four_digit | three_digit

        print(f"    ISCO exclusion: {len(user_entered):,} user codes -> {len(excluded):,} after expansion")

        def is_excluded(code: str) -> bool:
            if not code:
                return False
            # Exact match (includes auto-added ancestor codes)
            if code in excluded:
                return True
            # 5-digit job code:
            #   exclude if its 4-digit parent is in excluded (added from a sibling)
            #   exclude if its 3-digit parent was directly entered by the user
            if len(code) == 5 and code.isdigit():
                return code[:4] in excluded or code[:3] in user_entered
            # 4-digit job code:
            #   exclude if its 3-digit parent was directly entered by the user
            #   exclude if any 5-digit child was directly entered by the user
            #   (NOT if a 3-digit ancestor was auto-added from a different branch)
            if len(code) == 4 and code.isdigit():
                return (code[:3] in user_entered or
                        any(c.startswith(code) for c in user_entered if len(c) == 5))
            # 3-digit job code:
            #   exclude if any longer code starting with it was entered by the user
            if len(code) == 3 and code.isdigit():
                return any(c.startswith(code) for c in user_entered if len(c) > 3)
            return False

        return [j for j in jobs if not is_excluded(j.get("isco_code", ""))]

    @staticmethod
    def _filter_full_time_only(jobs):
        KEEP = {"plny", "sluzebni"}
        result = []
        for job in jobs:
            ppr_ids = set(job.get("ppr_ids") or [])
            if not ppr_ids:
                result.append(job)
            elif ppr_ids & KEEP:
                result.append(job)
        return result

    @staticmethod
    def _filter_shifts(jobs, exclude_shifts):
        """
        Exclude jobs whose shift type is in the exclusion list.
        exclude_shifts is a list of Smennost ID slugs (the part after '/').

        Confirmed IDs from live data:
          jednoSm    - Jednosmenny provoz
          dvouSm     - Dvousmenny provoz
          triSm      - Trismenny provoz
          ctyrSm     - Ctyrsmenny provoz
          deleneSm   - Delene smeny
          nepretrzity - Nepretrzity provoz
          nocni      - Nocni provoz
          pruznaPd   - Pruzna pracovni doba
          turnus     - Turnusove sluzby
          neurceno   - Neurceno

        Jobs with no shift info are always kept.
        """
        if not exclude_shifts:
            return jobs
        excluded = set(exclude_shifts)
        result = []
        for job in jobs:
            shift_ids = set(job.get("shift_ids") or [])
            if not shift_ids:
                result.append(job)
            elif shift_ids - excluded:
                result.append(job)
        return result

    # Confirmed mapping from live data (kraj ID -> region name)
    KRAJ_MAP = {
        'Kraj/19':  'Praha',
        'Kraj/27':  'Středočeský kraj',
        'Kraj/35':  'Jihočeský kraj',
        'Kraj/43':  'Plzeňský kraj',
        'Kraj/51':  'Karlovarský kraj',
        'Kraj/60':  'Ústecký kraj',
        'Kraj/78':  'Liberecký kraj',
        'Kraj/86':  'Královéhradecký kraj',
        'Kraj/94':  'Pardubický kraj',
        'Kraj/108': 'Kraj Vysočina',
        'Kraj/116': 'Jihomoravský kraj',
        'Kraj/124': 'Olomoucký kraj',
        'Kraj/132': 'Moravskoslezský kraj',
        'Kraj/141': 'Zlínský kraj',
    }

    @staticmethod
    def _filter_regions(jobs, regions):
        """
        Keep only jobs in the given regions.
        regions is a list of Kraj IDs, e.g. ["Kraj/19", "Kraj/116"].
        Jobs with no region info are always kept.
        """
        if not regions:
            return jobs
        allowed = set(regions)
        return [j for j in jobs if not j.get("kraj_id") or j["kraj_id"] in allowed]