"""
Custom search tool for Úřad práce ČR job listings
Uses web scraping to fetch job listings from uradprace.cz
"""

import requests
from bs4 import BeautifulSoup
from bs4 import BeautifulSoup
import json
from typing import List, Dict, Optional
from urllib.parse import urlencode, quote
import re
import urllib3

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class UradPraceSearcher:

    def __init__(self):
        self.base_url = "https://www.uradprace.cz"
        self.session = requests.Session()
        ...

    def search_jobs(self,
                    keyword=None,
                    location=None,
                    limit=20,
                    exclude_driver_license=False,
                    min_salary=None,
                    max_salary=None,
                    education=None):

        print("\n🔍 Searching via API...")

        api_url = "https://www.uradprace.cz/api/volna-mista"

        params = {
            "size": limit,
            "page": 0
        }

        if keyword:
            params["fulltext"] = keyword

        if location:
            params["lokalita"] = location

        try:
            response = self.session.get(api_url, params=params, timeout=15, verify=False)

            if response.status_code != 200:
                print("API Error:", response.status_code)
                return []

            data = response.json()

            jobs = []

            for item in data.get("content", []):
                job = {
                    "title": item.get("nazevPozice", ""),
                    "employer": item.get("nazevFirmy", ""),
                    "location": item.get("mistoVykonuPrace", ""),
                    "salary": item.get("mzdaText", ""),
                    "type": item.get("pracovniVztah", ""),
                    "posted": item.get("datumZverejneni", ""),
                    "url": f"{self.base_url}/volne-misto/{item.get('id')}",
                    "description": item.get("poznamka", "")
                }

                jobs.append(job)

            return jobs[:limit]

        except Exception as e:
            print("Error:", e)
            return []
    
    def _extract_jobs_from_page(self, soup: BeautifulSoup, keyword: Optional[str], 
                               location: Optional[str], limit: int) -> List[Dict]:
        """Extract job listings from the HTML page"""
        jobs = []
        
        try:
            # Look for job listing containers
            # Try multiple selectors that might contain job listings
            job_containers = []
            
            # Try finding articles or divs with job-related classes
            selectors = [
                'article',
                'div[class*="job"]',
                'div[class*="offer"]',
                'div[class*="listing"]',
                'li[class*="job"]',
                'div[data-testid*="job"]',
            ]
            
            for selector in selectors:
                elements = soup.select(selector)
                if elements:
                    print(f"   Found {len(elements)} elements with selector: {selector}")
                    job_containers = elements
                    break
            
            # If no containers found, try to find links that look like job listings
            if not job_containers:
                print("   No job containers found, trying alternative method...")
                job_containers = self._find_job_links(soup)
            
            # Extract job details from each container
            for container in job_containers[:limit]:
                try:
                    job = self._extract_job_details(container)
                    if job and job.get('title'):
                        jobs.append(job)
                except Exception as e:
                    continue
            
            return jobs
        
        except Exception as e:
            print(f"   Error extracting jobs: {e}")
            return []
    
    def _find_job_links(self, soup: BeautifulSoup) -> List:
        """Find elements that might be job listings"""
        job_links = []
        
        # Look for links with href that might be job listings
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Check if this looks like a job link
            if any(keyword in href.lower() for keyword in ['job', 'nabidka', 'prace', 'pozice', 'work', 'offer']):
                if len(text) > 3 and len(text) < 200:
                    job_links.append(link)
        
        print(f"   Found {len(job_links)} potential job links")
        return job_links
    
    def _extract_job_details(self, element) -> Dict:
        """Extract detailed job information from an element"""
        job = {
            "title": "",
            "employer": "",
            "location": "",
            "salary": "",
            "type": "",
            "posted": "",
            "url": "",
            "description": "",
        }
        
        try:
            # Get all text from the element
            all_text = element.get_text(strip=True)
            
            # Title - try to get from heading or link
            title_elem = element.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if title_elem:
                job['title'] = title_elem.get_text(strip=True)
            else:
                # Try getting from a link
                link_elem = element.find('a')
                if link_elem and link_elem.get_text(strip=True):
                    job['title'] = link_elem.get_text(strip=True)
            
            # URL - get from any link in the element
            link = element.find('a', href=True)
            if link:
                url = link.get('href', '')
                if url:
                    if not url.startswith('http'):
                        url = self.base_url + ('' if url.startswith('/') else '/') + url
                    job['url'] = url
            
            # Try to extract other info from text
            # Look for common patterns
            
            # Employer - often after "Zaměstnavatel:" or similar
            employer_match = re.search(r'(?:Zaměstnavatel|Employer|Firma):\s*([^\n]+)', all_text, re.IGNORECASE)
            if employer_match:
                job['employer'] = employer_match.group(1).strip()
            else:
                # Try to find employer from common text patterns
                employer_elem = element.find(['span', 'p', 'div'], class_=re.compile(r'employer|company|firma', re.I))
                if employer_elem:
                    job['employer'] = employer_elem.get_text(strip=True)
            
            # Location - look for city patterns
            location_match = re.search(r'(?:Místo|Location|Město):\s*([^\n,]+)', all_text, re.IGNORECASE)
            if location_match:
                job['location'] = location_match.group(1).strip()
            else:
                # Try to find location element
                location_elem = element.find(['span', 'p', 'div'], class_=re.compile(r'location|place|city|misto', re.I))
                if location_elem:
                    job['location'] = location_elem.get_text(strip=True)
            
            # Salary - look for number patterns with CZK
            salary_match = re.search(r'(\d+\s*(?:Kč|CZK|Kč/měsíc|per month)?)', all_text)
            if salary_match:
                job['salary'] = salary_match.group(1).strip()
            else:
                salary_elem = element.find(['span', 'p', 'div'], class_=re.compile(r'salary|wage|mzda', re.I))
                if salary_elem:
                    job['salary'] = salary_elem.get_text(strip=True)
            
            # Employment type
            type_elem = element.find(['span', 'p', 'div'], class_=re.compile(r'type|employment|uvazek', re.I))
            if type_elem:
                job['type'] = type_elem.get_text(strip=True)
            
            # Posted date
            date_match = re.search(r'(\d{1,2}[./\-]\d{1,2}[./\-]\d{2,4})', all_text)
            if date_match:
                job['posted'] = date_match.group(1).strip()
            
            # Description - get first paragraph or available text
            desc_elem = element.find(['p', 'div'], class_=re.compile(r'description|desc|popis', re.I))
            if desc_elem:
                job['description'] = desc_elem.get_text(strip=True)
            else:
                # Use first 300 chars of all text if no description found
                job['description'] = all_text[:300] if all_text else ""
            
            return job
        
        except Exception as e:
            print(f"   Error in extract_job_details: {e}")
            return job
    
    def _filter_driver_license(self, jobs: List[Dict]) -> List[Dict]:
        """Filter out jobs requiring a driver's license"""
        driver_keywords = [
            "řidič", "ridic", "řidičský", "ridicsky", "řp", "ŘP",
            "vozidlo", "auto", "doprava", "řízení", "řidičák", "ridicak",
            "kategorie", "c+e", "c e", "b+e", "driving", "driver", "license",
            "vzv", "vysokozdvižný", "vysokozdvizny"
        ]
        
        filtered_jobs = []
        for job in jobs:
            title_lower = str(job.get("title", "")).lower()
            description_lower = str(job.get("description", "")).lower()
            
            has_driver = any(
                keyword.lower() in title_lower or keyword.lower() in description_lower
                for keyword in driver_keywords
            )
            
            if not has_driver:
                filtered_jobs.append(job)
        
        return filtered_jobs
    
    def _filter_salary(self, jobs: List[Dict], min_salary: Optional[int], max_salary: Optional[int]) -> List[Dict]:
        """Filter jobs by salary range"""
        filtered_jobs = []
        
        for job in jobs:
            salary_text = str(job.get("salary", ""))
            
            if not salary_text or salary_text == "N/A" or salary_text == "":
                filtered_jobs.append(job)
                continue
            
            # Extract numbers from salary text
            numbers = re.findall(r"\d+", salary_text.replace(" ", "").replace(",", ""))
            
            if not numbers:
                filtered_jobs.append(job)
                continue
            
            try:
                salaries = [int(num) for num in numbers]
                
                if not salaries:
                    filtered_jobs.append(job)
                    continue
                
                job_salary = min(salaries)
                
                # Apply filters
                if min_salary and job_salary < min_salary:
                    continue
                if max_salary and job_salary > max_salary:
                    continue
                
                filtered_jobs.append(job)
            except:
                filtered_jobs.append(job)
        
        return filtered_jobs
    
    def _filter_education(self, jobs: List[Dict], education: str) -> List[Dict]:
        """Filter jobs by education level"""
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
            text = (str(job.get("title", "")).lower() + " " + 
                   str(job.get("description", "")).lower())
            
            # Check if has any education mention
            has_education = any(
                keyword in text
                for all_keywords in education_keywords.values()
                for keyword in all_keywords
            )
            
            # If no education mentioned, include it
            if not has_education:
                filtered_jobs.append(job)
                continue
            
            # Check if it matches the requested education level
            matches = any(keyword in text for keyword in keywords)
            
            if matches:
                filtered_jobs.append(job)
        
        return filtered_jobs