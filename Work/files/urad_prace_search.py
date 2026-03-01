"""
Custom search tool for Úřad práce ČR job listings
Allows filtering by location and keywords (e.g., logistics)
"""

import requests
from bs4 import BeautifulSoup
import json
from typing import List, Dict, Optional
from urllib.parse import urlencode
import time

class UradPraceSearcher:
    """Search Úřad práce job listings with custom filters"""
    
    def __init__(self):
        self.base_url = "https://www.uradprace.cz"
        self.search_url = f"{self.base_url}/api/volnamista"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
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
        
        Args:
            keyword: Search term (e.g., "logistics", "logistika")
            location: Location filter (e.g., "Praha", "Brno")
            limit: Maximum number of results to return
            exclude_driver_license: If True, exclude jobs requiring driver's license
            min_salary: Minimum salary in CZK per month
            max_salary: Maximum salary in CZK per month
            education: Education level filter (basic, vocational, secondary, higher, bachelor, master, phd)
            
        Returns:
            List of job listings with details
        """
        
        params = {
            'limit': limit,
            'offset': 0
        }
        
        if keyword:
            params['keyword'] = keyword
            
        if location:
            params['location'] = location
        
        try:
            # Try the API endpoint first
            response = self.session.get(self.search_url, params=params, timeout=10)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    jobs = self._parse_api_response(data)
                    
                    # Apply filters
                    if exclude_driver_license:
                        jobs = self._filter_driver_license(jobs)
                    if min_salary or max_salary:
                        jobs = self._filter_salary(jobs, min_salary, max_salary)
                    if education:
                        jobs = self._filter_education(jobs, education)
                    
                    return jobs
                except json.JSONDecodeError:
                    print("API returned non-JSON response, trying web scraping...")
                    return self._scrape_web_search(keyword, location, limit, exclude_driver_license,
                                                  min_salary, max_salary, education)
            else:
                print(f"API returned status {response.status_code}, trying web scraping...")
                return self._scrape_web_search(keyword, location, limit, exclude_driver_license,
                                              min_salary, max_salary, education)
                
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            print("Trying alternative web scraping method...")
            return self._scrape_web_search(keyword, location, limit, exclude_driver_license,
                                          min_salary, max_salary, education)
    
    def _parse_api_response(self, data: Dict) -> List[Dict]:
        """Parse API JSON response"""
        jobs = []
        
        if isinstance(data, dict) and 'results' in data:
            for item in data.get('results', []):
                job = {
                    'title': item.get('pozice', item.get('title', 'N/A')),
                    'employer': item.get('zamestnavatel', item.get('employer', 'N/A')),
                    'location': item.get('misto', item.get('location', 'N/A')),
                    'salary': item.get('mzda', item.get('salary', 'N/A')),
                    'type': item.get('uvazek', item.get('type', 'N/A')),
                    'posted': item.get('datum', item.get('posted', 'N/A')),
                    'url': item.get('url', ''),
                    'description': item.get('popis', item.get('description', ''))
                }
                jobs.append(job)
        
        return jobs
    
    def _filter_driver_license(self, jobs: List[Dict]) -> List[Dict]:
        """
        Filter out jobs that require a driver's license
        Checks for common Czech terms related to driving requirements
        
        Args:
            jobs: List of job dictionaries to filter
            
        Returns:
            Filtered list of jobs without driver's license requirements
        """
        driver_keywords = [
            'řidič', 'ridic', 'řidičský průkaz', 'ridicsky prukaz', 'řp',
            'vozidlo', 'auto', 'doprava', 'řízení', 'řidičák', 'ridicak',
            'kategorie', 'c+e', 'c e', 'b+e', 'driving', 'driver', 'license',
            'vzv', 'vysokozdvižný vozík', 'vysokozdvizny vozik'
        ]
        
        filtered_jobs = []
        for job in jobs:
            # Check title and description for driver-related keywords
            title_lower = job.get('title', '').lower()
            description_lower = job.get('description', '').lower()
            
            # Skip if any driver keyword is found
            has_driver_requirement = False
            for keyword in driver_keywords:
                if keyword in title_lower or keyword in description_lower:
                    has_driver_requirement = True
                    break
            
            if not has_driver_requirement:
                filtered_jobs.append(job)
        
        return filtered_jobs
    
    def _filter_salary(self, jobs: List[Dict], min_salary: Optional[int], 
                      max_salary: Optional[int]) -> List[Dict]:
        """
        Filter jobs by salary range
        
        Args:
            jobs: List of job dictionaries to filter
            min_salary: Minimum salary in CZK
            max_salary: Maximum salary in CZK
            
        Returns:
            Filtered list of jobs within salary range
        """
        import re
        
        filtered_jobs = []
        for job in jobs:
            salary_text = job.get('salary', '')
            if not salary_text or salary_text == 'N/A':
                # Include jobs without salary info
                filtered_jobs.append(job)
                continue
            
            # Extract numbers from salary text (e.g., "30 000 - 45 000 Kč")
            numbers = re.findall(r'\d+[\s\d]*', salary_text.replace(' ', ''))
            if not numbers:
                filtered_jobs.append(job)
                continue
            
            # Convert to integers
            salaries = []
            for num_str in numbers:
                try:
                    salary = int(num_str.replace(' ', ''))
                    salaries.append(salary)
                except:
                    pass
            
            if not salaries:
                filtered_jobs.append(job)
                continue
            
            # Use the minimum salary from the range for comparison
            job_salary = min(salaries) if len(salaries) > 0 else salaries[0]
            
            # Check if salary is within range
            if min_salary and job_salary < min_salary:
                continue
            if max_salary and job_salary > max_salary:
                continue
            
            filtered_jobs.append(job)
        
        return filtered_jobs
    
    def _filter_education(self, jobs: List[Dict], education: str) -> List[Dict]:
        """
        Filter jobs by education level
        
        Args:
            jobs: List of job dictionaries to filter
            education: Education level (basic, vocational, secondary, higher, bachelor, master, phd)
            
        Returns:
            Filtered list of jobs matching education level
        """
        education_keywords = {
            'basic': ['základní', 'zakladni'],
            'vocational': ['vyučen', 'vyucen', 'střední odborné', 'stredni odborne', 'sou'],
            'secondary': ['maturita', 'střední s maturitou', 'stredni s maturitou', 'sš'],
            'higher': ['vyšší odborné', 'vyssi odborne', 'vos'],
            'bachelor': ['bakalář', 'bakalar', 'bc.', 'vysokoškolské', 'vysokoskolske'],
            'master': ['magistr', 'mgr.', 'ing.', 'vysokoškolské', 'vysokoskolske'],
            'phd': ['doktor', 'ph.d.', 'phd']
        }
        
        if education not in education_keywords:
            return jobs
        
        keywords = education_keywords[education]
        filtered_jobs = []
        
        for job in jobs:
            title_lower = job.get('title', '').lower()
            description_lower = job.get('description', '').lower()
            
            # If no education mentioned, include the job
            has_education_mention = False
            text = title_lower + ' ' + description_lower
            
            for edu_level in education_keywords.values():
                for keyword in edu_level:
                    if keyword in text:
                        has_education_mention = True
                        break
                if has_education_mention:
                    break
            
            if not has_education_mention:
                filtered_jobs.append(job)
                continue
            
            # Check if job matches selected education level
            matches = False
            for keyword in keywords:
                if keyword in text:
                    matches = True
                    break
            
            if matches:
                filtered_jobs.append(job)
        
        return filtered_jobs
    
    def _scrape_web_search(self, keyword: Optional[str], location: Optional[str], 
                          limit: int, exclude_driver_license: bool = False,
                          min_salary: Optional[int] = None, max_salary: Optional[int] = None,
                          education: Optional[str] = None) -> List[Dict]:
        """
        Fallback method: scrape the web interface
        Note: This is a simplified version and may need adjustment based on actual HTML structure
        """
        print("Using web scraping fallback method...")
        print("Note: Web scraping may be limited. For full functionality, check if there's an official API.")
        
        # This is a placeholder - actual implementation would need to analyze the HTML structure
        jobs = []
        
        search_params = {}
        if keyword:
            search_params['q'] = keyword
        if location:
            search_params['loc'] = location
            
        url = f"{self.base_url}/volna-mista-v-cr"
        if search_params:
            url += f"?{urlencode(search_params)}"
        
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # This would need to be customized based on actual page structure
            # For now, returning a message about manual inspection
            return [{
                'message': 'Web scraping requires analyzing the actual page structure',
                'url': url,
                'suggestion': 'Visit the URL to see available filters and structure'
            }]
            
        except Exception as e:
            return [{'error': str(e)}]
    
    def print_results(self, jobs: List[Dict]):
        """Pretty print search results"""
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
            
            if job.get('salary'):
                print(f"   Salary: {job['salary']}")
            
            if job.get('type'):
                print(f"   Type: {job['type']}")
            
            if job.get('posted'):
                print(f"   Posted: {job['posted']}")
            
            if job.get('url'):
                print(f"   URL: {job['url']}")
            
            print()


def main():
    """Example usage"""
    searcher = UradPraceSearcher()
    
    print("Úřad práce ČR - Custom Job Search\n")
    print("Examples:")
    print("1. Search for logistics jobs in Prague")
    print("2. Search for any jobs in Brno")
    print("3. Search for 'IT' jobs anywhere\n")
    
    # Example 1: Logistics in Prague
    print("\n--- Example 1: Logistics jobs in Prague ---")
    jobs = searcher.search_jobs(keyword="logistika", location="Praha", limit=10)
    searcher.print_results(jobs)
    
    # Example 2: Jobs in Brno
    print("\n--- Example 2: Jobs in Brno ---")
    jobs = searcher.search_jobs(location="Brno", limit=10)
    searcher.print_results(jobs)
    
    # Example 3: IT jobs
    print("\n--- Example 3: IT jobs ---")
    jobs = searcher.search_jobs(keyword="IT", limit=10)
    searcher.print_results(jobs)


if __name__ == "__main__":
    main()
