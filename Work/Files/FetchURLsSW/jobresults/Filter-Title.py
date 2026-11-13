#!/usr/bin/env python3
"""
SMART Filter - Filtered + Excluded version
- Input is Combined-Job-Titles.json (or any combined list)
- Output is split into:
  FILTERED = titles that passed the blacklist
  EXCLUDED = titles that matched the blacklist
- FILTERED + EXCLUDED == COMBINED (count-wise and content-wise)

Matching rules:
- Short terms (<=3 chars like "PR", "HR") -> whole word match only (\bPR\b)
- Longer terms -> case-insensitive substring match
- Multi-word phrases -> substring match
- Optional diacritic-insensitive mode

Usage:
  python Filter-Titles-Smart-Filtered-Excluded.py -i Combined-Job-Titles.json -b Title_Blacklist.json -f Filtered-Job-Titles.json -e Excluded-Job-Titles.json
"""

import json
import argparse
import re
import unicodedata
from pathlib import Path

def strip_diacritics(s: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')

def normalize(s: str, ignore_diacritics: bool = False) -> str:
    s = s.lower().strip()
    if ignore_diacritics:
        s = strip_diacritics(s)
    return s

def load_json(path: Path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    parser = argparse.ArgumentParser(description="Smart filter - splits Combined into Filtered + Excluded")
    parser.add_argument('--input', '-i', default='Combined-Job-Titles.json', help='Input combined file (default: Combined-Job-Titles.json)')
    parser.add_argument('--blacklist', '-b', default='Title_Blacklist.json', help='Blacklist file')
    parser.add_argument('--filtered', '-f', default='Filtered-Job-Titles.json', help='Output FILTERED file (kept titles)')
    parser.add_argument('--excluded', '-e', default='Excluded-Job-Titles.json', help='Output EXCLUDED file (removed titles)')
    # Keep backward compat with old arg names
    parser.add_argument('--output', '-o', default=None, help='Deprecated: use --filtered instead')
    parser.add_argument('--removed', default=None, help='Deprecated: use --excluded instead')
    parser.add_argument('--diacritic-insensitive', action='store_true', help='Ignore Czech diacritics (kuchari matches kuchaři)')
    parser.add_argument('--short-threshold', type=int, default=3, help='Terms <= this length require word boundaries')
    args = parser.parse_args()

    # Handle deprecated args
    filtered_path = Path(args.filtered if args.output is None else args.output)
    excluded_path = Path(args.excluded if args.removed is None else args.removed)
    input_path = Path(args.input)
    blacklist_path = Path(args.blacklist)

    data = load_json(input_path)
    blacklist_raw = load_json(blacklist_path)
    blacklist = [b for b in blacklist_raw if isinstance(b, str) and b.strip()]

    is_obj = len(data) > 0 and isinstance(data[0], dict) and 'title' in data[0]

    filtered = []
    excluded = []

    for item in data:
        title = item['title'] if is_obj else str(item)
        title_norm = normalize(title, args.diacritic_insensitive)

        matched = None
        for raw_term in blacklist:
            norm_term = normalize(raw_term, args.diacritic_insensitive)
            if not norm_term:
                continue

            # Decide matching strategy
            if ' ' in norm_term.strip():
                # Multi-word phrase -> substring
                if norm_term in title_norm:
                    matched = raw_term
                    break
            elif len(norm_term) <= args.short_threshold:
                # Very short -> require word boundary \bTERM\b
                pattern = r'\b' + re.escape(raw_term) + r'\b'
                flags = re.IGNORECASE
                # For diacritic mode, check against normalized? Use original + normalized fallback
                if args.diacritic_insensitive:
                    # Need to search in normalized version for diacritic-insensitivity
                    # but \b works better on original, so check both
                    if re.search(pattern, title, flags) or re.search(r'\b' + re.escape(norm_term) + r'\b', title_norm):
                        matched = raw_term
                        break
                else:
                    if re.search(pattern, title, flags):
                        matched = raw_term
                        break
            else:
                # Normal term -> substring (covers inflections like "řidič" in "řidiči")
                if norm_term in title_norm:
                    matched = raw_term
                    break

        if matched:
            if is_obj:
                excluded.append({**item, "_removed_by": matched})
            else:
                excluded.append(item)
        else:
            filtered.append(item)

    # Write outputs
    with open(filtered_path, 'w', encoding='utf-8') as f:
        json.dump(filtered, f, ensure_ascii=False, indent=2)
    with open(excluded_path, 'w', encoding='utf-8') as f:
        json.dump(excluded, f, ensure_ascii=False, indent=2)

    # Verification that filtered + excluded == combined
    total_ok = len(filtered) + len(excluded) == len(data)
    
    print(f"Total (Combined): {len(data)}, Filtered: {len(filtered)}, Excluded: {len(excluded)} - Sum OK: {total_ok}")
    print(f"Filtered -> {filtered_path}")
    print(f"Excluded -> {excluded_path}")
    if not total_ok:
        print("WARNING: Count mismatch! Filtered + Excluded != Combined")

if __name__ == '__main__':
    main()
