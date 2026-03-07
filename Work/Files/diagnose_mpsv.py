"""
Run this standalone to diagnose why jobs aren't loading.
Usage: python diagnose_mpsv.py
"""

import requests
import urllib3
import json
import sys

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

URL = "https://data.mpsv.cz/od/soubory/volna-mista/volna-mista.json"

print("=" * 60)
print("MPSV API Diagnostic Tool")
print("=" * 60)

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json',
})

# ── Step 1: Basic connectivity ──────────────────────────────
print("\n[1] Testing connectivity...")
try:
    response = session.get(URL, timeout=30, verify=False, allow_redirects=True)
    print(f"    ✅ HTTP {response.status_code}")
    print(f"    Content-Type : {response.headers.get('Content-Type', 'N/A')}")
    print(f"    Content-Length: {response.headers.get('Content-Length', 'N/A')}")
    print(f"    Actual bytes : {len(response.content)}")
    print(f"    Final URL    : {response.url}")
except Exception as e:
    print(f"    ❌ Connection failed: {e}")
    sys.exit(1)

# ── Step 2: Check if response looks like JSON ───────────────
print("\n[2] Checking content format...")
text = response.text
print(f"    First 300 chars: {repr(text[:300])}")

if text.strip().startswith('{') or text.strip().startswith('['):
    print("    ✅ Looks like JSON")
else:
    print("    ❌ Does NOT look like JSON! Possible redirect to HTML page or error page.")
    print(f"\n    Full response (first 2000 chars):\n{text[:2000]}")
    sys.exit(1)

# ── Step 3: Parse JSON ──────────────────────────────────────
print("\n[3] Parsing JSON...")
try:
    data = response.json()
    print(f"    ✅ Parsed successfully. Root type: {type(data).__name__}")
except json.JSONDecodeError as e:
    print(f"    ❌ JSON parse error: {e}")
    sys.exit(1)

# ── Step 4: Explore structure ───────────────────────────────
print("\n[4] Exploring structure...")

def explore(obj, path="root", depth=0):
    indent = "    " + "  " * depth
    if depth > 4:
        return
    if isinstance(obj, dict):
        print(f"{indent}[dict] {path} — keys: {list(obj.keys())}")
        for k, v in obj.items():
            explore(v, f"{path}['{k}']", depth + 1)
    elif isinstance(obj, list):
        print(f"{indent}[list] {path} — {len(obj)} items")
        if obj:
            first = obj[0]
            if isinstance(first, dict):
                print(f"{indent}  First item keys: {list(first.keys())}")
                print(f"{indent}  First item sample:")
                for k, v in list(first.items())[:12]:
                    print(f"{indent}    '{k}': {repr(v)[:100]}")
            elif isinstance(first, str):
                print(f"{indent}  First item (str): {repr(first[:200])}")
    else:
        if depth <= 2:
            print(f"{indent}[{type(obj).__name__}] {path} = {repr(obj)[:100]}")

explore(data)

# ── Step 5: Find any list of dicts (jobs) ───────────────────
print("\n[5] Searching for job-like arrays (any list of dicts)...")

def find_lists(obj, path="root", depth=0, found=None):
    if found is None:
        found = []
    if depth > 6:
        return found
    if isinstance(obj, list) and obj and isinstance(obj[0], dict):
        found.append((path, len(obj), list(obj[0].keys())[:10]))
    if isinstance(obj, dict):
        for k, v in obj.items():
            find_lists(v, f"{path}['{k}']", depth + 1, found)
    elif isinstance(obj, list):
        for i, item in enumerate(obj[:3]):
            find_lists(item, f"{path}[{i}]", depth + 1, found)
    return found

lists_found = find_lists(data)
if lists_found:
    print(f"    Found {len(lists_found)} list(s) of dicts:")
    for path, count, keys in lists_found:
        print(f"    ✅ {path}: {count} items, keys={keys}")
else:
    print("    ❌ No lists of dicts found at all!")

# ── Step 6: Try JSONL format ────────────────────────────────
print("\n[6] Checking if file is JSONL (one JSON object per line)...")
lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
print(f"    Total lines: {len(lines)}")
if len(lines) > 1:
    try:
        first_line = json.loads(lines[0])
        second_line = json.loads(lines[1])
        print(f"    ✅ Looks like JSONL! Each line is valid JSON.")
        print(f"    Line 0 type: {type(first_line).__name__}, keys: {list(first_line.keys()) if isinstance(first_line, dict) else 'N/A'}")
        print(f"    Line 1 type: {type(second_line).__name__}, keys: {list(second_line.keys()) if isinstance(second_line, dict) else 'N/A'}")
        print(f"\n    ⚠️  FIX NEEDED: Use JSONL parsing instead of response.json()")
        print(f"    Replace: data = response.json()")
        print(f"    With:    data = [json.loads(l) for l in response.text.splitlines() if l.strip()]")
    except json.JSONDecodeError:
        print("    Not JSONL format.")

# ── Step 7: Alternative URL check ───────────────────────────
print("\n[7] Trying alternative MPSV endpoints...")
alt_urls = [
    "https://data.mpsv.cz/od/soubory/volna-mista/volna-mista.json",
    "https://www.uradprace.cz/web/cz/prohlizeni-volnych-mist",
]
for url in alt_urls:
    if url == URL:
        continue
    try:
        r = session.get(url, timeout=10, verify=False)
        print(f"    {url}: HTTP {r.status_code}, {len(r.content)} bytes")
    except Exception as e:
        print(f"    {url}: ❌ {e}")

print("\n" + "=" * 60)
print("Diagnostic complete.")
print("=" * 60)
