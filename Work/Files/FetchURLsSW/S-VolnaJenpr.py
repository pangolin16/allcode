"""Jooble + JenPrace + VolnaMista -> S-VolnaJenprJooble.json/.csv (all URLs kept)"""
import json, re
from pathlib import Path
from urllib.parse import urlparse
import scraper_utils as su
from scraper_utils import scrape_paginated, extract_jobs, dedup_jobs, filter_blacklist, save_final_outputs

BASE_NAME = Path(__file__).stem
RESUME = False
MAX_PAGES = 50
PAGE_DELAY = (1.0, 2.5)

# ------------------------------------------------------------------ Jooble
_JOOBLE = re.compile(r"^/(desc|jdp|job)/")
def jooble_is_offer(url):
    return bool(_JOOBLE.match(urlparse(url).path))

def parse_jooble(html, url):
    return extract_jobs(html, url, "jooble", "jooble.org",
                        "article, div[data-test='job-card'], li.result, div[class*='result']",
                        href_must=("/desc/", "/jdp/", "/job/"), url_filter=jooble_is_offer)

# ------------------------------------------------------------------ JenPrace
# offer = /nabidka/<6-char id>/<slug>  (or /brigada/<id>/<slug>); listings are /nabidky/... (plural) -> rejected
_JENPRACE = re.compile(r"^/(nabidka|brigada)/[a-z0-9]{4,10}/[^/]+$")
def jenprace_is_offer(url):
    return bool(_JENPRACE.match(urlparse(url).path))

def parse_jenprace(html, url):
    soup = su.get_soup(html)
    jobs, seen = [], set()
    for a in soup.select("a[href*='/nabidka/'], a[href*='/brigada/']"):
        link = su.abs_url(a.get("href", ""), url)
        if not link or link in seen or "jenprace.cz" not in link or not jenprace_is_offer(link):
            continue
        title = re.sub(r"\s+", " ", a.get_text(" ", strip=True))
        if len(title) < 3:
            continue
        company = ""
        try:                                   # company = first text after the <h2> title
            h = a.find_parent(["h2", "h3"]) or a
            for t in h.find_all_next(string=True):
                if t.strip() and h not in t.parents:      # first text AFTER the heading, not inside it
                    company = t.strip().split("|")[0].strip()[:120]
                    break
        except Exception:
            pass
        seen.add(link)
        jobs.append({"title": title[:250], "company": company, "url": link, "source": "jenprace"})
    return jobs

# ------------------------------------------------------------------ VolnaMista
# NOTE: volnamista.cz's robots rules block automated fetching and I could not inspect its HTML.
# So this parser LEARNS the offer-URL pattern from the page: 1) JSON-LD JobPosting urls,
# 2) the most common "offer-looking" URL shape among same-domain links. It logs the shapes it saw.
def _shape(path):
    segs = [x for x in path.split("/") if x]
    last = segs[-1] if segs else ""
    kind = "id" if re.search(r"\d{5,}", last) else ("slug" if len(last) >= 25 else "short")
    return (segs[0] if segs else "", len(segs), kind)

def parse_volnamista(html, url):
    soup = su.get_soup(html)
    jobs, seen = [], set()

    def add(title, href, company=""):
        link = su.abs_url(href, url)
        title = re.sub(r"\s+", " ", title or "").strip()
        if link and link not in seen and "volnamista.cz" in link and len(title) >= 4:
            seen.add(link)
            jobs.append({"title": title[:250], "company": company, "url": link, "source": "volnamista"})

    # 1) JSON-LD (JobPosting / ItemList)
    def walk(o):
        if isinstance(o, dict):
            if o.get("@type") == "JobPosting" and o.get("url"):
                org = o.get("hiringOrganization")
                add(o.get("title") or o.get("name") or "", o["url"], org.get("name", "") if isinstance(org, dict) else "")
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    for sc in soup.select("script[type='application/ld+json']"):
        try:
            walk(json.loads(sc.string or ""))
        except Exception:
            pass
    if jobs:
        return jobs

    # 2) learn the offer shape from the links on the page
    cands = []
    for a in soup.find_all("a", href=True):
        link = su.abs_url(a["href"], url)
        if not link or "volnamista.cz" not in link or "strana=" in link:
            continue
        title = a.get_text(" ", strip=True)
        if len(title) < 8:
            continue
        cands.append((link, title, _shape(urlparse(link).path)))
    groups = {}
    for link, title, shp in cands:
        groups.setdefault(shp, {})[link] = title
    if not groups:
        return []
    ranked = sorted(groups.items(), key=lambda kv: (kv[0][2] != "short", len(kv[1])), reverse=True)
    print("\n    volnamista link shapes (first-segment, depth, kind): count, example")
    for shp, d in ranked[:5]:
        print(f"      {shp}: {len(d)}  e.g. {next(iter(d))}")
    best_shape, best = ranked[0]
    if best_shape[2] == "short":
        return []                              # nothing that looks like an offer -> caller dumps debug HTML
    for link, title in best.items():
        add(title, link)
    return jobs

SOURCES = [
    # my test fetch of the language-filtered URL returned 404, so fall back to plain Praha listing if page 1 fails
    {"name": "jenprace", "url_template": "https://www.jenprace.cz/nabidky/praha?language%5B0%5D=5&language%5B1%5D=1&language%5B2%5D=34&page={page}",
     "fallback_template": "https://www.jenprace.cz/nabidky/praha?page={page}", "parser": parse_jenprace},
    {"name": "volnamista", "url_template": "https://www.volnamista.cz/praha?v-okoli=0-km&strana={page}", "parser": parse_volnamista},
]

def main():
    if not RESUME:
        su.clear_checkpoints()
    su.reload_blacklist()
    print(f"TITLE_BLACKLIST: {len(su.TITLE_BLACKLIST)} terms")
    all_jobs = []
    for src in SOURCES:
        try:
            jobs = scrape_paginated(src, max_pages=MAX_PAGES, delay=PAGE_DELAY, resume=RESUME)
            all_jobs.extend(filter_blacklist(jobs, src["name"]))
        except Exception as e:
            print(f"!! {src['name']} failed: {e}")
    final, dups = dedup_jobs(all_jobs)
    print(f"TOTAL {len(all_jobs)} -> {len(final)} (dups {dups})")
    save_final_outputs(final, BASE_NAME)

if __name__ == "__main__":
    main()
