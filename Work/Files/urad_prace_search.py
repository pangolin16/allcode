"""
Custom search tool for Úřad práce ČR job listings
Scrapes real job data from the website
"""

import requests
from bs4 import BeautifulSoup
import json
from typing import List, Dict, Optional
from urllib.parse import urlencode
import re
import urllib3
import time

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class UradPraceSearcher:
    """Search Úřad práce job listings"""
    
    def __init__(self):
        self.base_url = "https://www.uradprace.cz"
        self.api_url = "https://www.uradprace.cz/api/v2/job-offers"  # Real API endpoint
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'cs-CZ,cs;q=0.9',
            'Referer': 'https://www.uradprace.cz/volna-mista-v-cr',
        })
    
    def search_jobs(self, 
                   keyword: Optional[str] = None,
                   location: Optional[str] = None,
                   limit: int = 20,
                   exclude_driver_license: bool = False,
                   min_salary: Optional[int] = None,
                   max_salary: Optional[int] = None,
                   education: Optional[str] = None) -> List[Dict]:
        """
        Search for jobs with custom filters
        """
        
        print(f"\n🔍 Searching for jobs...")
        if keyword:
            print(f"   Keyword: {keyword}")
        if location:
            print(f"   Location: {location}")
        
        # Try different API approaches
        jobs = []
        
        # Try approach 1: Main page with embedded data
        jobs = self._scrape_main_page(keyword, location, limit * 2)
        
        # Try approach 2: Direct API call
        if not jobs or len(jobs) < 5:
            jobs = self._try_api_endpoints(keyword, location, limit * 2)
        
        print(f"📊 Found {len(jobs)} job listings")
        
        # Apply filters
        if jobs:
            if exclude_driver_license:
                jobs = self._filter_driver_license(jobs)
                print(f"   After driver license filter: {len(jobs)}")
            if min_salary or max_salary:
                jobs = self._filter_salary(jobs, min_salary, max_salary)
                print(f"   After salary filter: {len(jobs)}")
            if education:
                jobs = self._filter_education(jobs, education)
                print(f"   After education filter: {len(jobs)}")
        
        return jobs[:limit]
    
    def _scrape_main_page(self, keyword: Optional[str], location: Optional[str], limit: int) -> List[Dict]:
        """Scrape jobs from the main page"""
        try:
            print("   📄 Scraping main page...")
            
            url = f"{self.base_url}/volna-mista-v-cr"
            params = {}
            
            if keyword:
                params['q'] = keyword
            if location:
                params['location'] = location
            
            if params:
                url += f"?{urlencode(params)}"
            
            response = self.session.get(url, timeout=15, verify=False)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                print(f"   ⚠️  HTTP {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            jobs = []
            
            # Look for all links that might be job listings
            # Find all elements that contain job information
            for link in soup.find_all('a', href=re.compile(r'/nabidka/|/volna-mista')):
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                # Skip if text is too short or empty
                if not text or len(text) < 3 or text.isdigit():
                    continue
                
                # Check if this looks like a job listing
                if '/nabidka/' in href or any(word in text.lower() for word in 
                    ['pracovník', 'specialista', 'vývojář', 'engineer', 'senior', 'junior']):
                    
                    job = {
                        "title": text,
                        "employer": "",
                        "location": location or "",
                        "salary": "",
                        "type": "Plný úvazek",
                        "posted": "",
                        "url": href if href.startswith('http') else self.base_url + href,
                        "description": text,
                    }
                    
                    jobs.append(job)
            
            print(f"   Found {len(jobs)} jobs from main page")
            return jobs[:limit]
        
        except Exception as e:
            print(f"   ⚠️  Error: {e}")
            return []
    
    def _try_api_endpoints(self, keyword: Optional[str], location: Optional[str], limit: int) -> List[Dict]:
        """Try different API endpoints"""
        
        endpoints = [
            "https://www.uradprace.cz/api/v2/job-offers",
            "https://up.gov.cz/api/v1/job-offers",
            "https://api.apitalks.store/volna-pracovni-mista",
            "https://www.uradprace.cz/api/jobs",
        ]
        
        for endpoint in endpoints:
            try:
                print(f"   📡 Trying {endpoint}...")
                
                params = {
                    'limit': limit,
                    'offset': 0,
                    'sort': '-id'
                }
                
                if keyword:
                    params['q'] = keyword
                    params['query'] = keyword
                    params['search'] = keyword
                
                if location:
                    params['location'] = location
                    params['city'] = location
                
                response = self.session.get(endpoint, params=params, timeout=10, verify=False)
                
                if response.status_code == 200:
                    data = response.json()
                    jobs = self._parse_api_response(data)
                    
                    if jobs:
                        print(f"   Found {len(jobs)} jobs from API")
                        return jobs
                
            except Exception as e:
                continue
        
        return []
    
    def _parse_api_response(self, data) -> List[Dict]:
        """Parse API response"""
        jobs = []
        
        try:
            # Handle different response structures
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict):
                # Try different response formats
                items = (data.get('results') or 
                        data.get('data') or 
                        data.get('items') or 
                        data.get('jobs') or 
                        data.get('volna_mista') or 
                        data.get('offers') or [])
            else:
                return []
            
            if not isinstance(items, list):
                return []
            
            for item in items:
                if not isinstance(item, dict):
                    continue
                
                job = {
                    "title": (item.get("position") or item.get("title") or 
                             item.get("pozice") or item.get("job_title") or ""),
                    "employer": (item.get("company") or item.get("employer") or 
                               item.get("zamestnavatel") or item.get("company_name") or ""),
                    "location": (item.get("location") or item.get("city") or 
                               item.get("misto") or item.get("mesto") or ""),
                    "salary": (item.get("salary") or item.get("mzda") or 
                              item.get("wage") or item.get("plat") or ""),
                    "type": (item.get("employment_type") or item.get("type") or 
                            item.get("uvazek") or item.get("job_type") or "Plný úvazek"),
                    "posted": (item.get("posted_date") or item.get("posted") or 
                              item.get("datum") or item.get("date") or ""),
                    "url": (item.get("url") or item.get("link") or item.get("href") or "#"),
                    "description": (item.get("description") or item.get("popis") or 
                                  item.get("summary") or ""),
                }
                
                if job['title']:
                    jobs.append(job)
        
        except Exception as e:
            print(f"   Error parsing API: {e}")
        
        return jobs
    
    def _filter_driver_license(self, jobs: List[Dict]) -> List[Dict]:
        """Filter out jobs requiring a driver's license"""
        driver_keywords = [
            "řidič", "ridic", "řidičský", "ridicsky", "řp",
            "vozidlo", "auto", "doprava", "řízení", "řidičák",
            "kategorie", "c+e", "b+e", "driving", "driver",
            "vozík", "vozik"
        ]
        
        filtered = []
        for job in jobs:
            title = str(job.get("title", "")).lower()
            desc = str(job.get("description", "")).lower()
            text = title + " " + desc
            
            if not any(kw.lower() in text for kw in driver_keywords):
                filtered.append(job)
        
        return filtered
    
    def _filter_salary(self, jobs: List[Dict], min_salary: Optional[int], max_salary: Optional[int]) -> List[Dict]:
        """Filter jobs by salary range"""
        filtered = []
        
        for job in jobs:
            salary_text = str(job.get("salary", ""))
            
            if not salary_text or salary_text == "":
                filtered.append(job)
                continue
            
            # Extract numbers from salary
            numbers = re.findall(r"\d+", salary_text.replace(" ", "").replace(",", ""))
            
            if not numbers:
                filtered.append(job)
                continue
            
            try:
                # Get minimum salary from the range
                min_num = min(int(n) for n in numbers if n)
                
                if min_salary and min_num < min_salary:
                    continue
                if max_salary and min_num > max_salary:
                    continue
                
                filtered.append(job)
            except:
                filtered.append(job)
        
        return filtered
    
    def _filter_education(self, jobs: List[Dict], education: str) -> List[Dict]:
        """Filter jobs by education level"""
        education_keywords = {
            "basic": ["základní", "zakladni"],
            "vocational": ["vyučen", "střední odborné", "sou", "odborné učiliště"],
            "secondary": ["maturita", "střední s maturitou", "sš"],
            "higher": ["vyšší odborné", "vos"],
            "bachelor": ["bakalář", "bc.", "vysokoškolské", "vysokoškolské vzdělání"],
            "master": ["magistr", "mgr.", "ing.", "vysokoškolské"],
            "phd": ["doktor", "ph.d.", "phd"],
        }
        
        if education not in education_keywords:
            return jobs
        
        keywords = education_keywords[education]
        filtered = []
        
        for job in jobs:
            text = (str(job.get("title", "")).lower() + " " + 
                   str(job.get("description", "")).lower())
            
            # Check if matches education level
            if any(kw.lower() in text for kw in keywords):
                filtered.append(job)
        
        return filtered