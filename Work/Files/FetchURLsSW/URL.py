import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

base = "https://www.jobs.ch/en/vacancies/?employment-type=1&employment-type=4&employment-type=5&industry=1&industry=2&industry=3&industry=4&industry=5&industry=6&industry=11&industry=13&industry=14&industry=15&industry=16&industry=19&industry=20&industry=21&industry=22&industry=23&industry=24&language-skill=en&position=3&term="

headers = {"User-Agent": "Mozilla/5.0"}
jobs = set()

for page in range(1, 54):
    url = base if page == 1 else base.replace(
        "&position=3",
        f"&page={page}&position=3"
    )

    r = requests.get(url, headers=headers)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    for a in soup.select('a[href*="/en/vacancies/detail/"]'):
        jobs.add(urljoin(url, a["href"]))

with open("jobs_ch_urls.txt", "w", encoding="utf-8") as f:
    for url in sorted(jobs):
        f.write(url + "\n")