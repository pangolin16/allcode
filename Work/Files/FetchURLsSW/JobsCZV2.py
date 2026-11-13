"""
Jobs.cz - Praha full scraper v4
- Single output: only filtered list (all - blacklist)
- Expanded TITLE_BLACKLIST
"""

import re, math, json, time, csv
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from playwright.sync_api import sync_playwright
from collections import Counter

BASE_URL = "https://www.jobs.cz/prace/praha/?education=high&locality%5Bradius%5D=20"

CHUNKS = []
for contract in [["employment_contract"], ["identification_number"], ["agreement"]]:
    for employment in [["full"], ["part"]]:
        label = f"{contract[0][:4].upper()}-{employment[0].upper()}"
        CHUNKS.append({"label": label, "contract": contract, "employment": employment})

JOBS_PER_PAGE = 30
MAX_PAGES_PER_QUERY = 100
MAX_JOBS_PER_QUERY = 3000

# --- BLACKLIST CONFIG - v4 expanded ---
TITLE_BLACKLIST = [

]

def compile_blacklist_patterns(blacklist):
    patterns = []
    for term in blacklist:
        term_clean = term.strip()
        if not term_clean:
            continue
        # For very short acronyms (HR, PR, RTB, CRM, CAD) use word boundaries to avoid false positives
        if len(term_clean) <= 3:
            pat = re.compile(r'\b' + re.escape(term_clean) + r'\b', re.IGNORECASE)
        else:
            pat = re.compile(re.escape(term_clean), re.IGNORECASE)
        patterns.append((term_clean, pat))
    return patterns

BLACKLIST_PATTERNS = compile_blacklist_patterns(TITLE_BLACKLIST)

def is_blacklisted(title):
    if not title:
        return False, None
    for original_term, pat in BLACKLIST_PATTERNS:
        if pat.search(title):
            return True, original_term
    return False, None

def filter_jobs_by_title(jobs):
    kept, removed = [], []
    for j in jobs:
        blocked, matched = is_blacklisted(j.get("title",""))
        if blocked:
            jc = j.copy()
            jc["_blocked_by"] = matched
            removed.append(jc)
        else:
            kept.append(j)
    return kept, removed

def build_url(base_url, contract_list, employment_list, page=1):
    parsed = urlparse(base_url)
    qs = parse_qs(parsed.query)
    qs["contract[]"] = contract_list
    qs["employment[]"] = employment_list
    if page > 1:
        qs["page"] = [str(page)]
    else:
        qs.pop("page", None)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, urlencode(qs, doseq=True), parsed.fragment))

def extract_total_jobs(page):
    try:
        text = page.locator("body").inner_text(timeout=5000)
        m = re.search(r"Našli jsme\s+([\d\s]+)\s+nabídek", text)
        if m:
            return int(m.group(1).replace(" ", "").replace("\xa0", ""))
    except:
        pass
    return None

def extract_jobs_from_page(page):
    jobs = []
    try:
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(800)
    except:
        pass
    selectors = ['[data-test="advert-card"]','.search-list__item','[data-test-id="job-card"]','.job-card','article']
    cards = []
    for sel in selectors:
        try:
            found = page.locator(sel).all()
            if len(found) > 3:
                cards = found
                break
        except:
            continue
    if not cards:
        cards = page.locator('a[href*="/rpd/"]').all()
    for card in cards:
        try:
            text = card.inner_text()
            try:
                link = card.locator('a').first.get_attribute('href')
                if link and not link.startswith('http'):
                    link = "https://www.jobs.cz" + link
            except:
                try:
                    link = card.get_attribute('href')
                except:
                    link = ""
                if link and not link.startswith('http'):
                    link = "https://www.jobs.cz" + link
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            if len(lines) < 2:
                continue
            title = lines[0][:200]
            company = ""
            for l in lines[1:4]:
                if any(x in l for x in ["s.r.o.","a.s.","spol.","s.r.","Czech"]):
                    company = l
                    break
            job_id = ""
            if link:
                m = re.search(r'/rpd/(\d+)', link)
                if m:
                    job_id = m.group(1)
            if title and len(title) > 5:
                jobs.append({"id": job_id, "title": title, "company": company, "url": link, "raw": text[:500]})
        except:
            continue
    return jobs

def scrape_chunk(playwright, chunk, base_url):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        locale="cs-CZ"
    )
    page = context.new_page()
    url_page_1 = build_url(base_url, chunk["contract"], chunk["employment"], page=1)
    print(f"\n=== CHUNK {chunk['label']}: {chunk['contract']} {chunk['employment']}")
    page.goto(url_page_1, wait_until="domcontentloaded", timeout=60000)
    try:
        page.wait_for_selector('a[href*="/rpd/"]', timeout=12000)
    except:
        print("  [WARN] No job links")
    total = extract_total_jobs(page)
    pages = MAX_PAGES_PER_QUERY
    if total:
        pages = min(math.ceil(total / JOBS_PER_PAGE), MAX_PAGES_PER_QUERY)
        print(f"  Site says total: {total} -> will scrape {pages} pages")
    all_jobs = []
    jobs = extract_jobs_from_page(page)
    print(f"  Page 1: {len(jobs)}")
    all_jobs.extend(jobs)
    for p in range(2, pages+1):
        url = build_url(base_url, chunk["contract"], chunk["employment"], page=p)
        print(f"  Fetching page {p}/{pages}...")
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            try:
                page.wait_for_load_state("networkidle", timeout=5000)
            except:
                pass
            page.wait_for_timeout(1500)
            jobs = extract_jobs_from_page(page)
            print(f"    -> {len(jobs)}")
            if not jobs:
                page.wait_for_timeout(3000)
                jobs = extract_jobs_from_page(page)
                if not jobs:
                    print("    Empty, stop")
                    break
            all_jobs.extend(jobs)
        except Exception as e:
            print(f"    Error {e}")
            break
    browser.close()
    raw_total = len(all_jobs)
    dedup = {}
    for j in all_jobs:
        key = j["id"] or j["url"]
        if key and key not in dedup:
            dedup[key] = j
    unique_total = len(dedup)
    kept, removed = filter_jobs_by_title(list(dedup.values()))
    print(f"  [STATS {chunk['label']}] raw:{raw_total} dedup:{unique_total} after_blacklist:{len(kept)} removed:{len(removed)}")
    return kept, removed, raw_total, unique_total, total

def main():
    all_results = []
    all_removed = []
    grand_raw = 0
    grand_dedup = 0
    grand_kept_per_chunk = 0
    site_totals = []

    with sync_playwright() as p:
        for chunk in CHUNKS:
            kept, removed, raw_count, dedup_count, site_total = scrape_chunk(p, chunk, BASE_URL)
            all_results.extend(kept)
            all_removed.extend(removed)
            grand_raw += raw_count
            grand_dedup += dedup_count
            grand_kept_per_chunk += len(kept)
            if site_total:
                site_totals.append(site_total)
            time.sleep(2)

    final = {}
    for j in all_results:
        key = j["id"] or j["url"]
        if key and key not in final:
            final[key] = j
    final_list = list(final.values())
    final_list, extra = filter_jobs_by_title(final_list)
    all_removed.extend(extra)

    intra_dup = grand_raw - grand_dedup
    blacklist_total = len(all_removed)
    cross_dup = grand_kept_per_chunk - len(final_list)

    print(f"\n{'='*70}")
    print(f"FINAL LINK EXTRACTION SUMMARY v4 - SINGLE FILTERED LIST")
    print(f"{'='*70}")
    print(f"Site reported total (sum of 6 chunks): {sum(site_totals) if site_totals else 'unknown'}")
    print(f"Official single-query total: 4107")
    print(f"Total BEFORE any dedup: {grand_raw}")
    print(f"Total AFTER chunk dedup: {grand_dedup} (intra-dup: {intra_dup})")
    print(f"Total AFTER blacklist per chunk: {grand_kept_per_chunk}")
    print(f"Total FINAL (global dedup + blacklist): {len(final_list)}")
    print(f"  -> Cross-chunk dups: {cross_dup}")
    print(f"  -> Total removed by blacklist: {blacklist_total}")
    print(f"{'='*70}")
    blocked_counter = Counter([r["_blocked_by"] for r in all_removed])
    for term, cnt in blocked_counter.most_common():
        print(f"  {term}: {cnt}")
    print(f"{'='*70}\n")

    # --- SINGLE OUTPUT ONLY: filtered list (all - blacklist) ---
    with open("jobs_praha2.json", "w", encoding="utf-8") as f:
        json.dump(final_list, f, ensure_ascii=False, indent=2)

    with open("jobs_praha2.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id","title","company","url"])
        w.writeheader()
        for j in final_list:
            w.writerow({k: j.get(k,"") for k in ["id","title","company","url"]})

    print(f"Saved SINGLE filtered list: jobs_praha2.json ({len(final_list)} jobs)")
    print(f"Saved SINGLE filtered list: jobs_praha2.csv ({len(final_list)} jobs)")

if __name__ == "__main__":
    main()
