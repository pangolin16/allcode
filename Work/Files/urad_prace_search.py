"""
Custom search tool for Úřad práce ČR job listings
Uses the official JSON data source from data.mpsv.cz
"""

import requests
from typing import List, Dict, Optional
import re
import urllib3
import json

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class UradPraceSearcher:
    """Search Úřad práce job listings using the official JSON data"""
    
    def __init__(self):
        self.data_url = "https://data.mpsv.cz/od/soubory/volna-mista/volna-mista.json"
        self.base_url = "https://www.uradprace.cz"
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        })
        
        # Cache the data
        self.all_jobs = []
        self._load_data()
    
    def _load_data(self):
        """Load job data from the JSON source"""
        try:
            print(f"\n📥 Loading job data from {self.data_url}...")
            
            response = self.session.get(
                self.data_url,
                timeout=30,
                verify=False,
                allow_redirects=True
            )
            
            print(f"   Status: {response.status_code}")
            print(f"   Content-Type: {response.headers.get('Content-Type', 'Unknown')}")
            print(f"   Content length: {len(response.content)} bytes")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    print(f"   Response type: {type(data).__name__}")
                    
                    if isinstance(data, dict):
                        print(f"   Response keys: {list(data.keys())}")
                    elif isinstance(data, list):
                        print(f"   Response is a list with {len(data)} items")
                    
                    self.all_jobs = self._parse_response(data)
                    
                    if self.all_jobs:
                        print(f"✅ Successfully loaded {len(self.all_jobs)} jobs!")
                        # Show sample
                        print(f"\n   Sample job:")
                        sample = self.all_jobs[0]
                        print(f"   Title: {sample['title']}")
                        print(f"   Employer: {sample['employer']}")
                        print(f"   Salary: {sample['salary']}")
                    else:
                        print(f"⚠️  Loaded JSON but found 0 jobs")
                        print(f"   This might mean the JSON structure is different")
                
                except json.JSONDecodeError as e:
                    print(f"❌ Invalid JSON: {e}")
                    print(f"   Response preview: {response.text[:200]}")
            else:
                print(f"⚠️  HTTP {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                self.all_jobs = []
        
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection error - cannot reach {self.data_url}")
            self.all_jobs = []
        except requests.exceptions.Timeout:
            print(f"❌ Timeout - data source is too slow")
            self.all_jobs = []
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            import traceback
            traceback.print_exc()
            self.all_jobs = []
    
    def search_jobs(self, 
                   keyword: Optional[str] = None,
                   location: Optional[str] = None,
                   limit: int = 20,
                   exclude_driver_license: bool = False,
                   min_salary: Optional[int] = None,
                   max_salary: Optional[int] = None,
                   education: Optional[str] = None) -> List[Dict]:
        """Search for jobs with custom filters"""
        
        print(f"\n🔍 Searching in {len(self.all_jobs)} jobs...")
        
        if not self.all_jobs:
            print(f"⚠️  No jobs loaded! Trying to reload...")
            self._load_data()
        
        if keyword:
            print(f"   Keyword: {keyword}")
        if location:
            print(f"   Location: {location}")
        if min_salary:
            print(f"   Min Salary: {min_salary} CZK")
        if max_salary:
            print(f"   Max Salary: {max_salary} CZK")
        
        # Start with all jobs
        jobs = self.all_jobs.copy()
        
        # Filter by keyword
        if keyword:
            keyword_lower = keyword.lower()
            jobs = [j for j in jobs if keyword_lower in j['title'].lower() or 
                   keyword_lower in j['description'].lower() or
                   keyword_lower in j['employer'].lower()]
            print(f"   After keyword filter: {len(jobs)} jobs")
        
        # Filter by location
        if location:
            location_lower = location.lower()
            jobs = [j for j in jobs if location_lower in j['location'].lower()]
            print(f"   After location filter: {len(jobs)} jobs")
        
        print(f"📊 Found {len(jobs)} jobs before special filters")
        
        # Apply special filters
        if jobs:
            if exclude_driver_license:
                before = len(jobs)
                jobs = self._filter_driver_license(jobs)
                print(f"   After driver license filter: {before} → {len(jobs)}")
            
            if min_salary or max_salary:
                before = len(jobs)
                jobs = self._filter_salary(jobs, min_salary, max_salary)
                print(f"   After salary filter: {before} → {len(jobs)}")
            
            if education:
                before = len(jobs)
                jobs = self._filter_education(jobs, education)
                print(f"   After education filter: {before} → {len(jobs)}")
        
        print(f"📊 Final: {len(jobs)} jobs")
        return jobs[:limit]
    
    def _parse_response(self, data: Dict) -> List[Dict]:
        """Parse the JSON response"""
        jobs = []
        
        try:
            # Find the items array in different possible keys
            items = None
            
            if isinstance(data, list):
                items = data
                print(f"   Data is a list")
            elif isinstance(data, dict):
                print(f"   Data is a dict with keys: {list(data.keys())}")
                
                # Try different possible keys for items
                for key in ['polozky', 'items', 'content', 'data', 'results', 'jobs', 'offers', 'volna_mista', 'nabidky']:
                    if key in data:
                        items = data[key]
                        print(f"   Found items under key: '{key}'")
                        break
            
            if not items:
                print(f"   ⚠️  Could not find items in response")
                return []
            
            if not isinstance(items, list):
                print(f"   ⚠️  Items is not a list, it's a {type(items).__name__}")
                return []
            
            print(f"   Parsing {len(items)} items...")
            
            for idx, item in enumerate(items):
                if not isinstance(item, dict):
                    continue
                
                try:
                    # Extract salary
                    salary_from = item.get('mzdaOd') or item.get('salaryMin') or item.get('salary_from')
                    salary_to = item.get('mzdaDo') or item.get('salaryMax') or item.get('salary_to')
                    
                    salary_text = ""
                    if salary_from and salary_to:
                        salary_text = f"{salary_from} - {salary_to} Kč/měsíc"
                    elif salary_from:
                        salary_text = f"Od {salary_from} Kč/měsíc"
                    elif salary_to:
                        salary_text = f"Do {salary_to} Kč/měsíc"
                    
                    # Get education
                    education_info = item.get('vzdelani') or item.get('education') or {}
                    education_name = ""
                    if isinstance(education_info, dict):
                        education_name = education_info.get('nazev') or education_info.get('name') or ''
                    elif isinstance(education_info, str):
                        education_name = education_info
                    
                    # Extract fields
                    title = item.get('nazevPozice') or item.get('title') or item.get('position') or ''
                    employer = item.get('nazevFirmy') or item.get('employer') or item.get('company') or ''
                    location = item.get('mistoVykonuPrace') or item.get('location') or item.get('city') or ''
                    job_id = item.get('id') or item.get('offerId') or ''
                    description = item.get('popis') or item.get('description') or ''
                    
                    # Convert salary to int
                    try:
                        salary_from = int(str(salary_from).replace(' ', '')) if salary_from else 0
                        salary_to = int(str(salary_to).replace(' ', '')) if salary_to else 0
                    except:
                        salary_from = 0
                        salary_to = 0
                    
                    # Build job object
                    job = {
                        "id": str(job_id),
                        "title": title.strip() if title else '',
                        "employer": employer.strip() if employer else '',
                        "location": location.strip() if location else '',
                        "salary": salary_text.strip() if salary_text else '',
                        "salary_from": salary_from,
                        "salary_to": salary_to,
                        "type": (item.get('typPozice') or item.get('type') or '').strip(),
                        "posted": (item.get('datumZverejneni') or item.get('publishedDate') or '').strip(),
                        "education": education_name.strip() if education_name else '',
                        "url": f"https://www.uradprace.cz/volne-miste/{job_id}" if job_id else "#",
                        "description": (description[:500] if description else '').strip(),
                    }
                    
                    if job['title']:
                        jobs.append(job)
                
                except Exception as e:
                    if idx < 3:  # Only log first few errors
                        print(f"   ⚠️  Error parsing item {idx}: {e}")
            
            print(f"   ✅ Successfully parsed {len(jobs)} jobs")
                    
        except Exception as e:
            print(f"   ❌ Parse error: {e}")
            import traceback
            traceback.print_exc()
        
        return jobs
    
    def _filter_driver_license(self, jobs: List[Dict]) -> List[Dict]:
        """Filter out jobs requiring a driver's license"""
        keywords = [
            "řidič", "ridic", "řidičský", "ridicsky", "řp",
            "vozidlo", "auto", "doprava", "řízení",
            "vozík", "vozik", "řidičák", "driver", "driving",
            "kategorie c+e", "kategorie c e", "kategorie b+e", "řidičský průkaz"
        ]
        
        filtered = []
        for job in jobs:
            text = (job.get('title', '') + ' ' + job.get('description', '')).lower()
            has_driver = any(kw.lower() in text for kw in keywords)
            
            if not has_driver:
                filtered.append(job)
        
        return filtered
    
    def _filter_salary(self, jobs: List[Dict], min_sal: Optional[int], max_sal: Optional[int]) -> List[Dict]:
        """Filter by salary - STRICT filtering"""
        filtered = []
        
        for job in jobs:
            sal_from = job.get('salary_from') or 0
            sal_to = job.get('salary_to') or 0
            
            # If no salary data, exclude it
            if sal_from == 0 and sal_to == 0:
                continue
            
            # Check minimum salary
            if min_sal:
                effective_max = sal_to if sal_to > 0 else sal_from
                if effective_max < min_sal:
                    continue
            
            # Check maximum salary
            if max_sal:
                if sal_from > max_sal:
                    continue
            
            filtered.append(job)
        
        return filtered
    
    def _filter_education(self, jobs: List[Dict], education: str) -> List[Dict]:
        """Filter by education level"""
        keywords = {
            "basic": ["základní"],
            "vocational": ["vyučen", "střední odborné", "sou"],
            "secondary": ["maturita", "střední s maturitou"],
            "higher": ["vyšší odborné", "vos"],
            "bachelor": ["bakalář", "bc."],
            "master": ["magistr", "mgr.", "ing."],
            "phd": ["doktor", "ph.d.", "phd"],
        }
        
        if education not in keywords:
            return jobs
        
        keywords_to_match = keywords[education]
        return [j for j in jobs if any(
            kw.lower() in (j.get('education', '') + ' ' + j.get('title', '') + ' ' + j.get('description', '')).lower()
            for kw in keywords_to_match
        )]