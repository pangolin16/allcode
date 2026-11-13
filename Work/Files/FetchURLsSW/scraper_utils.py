"""
scraper_utils - UNIVERSAL FIXED version for all 4 scrapers
- headers for ALL domains
- lxml fallback get_soup()
- blacklist uses word-boundary for short terms
- dedup robust + URL normalization
- fetch handles 403/429/503
- TITLE_BLACKLIST loaded from Title_Blacklist.json (no hardcoded list)
"""

import time
import random
import json
import re
from pathlib import Path
from urllib.parse import urlparse, urlunparse, urljoin
import requests

CHECKPOINT_DIR = Path("checkpoints")
CHECKPOINT_DIR.mkdir(exist_ok=True)

# --- TITLE_BLACKLIST reference ---
# File can be in same folder as this script or in current working dir
TITLE_BLACKLIST_FILE = Path(__file__).parent / "Title_Blacklist.json"

def _load_title_blacklist():
    """Load blacklist terms from Title_Blacklist.json - supports list or dict formats"""
    candidates = [
        TITLE_BLACKLIST_FILE,
        Path("Title_Blacklist.json"),
        Path.cwd() / "Title_Blacklist.json",
    ]
    for fp in candidates:
        if fp.exists():
            try:
                data = json.loads(fp.read_text(encoding="utf-8"))
                # If file is a plain list: ["erotic", "onlyfans"]
                if isinstance(data, list):
                    terms = [str(x).strip() for x in data if str(x).strip()]
                    print(f"  Loaded TITLE_BLACKLIST from {fp}: {len(terms)} terms")
                    return terms
                # If file is dict: {"TITLE_BLACKLIST": [...]} or {"blacklist": [...]}
                if isinstance(data, dict):
                    for key in ["TITLE_BLACKLIST", "TITLE_BLACKLIST_TERMS", "BLACKLIST_TERMS", "blacklist", "terms", "list", "data"]:
                        if key in data and isinstance(data[key], list):
                            terms = [str(x).strip() for x in data[key] if str(x).strip()]
                            print(f"  Loaded TITLE_BLACKLIST from {fp}[{key}]: {len(terms)} terms")
                            return terms
                    # fallback: first list value in dict
                    for v in data.values():
                        if isinstance(v, list):
                            terms = [str(x).strip() for x in v if str(x).strip()]
                            print(f"  Loaded TITLE_BLACKLIST from {fp} (first list): {len(terms)} terms")
                            return terms
                print(f"  ! Title_Blacklist.json format unknown in {fp}, using empty")
                return []
            except Exception as e:
                print(f"  ! Failed to load Title_Blacklist.json {fp}: {e}, using empty blacklist")
                return []
    # File not found -> empty blacklist (safe)
    # print(f"  Title_Blacklist.json not found, using empty blacklist")
    return []

def reload_blacklist():
    """Reload TITLE_BLACKLIST from disk - call after editing Title_Blacklist.json"""
    global TITLE_BLACKLIST, BLACKLIST_TERMS
    TITLE_BLACKLIST = _load_title_blacklist()
    BLACKLIST_TERMS = TITLE_BLACKLIST
    return TITLE_BLACKLIST

# Load once at import
TITLE_BLACKLIST = _load_title_blacklist()
BLACKLIST_TERMS = TITLE_BLACKLIST  # backward compat alias

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
]

DOMAIN_HEADERS = {
    "jooble.org": {"referer": "https://cz.jooble.org/", "origin": "https://cz.jooble.org"},
    "jenprace.cz": {"referer": "https://www.jenprace.cz/", "origin": "https://www.jenprace.cz"},
    "volnamista.cz": {"referer": "https://www.volnamista.cz/", "origin": "https://www.volnamista.cz"},
    "profesia.cz": {"referer": "https://www.profesia.cz/", "origin": "https://www.profesia.cz"},
    "dobraprace.cz": {"referer": "https://www.dobraprace.cz/", "origin": "https://www.dobraprace.cz"},
    "pracezarohem.cz": {"referer": "https://www.pracezarohem.cz/", "origin": "https://www.pracezarohem.cz"},
    "jobs.cz": {"referer": "https://www.jobs.cz/", "origin": "https://www.jobs.cz"},
    "brigadovnik.cz": {"referer": "https://www.brigadovnik.cz/", "origin": "https://www.brigadovnik.cz"},
    "fajn-brigady.cz": {"referer": "https://www.fajn-brigady.cz/", "origin": "https://www.fajn-brigady.cz"},
    "randstad.cz": {"referer": "https://www.randstad.cz/", "origin": "https://www.randstad.cz"},
    "easyprace.cz": {"referer": "https://www.easyprace.cz/", "origin": "https://www.easyprace.cz"},
    "superannonce.cz": {"referer": "https://www.superannonce.cz/", "origin": "https://www.superannonce.cz"},
    "annonce.cz": {"referer": "https://www.annonce.cz/", "origin": "https://www.annonce.cz"},
    "easy-prace.cz": {"referer": "https://www.easy-prace.cz/", "origin": "https://www.easy-prace.cz"},
    "superkariera.cz": {"referer": "https://www.superkariera.cz/", "origin": "https://www.superkariera.cz"},
}

def _match_domain_config(url: str):
    url_l = url.lower()
    for domain, cfg in DOMAIN_HEADERS.items():
        if domain in url_l:
            return cfg
    return None

def _get_headers_for_url(url: str):
    ua = random.choice(USER_AGENTS)
    cfg = _match_domain_config(url)
    if cfg:
        referer = cfg["referer"]
        origin = cfg["origin"]
        same_origin = True
    else:
        referer = "https://www.google.com/"
        origin = None
        same_origin = False
    headers = {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "cs-CZ,cs;q=0.9,en-US;q=0.8,en;q=0.7,sk;q=0.6,uk;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Referer": referer,
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin" if same_origin else "cross-site",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
        "Connection": "keep-alive",
        "DNT": "1",
    }
    if origin:
        headers["Origin"] = origin
    if any(d in url.lower() for d in ["jooble.org", "profesia.cz", "pracezarohem.cz", "jobs.cz"]):
        headers["Sec-Ch-Ua"] = '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"'
        headers["Sec-Ch-Ua-Mobile"] = "?0"
        headers["Sec-Ch-Ua-Platform"] = '"Windows"'
    return headers

def fetch_with_retry(url, retries=4, timeout=25, session=None):
    use_cloudscraper = False
    try:
        import cloudscraper
        use_cloudscraper = True
    except ImportError:
        use_cloudscraper = False
    if session is None:
        if use_cloudscraper and "jooble.org" in url.lower():
            try:
                import cloudscraper
                session = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})
            except Exception:
                session = requests.Session()
        else:
            session = requests.Session()
    if "jooble.org" in url.lower():
        try:
            home_headers = _get_headers_for_url("https://cz.jooble.org/")
            session.get("https://cz.jooble.org/", headers=home_headers, timeout=10)
            time.sleep(random.uniform(0.5, 1.2))
        except Exception:
            pass
    elif "pracezarohem.cz" in url.lower() or "profesia.cz" in url.lower():
        try:
            base = "https://www.pracezarohem.cz/" if "pracezarohem" in url.lower() else "https://www.profesia.cz/"
            home_headers = _get_headers_for_url(base)
            session.get(base, headers=home_headers, timeout=8)
            time.sleep(random.uniform(0.3, 0.8))
        except Exception:
            pass
    last_exc = None
    last_response = None
    for attempt in range(1, retries + 1):
        headers = _get_headers_for_url(url)
        try:
            r = session.get(url, headers=headers, timeout=timeout)
            last_response = r
            if r.status_code in (403, 429, 500, 502, 503, 504):
                print(f"  ! fetch fail attempt {attempt}/{retries} {url} : {r.status_code} {r.reason} -> rotating UA & retrying")
                last_exc = requests.exceptions.HTTPError(f"{r.status_code} {r.reason} for url: {url}", response=r)
                time.sleep(1.5 * (attempt + 1) + random.uniform(0.5, 1.5))
                if attempt == 2 and "jooble.org" in url.lower() and use_cloudscraper:
                    try:
                        import cloudscraper
                        session = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})
                        session.get("https://cz.jooble.org/", headers=headers, timeout=10)
                    except Exception:
                        pass
                continue
            r.raise_for_status()
            if len(r.text) < 100 and attempt < retries:
                print(f"  ! fetch tiny response {len(r.text)} chars attempt {attempt}/{retries} -> retrying")
                time.sleep(1.0 * attempt)
                continue
            return r
        except requests.exceptions.HTTPError as e:
            if e.response is not None and e.response.status_code in (404, 410):
                raise                      # page does not exist - retrying is pointless
            if last_response is None or last_response.status_code not in (403, 429, 500, 502, 503, 504):
                print(f"  ! fetch fail attempt {attempt}/{retries} {url} : {e}")
            last_exc = e
        except Exception as e:
            print(f"  ! fetch fail attempt {attempt}/{retries} {url} : {e}")
            last_exc = e
        time.sleep(1.5 * (attempt + 1) + random.uniform(0, 1))
    if last_exc:
        raise last_exc
    raise requests.exceptions.HTTPError(f"Failed to fetch {url} after {retries} retries")

def get_soup(html):
    if not html:
        html = ""
    try:
        from bs4 import BeautifulSoup, FeatureNotFound
        try:
            return BeautifulSoup(html, "lxml")
        except FeatureNotFound:
            return BeautifulSoup(html, "html.parser")
        except Exception:
            return BeautifulSoup(html, "html.parser")
    except ImportError:
        from bs4 import BeautifulSoup
        return BeautifulSoup(html, "html.parser")

def make_soup(html):
    return get_soup(html)

def save_checkpoint(name, jobs, partial=False):
    """partial=True -> checkpoint_<name>.partial.json (never used for resume)"""
    try:
        CHECKPOINT_DIR.mkdir(exist_ok=True)
        suffix = ".partial.json" if partial else ".json"
        path = CHECKPOINT_DIR / f"checkpoint_{name}{suffix}"
        path.write_text(json.dumps(jobs, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        print(f"  ! checkpoint save failed {name}: {e}")

def load_checkpoints():
    data = {}
    for p in CHECKPOINT_DIR.glob("checkpoint_*.json"):
        try:
            data[p.stem] = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            pass
    return data

def clear_checkpoints():
    for p in CHECKPOINT_DIR.glob("checkpoint_*.json"):
        try:
            p.unlink()
        except Exception:
            pass
    for p in Path(".").glob("*_incremental.json"):
        try:
            p.unlink()
        except Exception:
            pass
    for p in Path(".").glob("*_temp.json"):
        try:
            p.unlink()
        except Exception:
            pass

def incremental_save(all_jobs, base_name):
    try:
        path = Path(f"{base_name}_incremental.json")
        path.write_text(json.dumps(all_jobs, ensure_ascii=False, indent=2), encoding="utf-8")
    except Exception as e:
        print(f"  ! incremental save failed: {e}")

def is_blacklisted(title: str) -> bool:
    """Check title against TITLE_BLACKLIST loaded from Title_Blacklist.json"""
    if not title:
        return False
    # Always use latest from file if you want live reload, or use cached global
    # Here we use global TITLE_BLACKLIST which was loaded at import, but you can call reload_blacklist() to refresh
    terms = TITLE_BLACKLIST
    if not terms:
        return False
    t = title.lower()
    for raw in terms:
        b = raw.lower().strip()
        if not b:
            continue
        if len(b) <= 3:
            if re.search(r'\b' + re.escape(b) + r'\b', t):
                return True
        else:
            if b in t:
                return True
    return False

def _normalize_url(url: str) -> str:
    """Strip fragment + tracking params. Path/query case is PRESERVED (IDs are case-sensitive)."""
    if not url:
        return ""
    try:
        parsed = urlparse(url.strip().split("#")[0])
        q = "&".join(p for p in parsed.query.split("&")
                     if p and not p.lower().startswith("utm_") and "fbclid" not in p.lower() and "gclid" not in p.lower())
        return urlunparse((parsed.scheme.lower(), parsed.netloc.lower(), parsed.path.rstrip("/"), parsed.params, q, ""))
    except Exception:
        return url.strip().rstrip("/")

def dedup_jobs(jobs):
    """Dedup by normalized URL only. title|company is used ONLY for jobs that have no URL
    (title-only dedup used to wipe out different jobs that share a title)."""
    seen = set()
    out = []
    for j in jobs:
        url = _normalize_url(j.get("url") or "")
        if url:
            key = "u:" + url
        else:
            key = "t:" + (j.get("title") or "").strip().lower() + "|" + (j.get("company") or "").strip().lower() + "|" + (j.get("source") or "")
        if key in seen:
            continue
        seen.add(key)
        out.append(j)
    return out, len(jobs) - len(out)

# ---------------------------------------------------------------- parsing helpers
def abs_url(href, base):
    """Always return an absolute URL (handles /x, x, //host/x). '' for junk links."""
    if not href:
        return ""
    href = href.strip()
    if href.startswith(("javascript:", "mailto:", "tel:", "#")):
        return ""
    return urljoin(base, href)

def extract_jobs(html, page_url, source, domain, card_sel,
                 company_sel="[class*='company'], [class*='employer'], [class*='firm']",
                 href_must=(), href_exclude=("strana=", "page=", "page_num=", "/strana/", "?p=", "&p="),
                 url_filter=None):
    """Generic parser. 1) job cards -> best link per card.  2) fallback: every same-domain link
    (optionally only those containing one of href_must). Every job gets an absolute URL."""
    soup = get_soup(html)
    jobs, seen, rejected = [], set(), []

    def add(title, href, comp="", must=()):
        url = abs_url(href, page_url)
        title = re.sub(r"\s+", " ", title or "").strip()
        if not url or domain not in urlparse(url).netloc.lower() or url in seen:
            return False
        if any(x in url for x in href_exclude):
            return False
        if must and not any(x in url for x in must):
            return False
        if url_filter and not url_filter(url):      # strict "is this really an offer detail URL?"
            if len(rejected) < 5 and url not in rejected:
                rejected.append(url)
            return False
        if not (4 <= len(title) <= 250):
            return False
        seen.add(url)
        jobs.append({"title": title, "company": comp, "url": url, "source": source})
        return True

    for card in (soup.select(card_sel) if card_sel else []):   # card_sel='' -> link-only mode
        ce = card.select_one(company_sel) if company_sel else None
        comp = ce.get_text(" ", strip=True)[:120] if ce else ""
        heading = card.select_one("h1, h2, h3, h4, [class*='title']")
        anchors = (card.select("h1 a[href], h2 a[href], h3 a[href], h4 a[href], a[class*='title'][href], [class*='title'] a[href]")
                   + card.select("a[href]"))
        for a in anchors:
            title = a.get_text(" ", strip=True)
            if len(title) < 4 and heading:
                title = heading.get_text(" ", strip=True)
            if add(title, a["href"], comp):
                break          # one job per card
    if not jobs:
        for a in soup.find_all("a", href=True):
            add(a.get_text(" ", strip=True), a["href"], must=href_must)
    if not jobs and rejected:
        print(f"\n    ! {source}: 0 offer links accepted; rejected by url_filter e.g.:")
        for u in rejected:
            print(f"        {u}")
    return jobs

def _dump_debug(name, page, html):
    try:
        d = Path("debug"); d.mkdir(exist_ok=True)
        (d / f"{name}_p{page}.html").write_text(html or "", encoding="utf-8")
        print(f"    (saved debug/{name}_p{page}.html - open it and check the selectors / whether the page is JS-rendered)")
    except Exception:
        pass

def scrape_paginated(src, max_pages=50, delay=(1.0, 2.5), resume=True, timeout=25):
    """Walk pages until: empty page, page with NO NEW URLs, or 3 consecutive fetch errors.
    (No fixed 'per_page' threshold and no HTML-head hashing - both ended scraping after page 1-2.)"""
    name = src["name"]
    print(f"\n=== SOURCE {name.upper()} ===")
    final_ckpt = CHECKPOINT_DIR / f"checkpoint_{name}.json"
    if resume and final_ckpt.exists():
        try:
            data = json.loads(final_ckpt.read_text(encoding="utf-8"))
            if data:
                print(f"  resume: {len(data)} jobs from completed checkpoint")
                return data
        except Exception:
            pass
    collected, seen, errors = [], set(), 0
    template, fallback, page = src["url_template"], src.get("fallback_template"), 0
    while page < max_pages:
        page += 1
        url = template.format(page=page)
        print(f"  {name} page {page}: {url}", end=" ", flush=True)
        try:
            r = fetch_with_retry(url, timeout=timeout)
            jobs = src["parser"](r.text, url)
            errors = 0
        except Exception as e:
            resp = getattr(e, "response", None)
            if resp is not None and resp.status_code in (404, 410):
                if page == 1 and fallback and fallback != template:
                    print(f"-> {resp.status_code}; switching to fallback URL")
                    template, fallback, page = fallback, None, 0
                    continue
                print(f"-> {resp.status_code}: no more pages" + (" (check the URL!)" if page == 1 else ""))
                break
            errors += 1
            print(f"-> ERROR {e}")
            if errors >= 3:
                break
            continue
        if not jobs:
            print("-> 0 jobs, stop")
            if page == 1:
                _dump_debug(name, page, r.text)
            break
        new = [j for j in jobs if _normalize_url(j["url"]) not in seen]
        print(f"-> {len(jobs)} jobs, {len(new)} new")
        if not new:
            break
        seen.update(_normalize_url(j["url"]) for j in new)
        collected.extend(new)
        save_checkpoint(name, collected, partial=True)
        time.sleep(random.uniform(*delay))
    deduped, removed = dedup_jobs(collected)
    print(f"  {name}: {len(collected)} raw -> {len(deduped)} after dedup (removed {removed})")
    if deduped:
        save_checkpoint(name, deduped)
    return deduped

def filter_blacklist(jobs, label=""):
    kept = [j for j in jobs if not is_blacklisted(j.get("title", ""))]
    gone = [j for j in jobs if is_blacklisted(j.get("title", ""))]
    print(f"  {label} blacklist ({len(TITLE_BLACKLIST)} terms): {len(jobs)} -> {len(kept)} (removed {len(gone)})")
    for j in gone[:5]:
        print(f"      removed e.g.: {j.get('title','')[:70]}")
    return kept

def save_final_outputs(jobs, base_name):
    import csv
    for pat in [f"{base_name}_incremental.json", f"{base_name}_filtered.json", f"{base_name}_filtered.csv", f"{base_name}_*_temp.json"]:
        for f in Path(".").glob(pat):
            try: f.unlink()
            except Exception: pass
    json_path, csv_path = Path(f"{base_name}.json"), Path(f"{base_name}.csv")
    json_path.write_text(json.dumps(jobs, ensure_ascii=False, indent=2), encoding="utf-8")
    keys = sorted({k for j in jobs for k in j})
    pref = [k for k in ["id", "title", "company", "location", "url", "source"] if k in keys or not jobs]
    ordered = pref + [k for k in keys if k not in pref]
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as cf:
        w = csv.DictWriter(cf, fieldnames=ordered)
        w.writeheader()
        for j in jobs:
            w.writerow({k: j.get(k, "") for k in ordered})
    print(f"Saved: {json_path} and {csv_path} ({len(jobs)} jobs)")
