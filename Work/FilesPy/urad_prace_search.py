"""
Flask web application for searching Úřad práce ČR job listings
Provides a simple web interface with location and keyword filters
"""

from flask import Flask, render_template_string, request, jsonify
from urad_prace_search import UradPraceSearcher
import json
import requests
from typing import List, Dict, Optional
from urllib.parse import urlencode
from bs4 import BeautifulSoup

app = Flask(__name__)
searcher = UradPraceSearcher()

# Simple test to verify connection on startup
try:
    test_url = "https://www.uradprace.cz/api/volnamista?limit=1&location=Praha"
    requests.get(test_url, verify=False, timeout=5)
    print("✅ SSL Bypass successful: Connection to Úřad práce is working.")
except Exception as e:
    print(f"⚠️ Startup connection test failed: {e}")


class UradPraceSearcherExtended(UradPraceSearcher):

    def _parse_api_response(self, data: Dict) -> List[Dict]:
        jobs = []

        results = data.get("results", data.get("položky", []))

        for item in results:
            job = {
                "title": item.get("pozice", item.get("title", "Název neuveden")),
                "employer": item.get("zamestnavatel", item.get("employer", "Firma neuvedena")),
                "location": item.get("misto", item.get("location", "Lokalita neuvedena")),
                "salary": item.get("mzda", item.get("salary", "Dohodou")),
                "type": item.get("uvazek", item.get("type", "Plný úvazek")),
                "posted": item.get("datum", item.get("posted", "")),
                "url": item.get("url", "#"),
                "description": item.get("popis", ""),
            }
            jobs.append(job)

        return jobs

    def _filter_driver_license(self, jobs: List[Dict]) -> List[Dict]:
        driver_keywords = [
            "řidič", "ridic", "řidičský průkaz", "ridicsky prukaz", "řp",
            "vozidlo", "auto", "doprava", "řízení", "řidičák", "ridicak",
            "kategorie", "c+e", "c e", "b+e", "driving", "driver", "license",
            "vzv", "vysokozdvižný vozík", "vysokozdvizny vozik"
        ]

        filtered_jobs = []

        for job in jobs:
            title_lower = job.get("title", "").lower()
            description_lower = job.get("description", "").lower()

            has_driver_requirement = any(
                keyword in title_lower or keyword in description_lower
                for keyword in driver_keywords
            )

            if not has_driver_requirement:
                filtered_jobs.append(job)

        return filtered_jobs

    def _filter_salary(
        self,
        jobs: List[Dict],
        min_salary: Optional[int],
        max_salary: Optional[int],
    ) -> List[Dict]:
        import re

        filtered_jobs = []

        for job in jobs:
            salary_text = job.get("salary", "")

            if not salary_text or salary_text == "N/A":
                filtered_jobs.append(job)
                continue

            numbers = re.findall(r"\d+", salary_text.replace(" ", ""))

            if not numbers:
                filtered_jobs.append(job)
                continue

            salaries = []
            for num_str in numbers:
                try:
                    salaries.append(int(num_str))
                except ValueError:
                    pass

            if not salaries:
                filtered_jobs.append(job)
                continue

            job_salary = min(salaries)

            if min_salary and job_salary < min_salary:
                continue
            if max_salary and job_salary > max_salary:
                continue

            filtered_jobs.append(job)

        return filtered_jobs

    def _filter_education(self, jobs: List[Dict], education: str) -> List[Dict]:
        education_keywords = {
            "basic": ["základní", "zakladni"],
            "vocational": ["vyučen", "vyucen", "střední odborné", "stredni odborne", "sou"],
            "secondary": ["maturita", "střední s maturitou", "stredni s maturitou", "sš"],
            "higher": ["vyšší odborné", "vyssi odborne", "vos"],
            "bachelor": ["bakalář", "bakalar", "bc.", "vysokoškolské", "vysokoskolske"],
            "master": ["magistr", "mgr.", "ing.", "vysokoškolské", "vysokoskolske"],
            "phd": ["doktor", "ph.d.", "phd"],
        }

        if education not in education_keywords:
            return jobs

        keywords = education_keywords[education]
        filtered_jobs = []

        for job in jobs:
            text = (
                job.get("title", "").lower()
                + " "
                + job.get("description", "").lower()
            )

            has_education_mention = any(
                keyword in text
                for levels in education_keywords.values()
                for keyword in levels
            )

            if not has_education_mention:
                filtered_jobs.append(job)
                continue

            matches = any(keyword in text for keyword in keywords)

            if matches:
                filtered_jobs.append(job)

        return filtered_jobs

    def _scrape_web_search(
        self,
        keyword: Optional[str],
        location: Optional[str],
        limit: int,
        exclude_driver_license: bool = False,
        min_salary: Optional[int] = None,
        max_salary: Optional[int] = None,
        education: Optional[str] = None,
    ) -> List[Dict]:
        print("Using web scraping fallback method...")

        jobs = []
        search_params = {}

        if keyword:
            search_params["q"] = keyword
        if location:
            search_params["loc"] = location

        url = f"{self.base_url}/volna-mista-v-cr"

        if search_params:
            url += f"?{urlencode(search_params)}"

        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, "html.parser")

            return [{
                "message": "Web scraping requires analyzing the actual page structure",
                "url": url,
                "suggestion": "Visit the URL to inspect structure",
            }]

        except Exception as e:
            return [{"error": str(e)}]

    def print_results(self, jobs: List[Dict]):
        if not jobs:
            print("No jobs found.")
            return

        print(f"\n{'='*80}")
        print(f"Found {len(jobs)} job(s)")
        print(f"{'='*80}\n")

        for i, job in enumerate(jobs, 1):
            print(f"{i}. {job.get('title', 'N/A')}")
            print(f"   Employer: {job.get('employer', 'N/A')}")
            print(f"   Location: {job.get('location', 'N/A')}")

            if job.get("salary"):
                print(f"   Salary: {job['salary']}")

            if job.get("type"):
                print(f"   Type: {job['type']}")

            if job.get("posted"):
                print(f"   Posted: {job['posted']}")

            if job.get("url"):
                print(f"   URL: {job['url']}")

            print()


def main():
    searcher = UradPraceSearcherExtended()

    print("Úřad práce ČR - Custom Job Search\n")

    print("\n--- Example 1: Logistics jobs in Prague ---")
    jobs = searcher.search_jobs(keyword="logistika", location="Praha", limit=10)
    searcher.print_results(jobs)

    print("\n--- Example 2: Jobs in Brno ---")
    jobs = searcher.search_jobs(location="Brno", limit=10)
    searcher.print_results(jobs)

    print("\n--- Example 3: IT jobs ---")
    jobs = searcher.search_jobs(keyword="IT", limit=10)
    searcher.print_results(jobs)


if __name__ == "__main__":
    main()