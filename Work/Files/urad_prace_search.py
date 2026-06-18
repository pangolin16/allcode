"""
Custom search tool for Urad prace CR job listings
Uses the official JSON data source from data.mpsv.cz
"""

import requests
from typing import List, Dict, Optional
import urllib3
import unicodedata
import re
import json
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ORS API key — set via environment variable ORS_API_KEY or pass directly.
import os as _os
_ORS_API_KEY = _os.environ.get("ORS_API_KEY", "")


def is_point_in_polygon(x: float, y: float, poly: list) -> bool:
    """Determine if point (x=lon, y=lat) is inside polygon coordinates list [[lon, lat], ...]"""
    num = len(poly)
    j = num - 1
    c = False
    for i in range(num):
        if ((poly[i][1] > y) != (poly[j][1] > y)) and \
                (x < (poly[j][0] - poly[i][0]) * (y - poly[i][1]) / (poly[j][1] - poly[i][1]) + poly[i][0]):
            c = not c
        j = i
    return c


def get_ors_isochrone(lat: float, lon: float, max_minutes: int, mode: str, api_key: str = "") -> tuple:
    """
    Fetch an isochrone polygon from OpenRouteService.
    Returns (polygon, error_message):
      polygon       — list of [lon, lat] pairs, or [] on failure
      error_message — None on success, descriptive string on failure
    """
    key = api_key or _ORS_API_KEY
    if not key:
        msg = "ORS_API_KEY není nastaven — přidejte ho do .env souboru"
        print(f"  WARNING: {msg}")
        return [], msg

    profile_map = {"car": "driving-car", "bike": "cycling-regular", "walk": "foot-walking"}
    profile = profile_map.get(mode, "driving-car")

    url = f"https://api.openrouteservice.org/v2/isochrones/{profile}"
    headers = {"Authorization": key, "Content-Type": "application/json"}
    body = {
        "locations": [[lon, lat]],
        "range": [min(int(max_minutes) * 60, 3600)],  # ORS free tier cap: 3600s (60 min)
        "range_type": "time"
    }
    try:
        print(f"  ORS POST {url}")
        print(f"  ORS body: {body}")
        resp = requests.post(url, json=body, headers=headers, timeout=10)
        print(f"  ORS response: HTTP {resp.status_code}")
        if resp.status_code == 200:
            geojson = resp.json()
            coords = geojson['features'][0]['geometry']['coordinates'][0]
            print(f"  ORS polygon: {len(coords)} vertices")
            return coords, None
        else:
            # Surface the actual ORS error message (JSON or plain text)
            try:
                err_body = resp.json()
                detail = err_body.get("error", {})
                if isinstance(detail, dict):
                    msg = detail.get("message") or str(detail)
                else:
                    msg = str(detail)
            except Exception:
                msg = resp.text[:300]
            full = f"HTTP {resp.status_code}: {msg}"
            print(f"  ORS error: {full}")
            return [], full
    except requests.exceptions.Timeout:
        msg = "ORS API timeout (>10s) — zkuste znovu"
        print(f"  ORS: {msg}")
        return [], msg
    except Exception as e:
        msg = f"Síťová chyba: {e}"
        print(f"  ORS: {msg}")
        return [], msg


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
    Returns (display, search_text, lat, lon) from mistoVykonuPrace.

    display     - clean city name shown to the user
    search_text - ALL raw text from every address field, used for filtering.
                  This catches cities that appear only inside street address
                  strings like "Delnicka 1253/37, 43191 Vejprty" where the
                  city is not in dodatekAdresy but is in the full address.
    lat, lon    - WGS84 coordinates (float), 0.0 if not available.
    """
    if not isinstance(misto, dict):
        return "", "", 0.0, 0.0
    if obec_lookup is None:
        obec_lookup = {}

    lat, lon = 0.0, 0.0

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

        # Extract WGS84 coordinates (first pracoviste that has them wins)
        if lat == 0.0 and lon == 0.0:
            wgs = adresa.get("wgs84") or {}
            if isinstance(wgs, dict):
                try:
                    _lat = float(wgs.get("lat") or wgs.get("latitude") or wgs.get("zemepisnaSirka") or 0)
                    _lon = float(wgs.get("lon") or wgs.get("lng") or wgs.get("longitude") or wgs.get("zemepisnaDelka") or 0)
                    if _lat and _lon:
                        lat, lon = _lat, _lon
                except (TypeError, ValueError):
                    pass
            # Also try geometrie / vysledek_ruian style: [lon, lat] array
            if lat == 0.0:
                for coord_key in ("geometrie", "vysledek_ruian", "souradnice"):
                    coords = adresa.get(coord_key) or pracoviste.get(coord_key)
                    if isinstance(coords, list) and len(coords) >= 2:
                        try:
                            _lon2, _lat2 = float(coords[0]), float(coords[1])
                            if _lat2 and _lon2:
                                lat, lon = _lat2, _lon2
                                break
                        except (TypeError, ValueError):
                            pass

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

    return ", ".join(unique), " ".join(all_text_parts), lat, lon


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

    # ------------------------------------------------------------------
    # PSC -> (lat, lon) geocoding cache
    # ------------------------------------------------------------------

    PSC_CACHE_FILE = "psc_coords_cache.json"

    def _load_psc_cache(self) -> dict:
        if os.path.exists(self.PSC_CACHE_FILE):
            try:
                with open(self.PSC_CACHE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_psc_cache(self, cache: dict):
        try:
            with open(self.PSC_CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(cache, f, ensure_ascii=False)
        except Exception as e:
            print(f"  Warning: could not save PSC cache: {e}")

    def _geocode_psc_batch(self, psc_set: set, existing_cache: dict) -> dict:
        """
        Geocode all PSC codes not already in cache using Nominatim.
        Returns updated cache dict.
        """
        cache = dict(existing_cache)
        missing = [p for p in psc_set if p and p not in cache]
        if not missing:
            return cache

        print(f"  Geocoding {len(missing):,} new PSC codes via Nominatim...")
        headers = {"User-Agent": "UradPraceJobSearch/1.0 (psc-geocoder)"}
        ok = 0
        for i, psc in enumerate(missing):
            try:
                url = "https://nominatim.openstreetmap.org/search"
                params = {"postalcode": psc, "country": "cz", "format": "json", "limit": 1}
                r = requests.get(url, params=params, headers=headers, timeout=8)
                results = r.json()
                if results:
                    cache[psc] = [float(results[0]["lat"]), float(results[0]["lon"])]
                    ok += 1
                else:
                    cache[psc] = None  # mark as "tried but not found"
            except Exception as e:
                print(f"    PSC {psc} geocode error: {e}")
                cache[psc] = None
            # Nominatim rate limit: max 1 req/s
            if i % 50 == 49:
                print(f"    ... {i+1}/{len(missing)} ({ok} found so far)")
            import time
            time.sleep(1.05)

        print(f"  Geocoded {ok}/{len(missing)} PSC codes successfully.")
        return cache

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

            # Pass 1: build obec_id -> city_name lookup
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
                    dodatek = (adresa.get("dodatekAdresy") or "").strip()
                    if dodatek and obec_id not in obec_lookup:
                        clean = re.sub(r'(?i)^(okres|mesto|město|obec|cast obce)\s+', '', dodatek).strip()
                        if clean and not any(c.isdigit() for c in clean):
                            obec_lookup[obec_id] = clean

            print(f"  Built obec lookup: {len(obec_lookup):,} entries")

            # Pass 2: collect all unique PSC codes present in the data
            psc_set = set()
            for it in items:
                if not isinstance(it, dict):
                    continue
                misto = it.get("mistoVykonuPrace") or {}
                for p in (misto.get("pracoviste") or []):
                    if not isinstance(p, dict):
                        continue
                    psc = str((p.get("adresa") or {}).get("psc") or "").strip()
                    if psc:
                        psc_set.add(psc)
            print(f"  Found {len(psc_set):,} unique PSC codes.")

            # Pass 3: load disk cache, geocode missing PSCs, save back
            psc_cache = self._load_psc_cache()
            cached_before = sum(1 for v in psc_cache.values() if v)
            print(f"  PSC cache: {len(psc_cache):,} entries ({cached_before:,} with coords).")
            psc_cache = self._geocode_psc_batch(psc_set, psc_cache)
            self._save_psc_cache(psc_cache)

            # Pass 4: parse all items
            parsed = [self._parse_item(i, obec_lookup, psc_cache) for i in items if isinstance(i, dict)]
            self.all_jobs = [j for j in parsed if j["title"]]

            with_loc    = sum(1 for j in self.all_jobs if j["location"])
            with_coords = sum(1 for j in self.all_jobs if j.get("lat"))
            print(f"  Loaded {len(self.all_jobs):,} jobs | {with_loc:,} with location | {with_coords:,} with coords.")

            if self.all_jobs:
                s = self.all_jobs[0]
                print(f"  Sample: {s['title']} | {s['location']!r} | lat={s.get('lat')} lon={s.get('lon')}")

        except Exception as e:
            print(f"  Error loading data: {e}")
            import traceback
            traceback.print_exc()


    def _parse_item(self, item: dict, obec_lookup: dict = None, psc_cache: dict = None) -> Dict:
        title    = _extract(item.get("pozadovanaProfese") or item.get("nazevPozice") or item.get("pozice"))
        employer = _extract(item.get("zamestnavatel") or item.get("nazevFirmy"))
        location, location_search, lat, lon = _extract_location(item.get("mistoVykonuPrace"), obec_lookup or {})

        # If _extract_location found no coords (MPSV data has none), look up by PSC
        if (not lat or not lon) and psc_cache:
            misto_raw = item.get("mistoVykonuPrace") or {}
            for _p in (misto_raw.get("pracoviste") or []):
                psc = str((_p.get("adresa") or {}).get("psc") or "").strip()
                if psc and psc_cache.get(psc):
                    lat, lon = psc_cache[psc]
                    break

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

        # Languages: try several possible fields and also fall back to scanning
        # descriptive text. Normalize into short tokens for filtering.
        languages_found = []
        # Common field names that may contain language info
        for key in ("jazykoveZnalosti", "jazyk", "pozadovanaJazykovaZnalost", "jazykovaZnalost", "jazykove_znalosti"):
            val = item.get(key)
            if not val:
                continue
            if isinstance(val, str):
                if val.strip():
                    languages_found.append(val.strip())
            elif isinstance(val, dict):
                # dict may contain 'jazyk' or 'nazev'
                lang_text = _extract(val.get("jazyk") or val.get("nazev") or val.get("name"))
                if lang_text:
                    languages_found.append(lang_text)
            elif isinstance(val, list):
                for e in val:
                    if isinstance(e, dict):
                        languages_found.append(_extract(e.get("jazyk") or e.get("nazev") or e.get("name") or e))
                    else:
                        languages_found.append(_extract(e))

        # Also look in description/title for explicit language mentions
        info_text = _extract(item.get("upresnujiciInformace") or item.get("popis") or "")
        text_scan = _normalize(info_text + " " + title)
        explicit_langs = []
        for raw in languages_found:
            n = _normalize(raw)
            if n:
                explicit_langs.append(n)

        # Combine explicit langs and any mentions found in text
        combined = set(explicit_langs)
        # quick keyword checks for common languages
        lang_keyword_map = {
            "czech": ["cest", "cesk"],
            "slovak": ["slov"],
            "english": ["angl", "english"],
            "french": ["franc"],
            "spanish": ["span", "espan"],
        }
        # If keywords appear in scanned text, add them
        for slug, kws in lang_keyword_map.items():
            for kw in kws:
                if kw in text_scan:
                    combined.add(slug)
                    break

        # Also map explicit language names to slugs
        for n in explicit_langs:
            for slug, kws in lang_keyword_map.items():
                if any(k in n for k in kws):
                    combined.add(slug)
                    break
            else:
                # keep other languages as their normalized form
                combined.add(n)

        # Build a searchable text blob for languages (used for passive mentions)
        language_search = text_scan

        return {
            "id":          job_id,
            "title":       title,
            "employer":    employer,
            "location":    location,
            "location_search": location_search,
            "lat":         lat,
            "lon":         lon,
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
            "languages":   list(combined),
            "language_search": language_search,
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
                    exclude_languages: Optional[list] = None,
                    exclude_education: Optional[list] = None,
                    regions: Optional[list] = None,
                    lat_center: Optional[float] = None,
                    lon_center: Optional[float] = None,
                    max_minutes: Optional[int] = None,
                    travel_mode: str = 'car',
                    ors_api_key: str = "") -> List[Dict]:

        print(f"\nSearch: kw={keyword!r} loc={location!r} sal={min_salary}-{max_salary} "
              f"driver_excl={exclude_driver_license} edu={education!r} langs={exclude_languages} edus_excl={exclude_education} "
              f"isochrone=({lat_center},{lon_center},{max_minutes}min,{travel_mode})")

        if not self.all_jobs:
            print("No jobs cached - reloading...")
            self._load_data()

        jobs = self.all_jobs.copy()

        # KEYWORD: title-only to avoid false matches in descriptions
        if keyword:
            kw = _normalize(keyword)
            jobs = [j for j in jobs if kw in _normalize(j["title"])]
            print(f"  after keyword (title only): {len(jobs):,}")

        # ISOCHRONE: travel-time polygon filter (replaces plain text location when coords available)
        isochrone_polygon = None
        iso_status = {
            "requested": False,
            "geocoded": lat_center is not None,
            "polygon_fetched": False,
            "polygon_vertices": 0,
            "jobs_with_coords": 0,
            "jobs_without_coords": 0,
            "error": None,
            "mode": travel_mode,
            "max_minutes": max_minutes,
            "lat": lat_center,
            "lon": lon_center,
        }

        if lat_center is not None and lon_center is not None and max_minutes:
            iso_status["requested"] = True
            print(f"  Fetching isochrone: {max_minutes} min by {travel_mode} from ({lat_center}, {lon_center})")
            isochrone_polygon, ors_error = get_ors_isochrone(lat_center, lon_center, max_minutes, travel_mode, ors_api_key)
            if isochrone_polygon:
                iso_status["polygon_fetched"] = True
                iso_status["polygon_vertices"] = len(isochrone_polygon)
                print(f"  Isochrone polygon: {len(isochrone_polygon)} vertices")
                before = len(jobs)
                result = []
                no_coords = 0
                for j in jobs:
                    jlat, jlon = j.get("lat", 0.0), j.get("lon", 0.0)
                    if jlat and jlon:
                        if is_point_in_polygon(jlon, jlat, isochrone_polygon):
                            result.append(j)
                    else:
                        no_coords += 1
                        # No coordinates — fallback to text match if location text provided
                        if location:
                            loc = _normalize(location)
                            import re as _re
                            loc_pattern = _re.compile(r'(?<![a-z0-9])' + _re.escape(loc) + r'(?![a-z0-9])')
                            if loc_pattern.search(_normalize(j["location_search"] or j["location"])):
                                result.append(j)
                        else:
                            result.append(j)
                iso_status["jobs_with_coords"] = before - no_coords
                iso_status["jobs_without_coords"] = no_coords
                jobs = result
                print(f"  after isochrone filter: {len(jobs):,} (was {before:,}, {no_coords} had no coords)")
            else:
                iso_status["error"] = ors_error or "ORS vrátil prázdný polygon"
                print("  Isochrone fetch failed — falling back to text location filter")

        # LOCATION: normalised substring match (skipped if isochrone succeeded)
        if location and (isochrone_polygon is None or not isochrone_polygon):
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

        if exclude_languages:
            jobs = self._filter_languages(jobs, exclude_languages)
            print(f"  after language filter:      {len(jobs):,}")

        if exclude_education:
            jobs = self._filter_exclude_education(jobs, exclude_education)
            print(f"  after education exclusion:  {len(jobs):,}")

        if regions:
            jobs = self._filter_regions(jobs, regions)
            print(f"  after region filter:        {len(jobs):,}")

        jobs.sort(key=lambda j: _normalize(j.get("title", "")))
        print(f"  => {len(jobs):,} results (returning up to {limit})")
        return jobs[:limit], iso_status

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
            "basic":      ["zakladni", "zaklad", "bezvzdel", "neuplzakl", "zaklpraktskol"],
            "vocational": ["vycucen", "stredni odborne", "sou", "nizsi", "stredodbor", "stredodborvyuc"],
            "secondary":  ["maturita", "stredni s maturitou", "usosmat", "/usv"],
            "higher":     ["vyssi odborne", "vos", "vyssodbor"],
            "bachelor":   ["bakalar", "bakal", "bc."],
            "master":     ["magistr", "mgr.", "ing.", "vysoka"],
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

    @staticmethod
    def _filter_languages(jobs, exclude_languages):
        """
        Exclude jobs that require languages in the exclude list.
        exclude_languages is a list of slugs: czech, slovak, english, french, spanish, other
        Jobs with no language info are kept unless a passive mention in text matches.
        """
        if not exclude_languages:
            return jobs
        excluded = {s.lower() for s in exclude_languages}
        known = {"czech", "slovak", "english", "french", "spanish"}

        # keyword map (same as parsing)
        lang_keyword_map = {
            "czech": ["cest", "cesk"],
            "slovak": ["slov"],
            "english": ["angl", "english"],
            "french": ["franc"],
            "spanish": ["span", "espan"],
        }

        result = []
        for job in jobs:
            job_langs = set((job.get("languages") or []))
            lang_text = _normalize(job.get("language_search") or "" )

            should_exclude = False

            # If 'other' is requested, exclude jobs that mention any language
            # not in the known set.
            if "other" in excluded:
                for l in job_langs:
                    if l and l not in known:
                        should_exclude = True
                        break

            # Check explicit known languages and passive mentions
            for slug in (excluded & known):
                if slug in job_langs:
                    should_exclude = True
                    break
                # check passive mentions in language_search text
                for kw in lang_keyword_map.get(slug, []):
                    if kw in lang_text:
                        should_exclude = True
                        break
                if should_exclude:
                    break

            if not should_exclude:
                result.append(job)

        return result

    @staticmethod
    def _filter_exclude_education(jobs, exclude_education):
        """
        Exclude jobs that require education levels in the exclude list.
        exclude_education is a list of slugs:
          zakladni      - basic/elementary
          stredni       - secondary without maturita
          maturita      - secondary with maturita
          vyssiodborne  - higher vocational
          bakalar       - university bachelor (Bc.)
          magister      - university master (Mgr./Ing.)
          doktor        - PhD/doctoral

        Uses keyword matching against normalized education field.
        """
        if not exclude_education:
            return jobs

        excluded = {s.lower() for s in exclude_education}

        # keyword map for matching
        edu_keyword_map = {
            "zakladni":     ["zakladni", "zaklad", "bezvzdel", "neuplzakl", "zaklpraktskol"],
            "stredni":      ["stredni odborne", "ucni", "nizsi", "stredodbor", "stredodborvyuc"],
            "maturita":     ["maturita", "stredni s maturitou", "usosmat", "/usv"],
            "vyssiodborne": ["vyssi odborne", "vos", "vyssodbor"],
            "bakalar":      ["bakalar", "bakal", "bc.", "bc "],
            "magister":     ["magistr", "mgr.", "mgr ", "ing.", "ing ", "vysoka"],
            "doktor":       ["doktor", "phd", "ph.d.", "postdok"],
        }

        result = []
        for job in jobs:
            edu_text = _normalize(job.get("education") or "")

            should_exclude = False

            # Check each excluded education level
            for slug in excluded:
                kws = edu_keyword_map.get(slug, [])
                for kw in kws:
                    if kw in edu_text:
                        should_exclude = True
                        break
                if should_exclude:
                    break

            if not should_exclude:
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