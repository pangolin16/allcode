"""
MultiSourceJobs-Manpower-Grafton - FIXED VERSION
Scrapes Prague job listings from Manpower.cz and two Grafton.cz education filters.

Fixes for Grafton:
- Detail pages are now /en/node/<id> (not only /en/jobs/<slug>). Updated detail_link() and detail_patterns.
- Grafton pagination is Vue-based with no href (li > a without href). Pagination is handled
  entirely inside fetch_html() via Playwright clicks. pagination_urls() returns [] for Grafton.
- Added explicit wait for .job-item-wrapper and .job-total-count.
- Improved extract_listing_jobs to prioritize a.title-link and handle /en/node/ links.
- Fixed manpower pagination bug where f/stranka match was overwritten.

Outputs:
  S_manpowerGrafton.json
  S_manpowerGrafton.csv
  checkpoints/checkpoint_<source>.json
"""

import csv
import json
import random
import re
import time
import html as html_lib
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlunparse, parse_qsl, urlencode

from scraper_utils import (
    CHECKPOINT_DIR, dedup_jobs, fetch_with_retry, get_soup,
    is_blacklisted, reload_blacklist, save_checkpoint,
)

BASE_NAME = Path(__file__).stem.replace("_fixed", "")
RESUME = True
MAX_PAGES_PER_SOURCE = 60
DELAY = (0.9, 1.8)

SOURCES = [
    {
        "name": "manpower_praha",
        "start_url": "https://manpower.cz/nabidky-prace/f/okres/praha-hlavni-mesto/field/cyber-security,administrativa,bezpecnost-a-ekologie,data-science-analytics,development-engineering,doprava-a-logistika,ekonomika-ucetnictvi-bankovnictvi,elektro-a-automatizace,infrastructure,it-project-management,it-sprava,it-vyvoj,manualni-prace,retail,sluzby,stavebnictvi,vyroba-a-vyvoj,zdravotnictvi-a-farmaceutika,zemedelstvi/",
        "domain": "manpower.cz",
        "expected_urls": 110,
        "detail_patterns": (r"/nabidky-prace/", r"/job/"),
    },
    {
        "name": "grafton_education_5027",
        "start_url": "https://www.grafton.cz/en/job-search?location=Praha&lat=50.08333&lon=14.46667&distance=20km&education=5027",
        "domain": "grafton.cz",
        "expected_urls": 115,
        "detail_patterns": (r"/en/jobs?/", r"/en/node/", r"/en/(?:position|career)/", r"/job/"),
    },
    {
        "name": "grafton_education_5025",
        "start_url": "https://www.grafton.cz/en/job-search?location=Praha&lat=50.08333&lon=14.46667&distance=20km&education=5025",
        "domain": "grafton.cz",
        "expected_urls": 25,
        "detail_patterns": (r"/en/jobs?/", r"/en/node/", r"/en/(?:position|career)/", r"/job/"),
    },
]

TITLE_SELECTORS = (
    "h1", "h2", "h3", "h4", "[class*='job-title']", "[class*='job_title']",
    "[class*='title']", "[class*='position-name']", "[itemprop='title']",
)
COMPANY_SELECTORS = (
    "[class*='company']", "[class*='employer']", "[class*='firma']",
    "[itemprop='hiringOrganization']",
)
LOCATION_SELECTORS = (
    "[class*='location']", "[class*='lokalita']", "[class*='mesto']",
    "[itemprop='jobLocation']",
)
DATE_SELECTORS = (
    "time[datetime]", "time", "[class*='date']", "[class*='posted']",
    "[class*='publish']", "[class*='datum']",
)

def norm(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()

def abs_url(href, base):
    if not href:
        return ""
    href = href.strip()
    if href.startswith(("javascript:", "mailto:", "tel:", "#")):
        return ""
    return urljoin(base, href)

def clean_title(text):
    text = norm(text)
    text = re.sub(r"^(?:job title|position|pracovní pozice)\s*[:\-]\s*", "", text, flags=re.I)
    text = re.sub(r"\s*[|•]\s*.*$", "", text)
    return text.strip(" \t\r\n-|–—:;,.·")

def first_text(root, selectors, limit=160):
    if root is None:
        return ""
    for selector in selectors:
        try:
            nodes = root.select(selector)
        except Exception:
            nodes = []
        for node in nodes:
            value = norm(node.get("datetime") or node.get_text(" ", strip=True))
            if value and len(value) <= limit:
                return value
    return ""

def detail_link(url, source):
    """Recognize job-detail routes while excluding listing/filter routes."""
    parsed = urlparse(url)
    if source["domain"] not in parsed.netloc.lower():
        return False
    path = parsed.path.lower().rstrip("/")
    if not path:
        return False

    if source["name"].startswith("manpower"):
        prefix = "/nabidky-prace/"
        if not path.startswith(prefix):
            return False
        tail = path[len(prefix):]
        if any(seg in tail.split("/") for seg in ("f", "field", "okres", "stranka")):
            return False
        if tail in {"", "nabidky-prace"}:
            return False
        return len([part for part in tail.split("/") if part]) >= 1

    # Grafton
    if path in {"/en", "/en/jobs", "/en/job-search"}:
        return False
    if "/job-search" in path or any(part in path for part in (
        "/career-zone", "/about-us", "/contact", "/employers", "/jobs/apply"
    )):
        return False
    # Current Grafton routes:
    # - /en/jobs/<slug>  (old)
    # - /en/node/<numeric-id> (current, confirmed in debug HTML)
    # - /en/position/<slug> etc
    return bool(
        re.match(r"^/en/jobs?/[^/]+(?:/apply)?$", path) or
        re.match(r"^/en/node/\d+/?$", path) or
        re.match(r"^/en/(?:position|career)/[^/]+$", path)
    )

def extract_listing_jobs(html, page_url, source):
    """Extract every plausible job-detail URL; a title is optional."""
    soup = get_soup(html)
    jobs, seen = [], set()

    # Prioritize Grafton's actual job links: .job-item-wrapper a.title-link and a.more-info
    # Fallback to any a[href] that matches detail_link
    selectors = [
        "a.title-link[href]",
        "a.more-info[href]",
        "div.job-item-wrapper a[href]",
        "a[href*='/en/node/']",
        "a[href*='/en/jobs/']",
        "a[href]",
    ]
    # Use a set to avoid processing same anchor multiple times via overlapping selectors
    processed_anchors = set()

    for sel in selectors:
        for a in soup.select(sel):
            # Use id() to deduplicate anchor elements across selectors
            aid = id(a)
            if aid in processed_anchors:
                continue
            processed_anchors.add(aid)

            href = abs_url(a.get("href"), page_url)
            if not href:
                continue
            href = canonical(href)
            if not detail_link(href, source):
                continue
            key = canonical(href)
            if key in seen:
                continue

            title = ""
            # For Grafton node pages, the link text IS the title
            # Try direct text first
            direct_text = clean_title(a.get_text(" ", strip=True))
            if 4 <= len(direct_text) <= 180:
                # Exclude generic CTAs
                if direct_text.lower() not in {"read more", "more info", "detail", "jobs"}:
                    title = direct_text

            if not title:
                for selector in TITLE_SELECTORS:
                    try:
                        node = a.select_one(selector)
                    except Exception:
                        node = None
                    if node:
                        candidate = clean_title(node.get_text(" ", strip=True))
                        if 3 <= len(candidate) <= 180:
                            title = candidate
                            break
            if not title:
                heading = a.find_parent(["h1", "h2", "h3", "h4"])
                if heading:
                    title = clean_title(heading.get_text(" ", strip=True))
            if not title:
                title = clean_title(a.get("aria-label") or a.get("title") or a.get_text(" ", strip=True))
            if not (4 <= len(title) <= 180) or title.lower() in {
                "view job", "view details", "read more", "apply now", "more information",
                "show more", "learn more", "see details", "detail nabídky", "detail nabidky",
                "jobs", "refine search",
            }:
                # Fallback: slug from URL, but for /en/node/<id> slug is just id, so keep previous title or use id
                slug = urlparse(href).path.rstrip("/").split("/")[-1]
                # If slug is numeric (node id), keep title we already have or use href
                if slug.isdigit():
                    title = title or f"Grafton job {slug}"
                else:
                    fallback = re.sub(r"--\d+$", "", slug)
                    fallback = re.sub(r"[-_]+", " ", fallback).strip().title()
                    title = fallback or href

            context, node = a, a
            for _ in range(7):
                node = getattr(node, "parent", None)
                if node is None or not getattr(node, "get_text", None):
                    break
                txt = norm(node.get_text(" ", strip=True))
                if len(txt) <= 1800:
                    context = node
                if len(txt) > 1800:
                    break
            company = first_text(context, COMPANY_SELECTORS, 120)
            location = first_text(context, LOCATION_SELECTORS, 120)
            date_raw = first_text(context, DATE_SELECTORS, 100)
            date_posted = ""
            if date_raw:
                iso = re.search(r"\b(20\d{2})-(\d{2})-(\d{2})\b", date_raw)
                numeric = re.search(r"\b(\d{1,2})[./](\d{1,2})[./](20\d{2})\b", date_raw)
                if iso:
                    date_posted = iso.group(0)
                elif numeric:
                    d, m, y = numeric.groups()
                    date_posted = f"{int(y):04d}-{int(m):02d}-{int(d):02d}"
                else:
                    date_posted = date_raw
            seen.add(key)
            jobs.append({"title": title, "company": company, "location": location,
                         "date_posted": date_posted, "url": href, "source": source["name"]})

    # Some listings embed the job links in JSON/JS rather than ordinary anchors.
    raw_urls = re.findall(r"(?:https?:)?//[^\"\'<>\\ ]+|(?:/)?(?:en/(?:jobs?|node)|nabidky-prace)/[^\"\'<>\\ ]+", html, flags=re.I)
    for raw in raw_urls:
        candidate = html_lib.unescape(raw).replace(r"\/", "/").strip(" \"\'\\,;)")
        if candidate.startswith("//"):
            candidate = "https:" + candidate
        candidate = abs_url(candidate, page_url)
        candidate = canonical(candidate)
        if not candidate or not detail_link(candidate, source):
            continue
        if candidate in seen:
            continue
        seen.add(candidate)
        slug = urlparse(candidate).path.rstrip("/").split("/")[-1]
        if slug.isdigit():
            title = f"Grafton job {slug}"
        else:
            title = re.sub(r"--?\d+$", "", slug).replace("-", " ").replace("_", " ").title()
        jobs.append({"title": title or slug, "company": "", "location": "",
                     "date_posted": "", "url": candidate, "source": source["name"]})
    return jobs, soup


def fetch_html(url, source):
    """Render Grafton in Chromium every time; use requests for Manpower."""
    if not source["name"].startswith("grafton"):
        response = fetch_with_retry(url)
        return response.text

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError(
            "Grafton listing pages need JavaScript rendering. Run `pip install playwright` "
            "and `python -m playwright install chromium`."
        ) from exc

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        page = browser.new_page(user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ))
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        try:
            page.wait_for_load_state("networkidle", timeout=15000)
        except Exception:
            pass
        # Wait for Vue job list to appear
        try:
            page.wait_for_selector(".job-item-wrapper, .jobs-listing-wrapper", timeout=15000)
        except Exception:
            pass
        page.wait_for_timeout(2000)

        # Follow visible pagination/load-more controls; save every rendered state.
        snapshots, snapshot_hashes = [], set()
        for _ in range(40):
            content = page.content()
            digest = hash(content)
            if digest not in snapshot_hashes:
                snapshots.append(content)
                snapshot_hashes.add(digest)

            # Grafton pagination: ul.pagination li.active + li a  OR  a:has-text("Next")
            # Try multiple strategies
            control = None
            # Strategy 1: Next button in footer
            try:
                # Find the "Next" link that is NOT disabled
                next_candidates = page.locator("ul.className li:not(.disabled) a:has-text('Next'), .jobs-listing-footer a:has-text('Next')")
                if next_candidates.count() > 0 and next_candidates.last.is_visible():
                    # Check if parent li is disabled - if disabled, we are on last page
                    parent_disabled = page.locator("ul.className li.disabled a:has-text('Next')")
                    if parent_disabled.count() == 0:
                        control = next_candidates.last
            except Exception:
                pass

            if control is None:
                try:
                    # Strategy 2: next page number after active
                    next_page = page.locator("ul.className li.active + li a, .jobs-listing-footer li.active + li a")
                    if next_page.count() > 0 and next_page.first.is_visible():
                        control = next_page.first
                except Exception:
                    pass

            if control is None:
                try:
                    # Generic fallback from original code
                    generic = page.locator(
                        "a[rel='next'], button:has-text('Next'), a:has-text('Next'), "
                        "button:has-text('Load more'), button:has-text('Show more'), "
                        "a[aria-label*='Next'], button[aria-label*='Next']"
                    ).last
                    if generic.count() > 0 and generic.is_visible() and not generic.is_disabled():
                        control = generic
                except Exception:
                    pass

            if control is None:
                break

            try:
                if not control.count() or not control.is_visible() or control.is_disabled():
                    break
                control.click(timeout=3000)
                try:
                    page.wait_for_load_state("networkidle", timeout=8000)
                except Exception:
                    pass
                try:
                    page.wait_for_selector(".job-item-wrapper", timeout=8000)
                except Exception:
                    pass
                page.wait_for_timeout(1200)
            except Exception:
                break

        content = page.content()
        if hash(content) not in snapshot_hashes:
            snapshots.append(content)
        browser.close()
    return "\n".join(snapshots)

def pagination_urls(soup, current_url, source):
    """Find valid pagination links; preserve the original Manpower filters."""
    # For Grafton, pagination is handled entirely inside fetch_html() via Playwright
    # clicking. The footer uses <a> without href (Vue handlers), so returning [] avoids
    # queueing invalid URLs.
    if source["name"].startswith("grafton"):
        return []

    candidates = []
    for a in soup.select("a[href]"):
        href = abs_url(a.get("href"), current_url)
        if not href or source["domain"] not in urlparse(href).netloc.lower():
            continue
        label = norm(" ".join([a.get_text(" ", strip=True), a.get("aria-label", ""), a.get("title", "")])).lower()
        rel = " ".join(a.get("rel", [])).lower()
        is_next = ("next" in rel or "next" in label or "další" in label or
                   "older" in label or "›" in label or "»" in label or label in {">", "→"})
        is_page = bool(re.search(r"(?:page|strana|stranka|pageno|pager)[=/\-]?\d+", href, re.I))
        if (is_next or is_page) and not detail_link(href, source):
            candidates.append(href)

    # Manpower's CMS sometimes emits malformed pagination links that drop the
    # leading /f/ filter segment. Ignore those and derive the next page from
    # the user's exact filtered URL instead.
    if source["name"].startswith("manpower"):
        base = source["start_url"].rstrip("/")
        # FIXED: previously second match overwrote first
        m1 = re.search(r"/f/stranka/(\d+)/?$", current_url)
        m2 = re.search(r"/stranka/(\d+)/?$", current_url)
        match = m1 or m2
        current_page = int(match.group(1)) if match else 1
        candidates = [
            base + f"/f/stranka/{current_page + 1}/",
            base + f"/stranka/{current_page + 1}/",
        ]

    out, seen = [], {canonical(current_url)}
    for url in candidates:
        key = canonical(url)
        if key not in seen:
            seen.add(key)
            out.append(url)
    return out

def canonical(url):
    p = urlparse(url)
    query = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True)
             if not k.lower().startswith("utm_") and k.lower() not in {"fbclid", "gclid"}]
    return urlunparse((p.scheme.lower(), p.netloc.lower(), p.path.rstrip("/"), "", urlencode(query), ""))

def scrape_source(source):
    name = source["name"]
    checkpoint = CHECKPOINT_DIR / f"checkpoint_{name}.json"
    if RESUME and checkpoint.exists():
        try:
            cached = json.loads(checkpoint.read_text(encoding="utf-8"))
            expected = source.get("expected_urls")
            if isinstance(cached, list) and cached and expected and len(cached) >= expected:
                print(f"{name}: resumed {len(cached)} jobs from checkpoint")
                return cached
            if isinstance(cached, list) and cached:
                print(f"{name}: checkpoint has only {len(cached)} jobs; rebuilding to reach {expected or 'all'} URLs")
        except Exception as exc:
            print(f"{name}: checkpoint unreadable ({exc}); starting fresh")

    queue = [source["start_url"]]
    queued = {canonical(queue[0])}
    visited, collected, seen_jobs = set(), [], set()
    pages = 0

    while queue and pages < MAX_PAGES_PER_SOURCE:
        url = queue.pop(0)
        key = canonical(url)
        if key in visited:
            continue
        visited.add(key)
        pages += 1
        print(f"{name}: page {pages} -> {url}")
        try:
            html = fetch_html(url, source)
            jobs, soup = extract_listing_jobs(html, url, source)
            if not jobs and pages == 1:
                debug_path = Path(f"debug_{name}.html")
                debug_path.write_text(html, encoding="utf-8")
                anchors = soup.select("a[href]")
                likely = [a.get("href", "") for a in anchors
                          if any(token in a.get("href", "").lower()
                                 for token in ("/en/jobs", "/en/node/", "/en/job/", "/nabidky-prace/"))]
                print(f"  DEBUG: 0 job URLs from {len(anchors)} anchors; saved rendered HTML to {debug_path}")
                if likely:
                    print("  DEBUG: example job-like links: " + repr(likely[:8]))
                # Extra debug for Grafton: count job-item-wrapper
                wrappers = soup.select(".job-item-wrapper")
                if wrappers:
                    print(f"  DEBUG: found {len(wrappers)} .job-item-wrapper but detail_link rejected them")
            new_jobs = []
            for job in jobs:
                job_key = canonical(job["url"])
                if job_key not in seen_jobs:
                    seen_jobs.add(job_key)
                    new_jobs.append(job)
            collected.extend(new_jobs)
            print(f"  {len(jobs)} found, {len(new_jobs)} new")
            save_checkpoint(name, collected)
            for next_url in pagination_urls(soup, url, source):
                next_key = canonical(next_url)
                if next_key not in queued and next_key not in visited:
                    queued.add(next_key)
                    queue.append(next_url)
            if not new_jobs and pages > 1:
                pass
            time.sleep(random.uniform(*DELAY))
        except Exception as exc:
            print(f"  page failed: {exc}")
            import traceback; traceback.print_exc()

    deduped, removed = dedup_jobs(collected)
    filtered = deduped
    save_checkpoint(name, filtered)
    expected = source.get("expected_urls")
    status = f" (target {expected})" if expected else ""
    print(f"{name}: {len(filtered)} retained{status}; {removed} duplicate(s) removed")
    if expected and len(filtered) != expected:
        print(f"WARNING: {name} returned {len(filtered)} URLs, expected {expected}. "
              "Check browser support, site changes, or filter settings.")
    return filtered

def save_outputs(jobs):
    json_path = Path(f"{BASE_NAME}.json")
    csv_path = Path(f"{BASE_NAME}.csv")
    json_path.write_text(json.dumps(jobs, ensure_ascii=False, indent=2), encoding="utf-8")
    fields = ["id", "title", "company", "location", "date_posted", "url", "source"]
    extras = sorted({k for job in jobs for k in job} - set(fields))
    fields += extras
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for job in jobs:
            writer.writerow({field: job.get(field, "") for field in fields})
    print(f"Saved {json_path} ({len(jobs)} jobs)")
    print(f"Saved {csv_path} ({len(jobs)} jobs)")

def main():
    blacklist = reload_blacklist()
    print(f"Title blacklist loaded ({len(blacklist)} terms); URL extraction keeps all jobs")
    all_jobs = []
    for source in SOURCES:
        all_jobs.extend(scrape_source(source))
    final, removed = dedup_jobs(all_jobs)
    save_outputs(final)
    print(f"DONE: {len(final)} unique jobs; {removed} cross-source duplicate(s) removed")

if __name__ == "__main__":
    main()
