"""
Test script for the hourly-to-monthly salary conversion.
"""
import json

# Simulate the salary conversion logic
def _to_int(value) -> int:
    if value is None:
        return 0
    try:
        return int(str(value).replace("\xa0", "").replace(" ", "").replace(",", ""))
    except (ValueError, TypeError):
        return 0

def compute_salary_text(item):
    salary_from = _to_int(item.get("mesicniMzdaOd") or item.get("mzdaOd"))
    salary_to   = _to_int(item.get("mesicniMzdaDo") or item.get("mzdaDo"))

    # Determine salary type
    typ_mzdy_raw = item.get("typMzdy") or {}
    typ_mzdy = ""
    if isinstance(typ_mzdy_raw, dict):
        typ_mzdy = (typ_mzdy_raw.get("id") or "").replace("TypMzdy/", "")
    elif isinstance(typ_mzdy_raw, str):
        typ_mzdy = typ_mzdy_raw.replace("TypMzdy/", "")

    # Get weekly hours
    weekly_hours_raw = item.get("pocetHodinTydne")
    weekly_hours = 0
    if weekly_hours_raw is not None:
        try:
            weekly_hours = int(str(weekly_hours_raw).strip())
        except (ValueError, TypeError):
            pass

    print(f"  typMzdy: {typ_mzdy!r}, weekly_hours: {weekly_hours}")
    print(f"  salary_from: {salary_from}, salary_to: {salary_to}")

    if typ_mzdy == "hod" and weekly_hours > 0:
        factor = (166.67 / 40.0) * weekly_hours
        monthly_from = round(salary_from * factor) if salary_from else 0
        monthly_to   = round(salary_to * factor)   if salary_to   else 0

        if monthly_from and monthly_to:
            salary_text = f"{monthly_from} - {monthly_to} Kc/mesic"
        elif monthly_from:
            salary_text = f"Od {monthly_from} Kc/mesic"
        elif monthly_to:
            salary_text = f"Do {monthly_to} Kc/mesic"
        else:
            salary_text = ""
    elif typ_mzdy == "hod":
        if salary_from and salary_to:
            salary_text = f"{salary_from} - {salary_to} Kc/hod"
        elif salary_from:
            salary_text = f"Od {salary_from} Kc/hod"
        elif salary_to:
            salary_text = f"Do {salary_to} Kc/hod"
        else:
            salary_text = ""
    else:
        if salary_from and salary_to:
            salary_text = f"{salary_from} - {salary_to} Kc/mesic"
        elif salary_from:
            salary_text = f"Od {salary_from} Kc/mesic"
        elif salary_to:
            salary_text = f"Do {salary_to} Kc/mesic"
        else:
            salary_text = ""
    return salary_text

# Test cases
test_cases = [
    # Case 1: Hourly wage with 10h/week
    # Mzdové rozpětí od 150 Kč/hod, Počet hodin týdně = 10
    # Expected: (166,67/4)*150 = 6522 Kč/měsíc
    {
        "name": "Hourly 150kc, 10h/week -> monthly",
        "item": {"mesicniMzdaOd": 150, "typMzdy": {"id": "TypMzdy/hod"}, "pocetHodinTydne": 10},
        "expected_contains": ["6522", "Kc/mesic"]
    },
    # Case 2: Hourly wage with 30h/week
    # Expected: (166,67/40)*30*150 = 19566 Kč/měsíc
    {
        "name": "Hourly 150kc, 30h/week -> monthly",
        "item": {"mesicniMzdaOd": 150, "typMzdy": {"id": "TypMzdy/hod"}, "pocetHodinTydne": 30},
        "expected_contains": ["19566", "Kc/mesic"]
    },
    # Case 3: Hourly range with 40h/week
    # od 150 do 200 Kč/hod, 40h/week -> od 26088 do 34784 Kč/měsíc
    {
        "name": "Hourly range 150-200kc, 40h/week -> monthly",
        "item": {"mesicniMzdaOd": 150, "mesicniMzdaDo": 200, "typMzdy": {"id": "TypMzdy/hod"}, "pocetHodinTydne": 40},
        "expected_contains": ["26088", "34784", "Kc/mesic"]
    },
    # Case 4: Already monthly - unchanged
    {
        "name": "Monthly 20000kc -> unchanged",
        "item": {"mesicniMzdaOd": 20000, "typMzdy": {"id": "TypMzdy/mesic"}},
        "expected_contains": ["Od 20000", "Kc/mesic"]
    },
    # Case 5: Hourly without weekly hours -> keep hourly
    {
        "name": "Hourly 150kc, no weekly hours -> hourly",
        "item": {"mesicniMzdaOd": 150, "typMzdy": {"id": "TypMzdy/hod"}},
        "expected_contains": ["150", "Kc/hod"]
    },
    # Case 6: Hourly with weekly hours = "Nevyplněno" (None/missing) -> keep hourly
    {
        "name": "Hourly 150kc, weekly hours None -> hourly",
        "item": {"mesicniMzdaOd": 150, "typMzdy": {"id": "TypMzdy/hod"}, "pocetHodinTydne": None},
        "expected_contains": ["150", "Kc/hod"]
    },
    # Case 7: Hourly with weekly hours = 0 -> keep hourly
    {
        "name": "Hourly 150kc, weekly hours 0 -> hourly",
        "item": {"mesicniMzdaOd": 150, "typMzdy": {"id": "TypMzdy/hod"}, "pocetHodinTydne": 0},
        "expected_contains": ["150", "Kc/hod"]
    },
]

all_pass = True
for tc in test_cases:
    result = compute_salary_text(tc["item"])
    checks = all(c in result for c in tc["expected_contains"])
    status = "✅ PASS" if checks else "❌ FAIL"
    if not checks:
        all_pass = False
    print(f"{status}: {tc['name']}")
    print(f"  Result: {result}")
    print(f"  Expected contains: {tc['expected_contains']}")
    print()

if all_pass:
    print("All tests passed! ✅")
else:
    print("Some tests FAILED! ❌")