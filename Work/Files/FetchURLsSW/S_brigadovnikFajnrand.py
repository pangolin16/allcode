
"""MultiSourceBR-Agent - corrected job-title/date scraper.

Outputs:
    S_brigadovnikFajnrand.json
    S_brigadovnikFajnrand.csv

Uses scraper_utils.py in the same directory.
Re-scrapes incompatible checkpoints.
"""

import csv
import json
import random
import re
import time
from pathlib import Path
from urllib.parse import urljoin, urlparse, urldefrag

from scraper_utils import (
    CHECKPOINT_DIR,
    TITLE_BLACKLIST,
    TITLE_BLACKLIST_FILE,
    dedup_jobs,
    fetch_with_retry,
    get_soup,
    is_blacklisted,
    reload_blacklist,
    save_checkpoint,
)

TITLE_BLACKLIST_JSON = Path(__file__).parent / "Title_Blacklist.json"
BASE_NAME = Path(__file__).stem
RESUME = True
MAX_PAGES = 49

CZECH_MONTHS = {
    "ledna": 1, "února": 2, "unora": 2, "března": 3,
    "brezna": 3, "dubna": 4, "května": 5, "kvetna": 5,
    "června": 6, "cervna": 6, "července": 7, "cervence": 7,
    "srpna": 8, "září": 9, "zari": 9, "října": 10,
    "rijna": 10, "listopadu": 11, "prosince": 12,
}

DESCRIPTION_START_RE = re.compile(
    r"\b(?:"
    r"hledáme|hledáš|hledáte|nabízíme|něco o nás|"
    r"co budeš dělat|co budete dělat|co tě čeká|co vás čeká|"
    r"náplň práce|pracovní náplň|zamysleli jste se|"
    r"do našeho týmu hledáme|do našeho týmu přijmeme|"
    r"pokud máte|pokud tě|přidejte se|přidej se|"
    r"naším cílem|jedná se o|baví tě|láká tě|projev zájem|"
    r"budete mít na starosti|vaší rolí bude|vaším úkolem|"
    r"jsme .*? společnost|jako brigádník"
    r")\b",
    re.IGNORECASE,
)

TITLE_SELECTORS = (
    "h1", "h2", "h3", "h4",
    "[class*='job-title']", "[class*='job_title']",
    "[class*='title']", "[class*='nazev']",
    "[class*='nadpis']", "[class*='position-name']",
)

LOCATION_SELECTORS = (
    "[class*='location']", "[class*='lokalita']",
    "[class*='mesto']", "[itemprop='jobLocation']",
)

COMPANY_SELECTORS = (
    "[class*='company']", "[class*='employer']",
    "[class*='firma']", "[itemprop='hiringOrganization']",
)

BRIGADOVNIK_HOSTS = {"brigadovnik.cz", "www.brigadovnik.cz"}
FAJN_HOSTS = {"fajn-brigady.cz", "www.fajn-brigady.cz"}
RANDSTAD_HOSTS = {"randstad.cz", "www.randstad.cz"}

print(
    f"Using TITLE_BLACKLIST from {TITLE_BLACKLIST_FILE}: "
    f"{len(TITLE_BLACKLIST)} terms"
)


def _norm_text(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _normalized_url(href, base_url):
    """Resolve a URL, discard fragments, and normalize trailing slashes."""
    href = _norm_text(href)
    if not href:
        return ""

    absolute = urljoin(base_url, href)
    absolute, _fragment = urldefrag(absolute)
    parsed = urlparse(absolute)

    if parsed.scheme.lower() not in ("http", "https"):
        return ""

    host = parsed.netloc.lower()
    if not host:
        return ""

    # Keep query strings on detail URLs; they may contain meaningful IDs.
    path = parsed.path.rstrip("/") or "/"
    return parsed._replace(
        scheme="https",
        netloc=host,
        path=path,
        fragment="",
    ).geturl()


def _url_key(url):
    """Stable key for URL deduplication."""
    parsed = urlparse(_norm_text(url))
    host = parsed.netloc.lower().removeprefix("www.")
    path = parsed.path.rstrip("/").lower() or "/"
    return host, path, parsed.query


def _date_to_iso(day, month, year):
    try:
        from datetime import date
        return date(int(year), int(month), int(day)).isoformat()
    except (TypeError, ValueError):
        return ""


def _extract_posted_date(text, source=""):
    """Return a labeled posting date as YYYY-MM-DD, or empty if unknown."""
    text = _norm_text(text)

    labeled = re.search(
        r"(?:nově\s+přidáno|uveřejněno|uverejneno|"
        r"publikováno|publikovano)\s*"
        r"(\d{1,2})[./](\d{1,2})[./](\d{4})",
        text,
        re.IGNORECASE,
    )
    if labeled:
        return _date_to_iso(*labeled.groups())

    labeled_czech = re.search(
        r"(?:uveřejněno|uverejneno|publikováno|publikovano)\s+"
        r"(\d{1,2})\s+([a-zá-ž]+)\s+(\d{4})",
        text,
        re.IGNORECASE,
    )
    if labeled_czech:
        day, month_name, year = labeled_czech.groups()
        month = CZECH_MONTHS.get(month_name.lower())
        return _date_to_iso(day, month, year) if month else ""

    if source == "fajnbrigady":
        leading = re.match(
            r"^\s*(\d{1,2})[./](\d{1,2})[./](\d{4})\b",
            text,
        )
        if leading:
            return _date_to_iso(*leading.groups())

    return ""


def _clean_title_text(text):
    """Remove badges, dates, descriptions, and trailing metadata."""
    text = _norm_text(text)
    if not text:
        return ""

    text = re.sub(r"^(?:top\s+)+", "", text, flags=re.IGNORECASE)
    text = re.sub(
        r"^nově\s+přidáno\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r"^\d{1,2}[./]\d{1,2}[./]\d{4}\s*",
        "",
        text,
    )
    text = _norm_text(text)

    text = re.sub(
        r"(?<=[^\s])(?=(?:hledáme|hledáš|hledáte|nabízíme|"
        r"něco o nás|co budeš dělat|co budete dělat|"
        r"co tě čeká|co vás čeká|náplň práce|pracovní náplň|"
        r"zamysleli jste se|pokud máte|přidejte se|přidej se|"
        r"naším cílem|jedná se o|baví tě|láká tě|projev zájem|"
        r"budete mít na starosti|vaší rolí bude|vaším úkolem)\b)",
        " ",
        text,
        flags=re.IGNORECASE,
    )
    text = _norm_text(text)

    matches = [
        match for match in DESCRIPTION_START_RE.finditer(text)
        if match.start() >= 18
    ]
    if matches:
        text = text[:matches[0].start()].strip(
            " \t\r\n-|–—:;,.·"
        )

    text = re.sub(r"\s*[|•]\s*.*$", "", text)
    text = _norm_text(text).strip(" -–—|:;,. ")

    if len(text) > 180:
        shortened = text[:180]
        if " " in shortened:
            shortened = shortened.rsplit(" ", 1)[0]
        text = shortened.rstrip(" -–—|:;,.") + "…"

    return text


def _title_from_anchor(anchor):
    """Prefer a semantic title node over a card's complete text."""
    parent_heading = anchor.find_parent(["h1", "h2", "h3", "h4"])
    if parent_heading:
        candidate = _clean_title_text(
            parent_heading.get_text(" ", strip=True)
        )
        if 3 <= len(candidate) <= 180:
            return candidate

    for selector in TITLE_SELECTORS:
        try:
            descendants = anchor.select(selector)
        except Exception:
            descendants = []

        candidates = []
        for node in descendants:
            candidate = _clean_title_text(
                node.get_text(" ", strip=True)
            )
            if not 3 <= len(candidate) <= 180:
                continue
            if re.search(
                r"\b(?:informace o pracovním místě|"
                r"požadujeme|nabízíme)\b",
                candidate,
                re.IGNORECASE,
            ):
                continue
            candidates.append(candidate)

        if candidates:
            return min(candidates, key=len)

    label = _clean_title_text(
        anchor.get("aria-label") or anchor.get("title") or ""
    )
    if 3 <= len(label) <= 180:
        return label

    return _clean_title_text(anchor.get_text(" ", strip=True))


def _context_node(anchor, max_ancestors=7):
    """Find a compact ancestor that may contain listing metadata."""
    best = anchor
    node = anchor

    for _ in range(max_ancestors):
        node = getattr(node, "parent", None)
        if node is None or not getattr(node, "get_text", None):
            break

        text = _norm_text(node.get_text(" ", strip=True))
        if (
            len(text) <= 3500
            and re.search(
                r"(?:nově\s+přidáno|uveřejněno|uverejneno)",
                text,
                re.IGNORECASE,
            )
        ):
            return node

        if len(text) <= 500:
            best = node

    return best


def _metadata_text(root, selectors):
    if root is None:
        return ""

    for selector in selectors:
        try:
            nodes = root.select(selector)
        except Exception:
            nodes = []

        for node in nodes:
            value = _norm_text(node.get_text(" ", strip=True))
            if value and len(value) <= 120:
                return value

    return ""


def _fajn_trailing_metadata(text):
    """Fallback for Fajn-brigady cards with plain trailing metadata."""
    text = _norm_text(text)
    match = re.search(
        r"(Praha(?:\s+\d{1,2})?)\s*"
        r"([A-ZÁ-Ž][A-Za-zÁ-ž0-9&'’()., -]{1,80}?"
        r"(?:s\.r\.o\.|a\.s\.|s\.p\.|GmbH|Ltd\.?|SE))\s*$",
        text,
        re.IGNORECASE,
    )
    if match:
        return _norm_text(match.group(2)), _norm_text(match.group(1))
    return "", ""


def parse_brigadovnik(html):
    """Extract Brigadovnik job-detail URLs from listing cards."""
    soup = get_soup(html)
    jobs = []
    seen = set()
    base_url = "https://www.brigadovnik.cz"

    excluded_paths = {
        "/", "/chcibrigadu", "/nabizimbrigadu",
        "/prihlaseni", "/registrace",
    }

    excluded_fragments = (
        "/profil-firmy/", "/clanek/", "/podminky",
        "/kontakt", "/registrace", "/prihlaseni",
        "/inzerce", "/blog/",
    )

    # First inspect likely job links, then inspect links marked as detail actions.
    selectors = (
        "a[href*='/brigada/']",
        "a[href*='/brigady/']",
        "a[href*='/detail-brigady/']",
        "a[href]",
    )

    anchors = []
    anchor_ids = set()
    for selector in selectors:
        for anchor in soup.select(selector):
            identity = id(anchor)
            if identity not in anchor_ids:
                anchors.append(anchor)
                anchor_ids.add(identity)

    for anchor in anchors:
        href = _normalized_url(anchor.get("href", ""), base_url)
        if not href:
            continue

        parsed = urlparse(href)
        host = parsed.netloc.lower()
        if host not in BRIGADOVNIK_HOSTS:
            continue

        path = parsed.path.rstrip("/") or "/"
        path_lower = path.lower()

        if path_lower in excluded_paths:
            continue
        if any(fragment in path_lower for fragment in excluded_fragments):
            continue

        link_text = _norm_text(anchor.get_text(" ", strip=True))
        aria_text = _norm_text(
            anchor.get("aria-label") or anchor.get("title") or ""
        )
        combined_label = f"{link_text} {aria_text}".casefold()

        # Accept known detail routes and links explicitly labeled as job details.
        is_detail = (
            "/brigada/" in path_lower
            or "/brigady/" in path_lower
            or "/detail-brigady/" in path_lower
            or bool(re.search(
                r"/(?:brigada|brigady)?/?\d+(?:[-/]|$)",
                path_lower,
            ))
            or "detail brigády" in combined_label
            or "detail brigady" in combined_label
        )

        if not is_detail:
            continue

        key = _url_key(href)
        if key in seen:
            continue

        title = _title_from_anchor(anchor)

        # If the anchor is a generic detail button, recover the card heading.
        generic_titles = {
            "detail brigády", "detail brigady",
            "více informací", "zobrazit více",
            "přihlásit se", "chci brigádu",
        }
        if title.casefold() in generic_titles or len(title) < 4:
            card = anchor.find_parent(["article", "li"])
            if card is None:
                for _ in range(4):
                    parent = getattr(anchor, "parent", None)
                    if parent is None or not getattr(parent, "get_text", None):
                        break
                    anchor = anchor
                    parent_text = _norm_text(parent.get_text(" ", strip=True))
                    if len(parent_text) <= 1200:
                        card = parent
                        break
                    anchor = anchor

            if card:
                heading = card.find(["h1", "h2", "h3", "h4"])
                if heading:
                    title = _clean_title_text(
                        heading.get_text(" ", strip=True)
                    )

        if not title or len(title) < 4:
            continue
        if title.casefold() in generic_titles:
            continue

        seen.add(key)
        jobs.append({
            "title": title,
            "url": href,
            "company": "",
            "location": "",
            "date_posted": "",
            "source": "brigadovnik",
        })

    return jobs


def parse_fajnbrigady(html):
    """Parse Fajn-brigady detail links and keep title/date separate."""
    soup = get_soup(html)
    jobs = []
    seen = set()

    for anchor in soup.select("a[href*='/brigady/']"):
        href = _normalized_url(
            anchor.get("href", ""),
            "https://www.fajn-brigady.cz",
        )
        if not href:
            continue

        parsed = urlparse(href)
        if parsed.netloc.lower() not in FAJN_HOSTS:
            continue

        path = parsed.path
        if not re.search(
            r"/\d{5,}-[a-z0-9-]+/?$",
            path,
            re.IGNORECASE,
        ):
            continue

        key = _url_key(href)
        if key in seen:
            continue

        context = _context_node(anchor)
        context_text = (
            _norm_text(context.get_text(" ", strip=True))
            if context else _norm_text(anchor.get_text(" ", strip=True))
        )

        title = _title_from_anchor(anchor)
        date_posted = _extract_posted_date(
            context_text or anchor.get_text(" ", strip=True),
            "fajnbrigady",
        )
        location = _metadata_text(context, LOCATION_SELECTORS)
        company = _metadata_text(context, COMPANY_SELECTORS)

        if not company or not location:
            fallback_company, fallback_location = (
                _fajn_trailing_metadata(context_text)
            )
            company = company or fallback_company
            location = location or fallback_location

        if len(title) > 130 or re.search(
            r"nově\s+přidáno|uveřejněno",
            title,
            re.IGNORECASE,
        ):
            title = _clean_title_text(context_text)

        if not title or len(title) < 4:
            continue

        seen.add(key)
        jobs.append({
            "title": title,
            "url": href,
            "company": company,
            "location": location,
            "date_posted": date_posted,
            "source": "fajnbrigady",
        })

    return jobs


def parse_randstad(html):
    """Parse Randstad detail URLs ending in an ID such as _t-10638."""
    soup = get_soup(html)
    jobs = []
    seen = set()

    for anchor in soup.select("a[href*='_t-']"):
        href = _normalized_url(
            anchor.get("href", ""),
            "https://www.randstad.cz",
        )
        if not href:
            continue

        parsed = urlparse(href)
        if parsed.netloc.lower() not in RANDSTAD_HOSTS:
            continue
        if not re.search(r"_t-\d+/?$", parsed.path, re.IGNORECASE):
            continue

        key = _url_key(href)
        if key in seen:
            continue

        context = _context_node(anchor)
        context_text = (
            _norm_text(context.get_text(" ", strip=True))
            if context else _norm_text(anchor.get_text(" ", strip=True))
        )

        title = _title_from_anchor(anchor)
        date_posted = _extract_posted_date(context_text, "randstad")
        location = _metadata_text(context, LOCATION_SELECTORS) or "Praha"

        if not title or len(title) < 4 or len(title) > 180:
            continue
        if title.lower() in {
            "ukázat více o pracovní nabídce",
            "zobrazit více",
            "více informací",
        }:
            continue

        seen.add(key)
        jobs.append({
            "title": title,
            "url": href,
            "company": _metadata_text(context, COMPANY_SELECTORS),
            "location": location,
            "date_posted": date_posted,
            "source": "randstad",
        })

    return jobs


def build_brigadovnik_url(page: int) -> str:
    """Build Brigadovnik's Prague listing URL."""
    base = "https://www.brigadovnik.cz/chcibrigadu"
    if page == 1:
        return f"{base}?kraj=Praha"
    return f"{base}?kraj=Praha&page={page}"


def build_fajnbrigady_url(page: int) -> str:
    if page == 1:
        return (
            "https://www.fajn-brigady.cz/"
            "vysledek.html?s_sekce=1&id_lokality=kraj-19"
        )
    offset = (page - 1) * 40
    return (
        "https://www.fajn-brigady.cz/vysledek.html"
        f"?s={offset}&s_sekce=1&id_lokality=kraj-19&from=vypis"
    )


def build_fajnbrigady_url_alt(page: int) -> str:
    offset = (page - 1) * 40
    if page == 1:
        return "https://www.fajn-brigady.cz/brigady/okres-praha/"
    return (
        "https://www.fajn-brigady.cz/brigady/okres-praha/"
        f"?s={offset}"
    )


def build_randstad_url(page: int) -> str:
    base = "https://www.randstad.cz/jobs/hlavni-mesto-praha/praha/"
    return base if page == 1 else f"{base}page-{page}/"


SOURCES = [
    {
        "name": "brigadovnik",
        "url_builder": build_brigadovnik_url,
        "parser": parse_brigadovnik,
        "per_page": 30,
    },
    {
        "name": "fajnbrigady",
        "url_builder": build_fajnbrigady_url,
        "parser": parse_fajnbrigady,
        "per_page": 60,
    },
    {
        "name": "randstad",
        "url_builder": build_randstad_url,
        "parser": parse_randstad,
        "per_page": 30,
    },
]


def get_url_for_page(src, page: int) -> str:
    if callable(src.get("url_builder")):
        return src["url_builder"](page)

    offset = (page - 1) * src.get("per_page", 20)
    return src["url_template"].format(page=page, offset=offset)


def _checkpoint_is_stale(source_name, data):
    """Reject empty, malformed, or incompatible checkpoints."""
    if not isinstance(data, list) or not data:
        return True

    for job in data:
        if not isinstance(job, dict):
            return True

        title = _norm_text(job.get("title", ""))
        url = _norm_text(job.get("url", ""))

        if not title or not url:
            return True

        parsed = urlparse(url)
        host = parsed.netloc.lower()
        path = parsed.path.lower()

        if source_name == "brigadovnik":
            if host not in BRIGADOVNIK_HOSTS:
                return True
            if path.rstrip("/") in {
                "", "/chcibrigadu", "/nabizimbrigadu",
            }:
                return True
            if job.get("source") != "brigadovnik":
                return True

        elif source_name == "fajnbrigady":
            if host not in FAJN_HOSTS:
                return True
            if re.search(
                r"nově\s+přidáno|\b\d{1,2}[./]\d{1,2}[./]\d{4}\b",
                title,
                re.IGNORECASE,
            ):
                return True
            if len(title) > 180:
                return True

        elif source_name == "randstad":
            if host not in RANDSTAD_HOSTS:
                return True
            if not re.search(r"_t-\d+/?$", parsed.path, re.IGNORECASE):
                return True

    return False


def _cleanup_extra_outputs(base_name):
    patterns = [
        f"{base_name}_incremental.json",
        f"{base_name}_filtered.json",
        f"{base_name}_filtered.csv",
        f"{base_name}_*_temp.json",
    ]

    for pattern in patterns:
        for path in Path(".").glob(pattern):
            if path.name in {
                f"{base_name}.json",
                f"{base_name}.csv",
            }:
                continue
            try:
                path.unlink()
                print(f"  cleaned extra: {path}")
            except OSError:
                pass


def _save_final_one_json_one_csv(jobs, base_name):
    json_path = Path(f"{base_name}.json")
    csv_path = Path(f"{base_name}.csv")

    json_path.write_text(
        json.dumps(jobs, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Saved: {json_path} ({len(jobs)} jobs)")

    preferred = [
        "id", "title", "company", "location",
        "date_posted", "url", "source",
    ]
    keys = sorted({key for job in jobs for key in job.keys()})
    ordered = [key for key in preferred if key in keys]
    ordered += [key for key in keys if key not in preferred]

    if not ordered:
        ordered = preferred

    with csv_path.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=ordered,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(
            {key: job.get(key, "") for key in ordered}
            for job in jobs
        )

    print(f"Saved: {csv_path} ({len(jobs)} jobs)")


def main():
    active_blacklist = reload_blacklist()
    print(f"TITLE_BLACKLIST active ({len(active_blacklist)} terms)")
    all_jobs = []

    for src in SOURCES:
        name = src["name"]
        checkpoint = CHECKPOINT_DIR / f"checkpoint_{name}.json"

        if RESUME and checkpoint.exists():
            try:
                cached = json.loads(
                    checkpoint.read_text(encoding="utf-8")
                )
                if cached and not _checkpoint_is_stale(name, cached):
                    all_jobs.extend(cached)
                    print(
                        f"{name}: loaded compatible checkpoint "
                        f"({len(cached)} jobs)"
                    )
                    continue

                if cached:
                    print(
                        f"{name}: old/incompatible checkpoint; "
                        "re-scraping"
                    )
            except (OSError, json.JSONDecodeError) as exc:
                print(
                    f"{name}: could not load checkpoint ({exc}); "
                    "re-scraping"
                )

        collected = []
        seen_urls = set()
        consecutive_empty_pages = 0

        for page in range(1, MAX_PAGES + 1):
            try:
                url = get_url_for_page(src, page)
                print(f"{name} page {page} -> {url}")

                response = fetch_with_retry(url)
                html = (
                    response.text
                    if hasattr(response, "text")
                    else str(response)
                )
                parsed_jobs = src["parser"](html)
                print(f"  -> found {len(parsed_jobs)} raw jobs")

                if name == "brigadovnik":
                    for job in parsed_jobs[:5]:
                        print(f"     sample URL: {job['url']}")

                if (
                    not parsed_jobs
                    and name == "fajnbrigady"
                    and page == 1
                ):
                    alt_url = build_fajnbrigady_url_alt(page)
                    print(f"  -> trying canonical fallback {alt_url}")
                    fallback_response = fetch_with_retry(alt_url)
                    fallback_html = (
                        fallback_response.text
                        if hasattr(fallback_response, "text")
                        else str(fallback_response)
                    )
                    parsed_jobs = src["parser"](fallback_html)
                    print(
                        f"  -> fallback found {len(parsed_jobs)} raw jobs"
                    )

                if not parsed_jobs:
                    consecutive_empty_pages += 1
                    # A single empty page can be a transient response.
                    if (
                        name in {"brigadovnik", "randstad"}
                        and consecutive_empty_pages < 2
                    ):
                        time.sleep(random.uniform(0.8, 1.5))
                        continue
                    break

                consecutive_empty_pages = 0
                new_jobs = []

                for job in parsed_jobs:
                    url_key = _url_key(job.get("url", ""))
                    if url_key and url_key not in seen_urls:
                        seen_urls.add(url_key)
                        new_jobs.append(job)

                if not new_jobs:
                    print(
                        "  -> no new URLs on this page; "
                        "stopping pagination"
                    )
                    break

                collected.extend(new_jobs)
                save_checkpoint(name, collected)
                time.sleep(random.uniform(0.8, 1.6))

            except Exception as exc:
                print(f"{name} page {page} failed: {exc}")

                if collected:
                    break

                if name == "randstad" and page < 3:
                    time.sleep(random.uniform(1.0, 2.0))
                    continue

                break

        deduped, removed = dedup_jobs(collected)
        filtered = [
            job for job in deduped
            if not is_blacklisted(job.get("title", ""))
        ]

        save_checkpoint(name, filtered)
        all_jobs.extend(filtered)

        print(
            f"{name}: {len(filtered)} jobs after dedup/filter "
            f"(removed {removed} duplicates)"
        )

    final, removed = dedup_jobs(all_jobs)
    _cleanup_extra_outputs(BASE_NAME)
    _save_final_one_json_one_csv(final, BASE_NAME)

    brigadovnik_count = sum(
        1 for job in final
        if job.get("source") == "brigadovnik"
    )
    print(
        f"\nDONE: {BASE_NAME}.json and {BASE_NAME}.csv | "
        f"total {len(final)} jobs | "
        f"Brigadovnik {brigadovnik_count} | "
        f"final duplicates removed {removed}"
    )
    print(f"Blacklist source: {TITLE_BLACKLIST_JSON}")


if __name__ == "__main__":
    main()
