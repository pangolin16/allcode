import requests
import json
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ✅ Official MPSV Open Data endpoint - publicly available bulk JSON
OPEN_DATA_URL = "https://data.mpsv.cz/od/soubory/volna-mista/volna-mista.json"

session = requests.Session()
session.headers.update({
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (compatible; JobScraper/1.0)"
})

print(f"📡 Fetching from: {OPEN_DATA_URL}")
try:
    response = session.get(OPEN_DATA_URL, verify=False, timeout=30)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()

        # The JSON structure has a top-level list of job postings
        jobs = data if isinstance(data, list) else data.get("volnaMista", data.get("content", []))

        print(f"✅ Total jobs loaded: {len(jobs)}")

        # --- Filter locally (replaces server-side search) ---
        keyword = "Python"
        min_salary = 40000

        filtered = []
        for job in jobs:
            # Fulltext match in position name or description
            text_fields = " ".join([
                str(job.get("druhPrace", "")),
                str(job.get("pracovniNaplnPozice", "")),
                str(job.get("nazevPozice", "")),
            ]).lower()

            salary = job.get("mzdaOd") or job.get("zakladniMzda", 0) or 0
            
            if keyword.lower() in text_fields and salary >= min_salary:
                filtered.append(job)

        print(f"🔍 Filtered jobs matching '{keyword}' with salary ≥ {min_salary}: {len(filtered)}")

        if filtered:
            first = filtered[0]
            print(f"\nExample Result:")
            print(f"- Position:  {first.get('druhPrace') or first.get('nazevPozice')}")
            print(f"- Company:   {first.get('nazevZamestnavatele')}")
            print(f"- Location:  {first.get('obec') or first.get('mistoVykonuPrace')}")
            print(f"- Salary:    {first.get('mzdaOd')} - {first.get('mzdaDo')} CZK")
        else:
            print("No matching jobs found. Try a broader keyword or lower salary threshold.")

    else:
        print(f"❌ Failed: {response.text}")

except Exception as e:
    print(f"❌ Connection Error: {e}")