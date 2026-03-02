"""
Diagnostic script to discover the real Úřad práce API
"""

import requests
from bs4 import BeautifulSoup
import json
import re

# Suppress SSL warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
})

print("=" * 70)
print("ÚŘAD PRÁCE API DISCOVERY")
print("=" * 70)

# Step 1: Fetch the main page and look for API calls
print("\n📄 Step 1: Fetching main page and looking for API endpoints...")
print("-" * 70)

url = "https://up.gov.cz/volna-mista-v-cr"
response = session.get(url, timeout=15, verify=False)

if response.status_code == 200:
    print(f"✅ Page loaded successfully (HTTP 200)")
    print(f"   Page size: {len(response.content)} bytes")
    
    # Look for all script tags and extract URLs
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all script tags
    scripts = soup.find_all('script')
    print(f"   Found {len(scripts)} script tags")
    
    # Look for API endpoints in scripts
    api_patterns = [
        r'https?://[^"\s]+/api/[^"\s]+',
        r'/api/[^"\s]+',
        r'volna-mista',
        r'job-offers',
        r'nabidka',
    ]
    
    found_endpoints = set()
    
    for script in scripts:
        if script.string:
            content = script.string
            
            # Look for API URLs
            for pattern in api_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    if 'api' in match.lower() or 'job' in match.lower() or 'nabidka' in match.lower():
                        found_endpoints.add(match)
    
    if found_endpoints:
        print(f"\n   🔍 Found potential API endpoints:")
        for endpoint in sorted(found_endpoints):
            print(f"      - {endpoint}")
    else:
        print(f"\n   ⚠️  No obvious API endpoints found in scripts")
    
    # Look for data attributes
    print(f"\n   Looking for data-* attributes...")
    elements_with_data = soup.find_all(attrs={'data-api': True})
    if elements_with_data:
        print(f"   Found {len(elements_with_data)} elements with data-api")
        for elem in elements_with_data[:3]:
            print(f"      {elem}")
    
    # Look for fetch/axios calls
    print(f"\n   Looking for fetch/axios patterns in scripts...")
    fetch_pattern = r'fetch\([\'"]([^\'"]+)[\'"]'
    axios_pattern = r'axios\.[a-z]+\([\'"]([^\'"]+)[\'"]'
    
    for script in scripts:
        if script.string:
            content = script.string
            
            fetch_calls = re.findall(fetch_pattern, content)
            if fetch_calls:
                print(f"   Fetch calls found:")
                for call in fetch_calls:
                    print(f"      - {call}")
            
            axios_calls = re.findall(axios_pattern, content)
            if axios_calls:
                print(f"   Axios calls found:")
                for call in axios_calls:
                    print(f"      - {call}")

else:
    print(f"❌ Failed to load page (HTTP {response.status_code})")

# Step 2: Try common API endpoints
print("\n\n📡 Step 2: Testing common API endpoints...")
print("-" * 70)

common_endpoints = [
    "https://up.gov.cz/api/volna-mista",
    "https://up.gov.cz/api/v1/offers",
    "https://up.gov.cz/api/v2/offers",
    "https://up.gov.cz/api/job-offers",
    "https://up.gov.cz/api/nabidky",
    "https://up.gov.cz/api/volne-pozice",
    "https://www.uradprace.cz/api/volna-mista",
    "https://www.uradprace.cz/api/offers",
    "https://api.uradprace.cz/offers",
    "https://api.uradprace.cz/job-offers",
    "https://nabidky.uradprace.cz/api/offers",
]

for endpoint in common_endpoints:
    try:
        print(f"\nTesting: {endpoint}")
        response = session.get(endpoint, params={'limit': 5, 'offset': 0}, timeout=10, verify=False)
        print(f"   HTTP {response.status_code}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"   ✅ Valid JSON response!")
                print(f"   Type: {type(data)}")
                if isinstance(data, dict):
                    print(f"   Keys: {list(data.keys())[:10]}")
                    # Print first item if it's a list
                    for key in ['content', 'results', 'data', 'items', 'jobs', 'offers']:
                        if key in data:
                            items = data[key]
                            if isinstance(items, list) and items:
                                print(f"\n   Sample from '{key}':")
                                print(f"   {json.dumps(items[0], indent=4, ensure_ascii=False)[:500]}")
                            break
                elif isinstance(data, list) and data:
                    print(f"   First item sample:")
                    print(f"   {json.dumps(data[0], indent=4, ensure_ascii=False)[:500]}")
            except json.JSONDecodeError:
                print(f"   ❌ Not valid JSON")
                print(f"   Response: {response.text[:200]}")
        
        elif response.status_code == 301 or response.status_code == 302:
            print(f"   ➡️  Redirects to: {response.headers.get('Location', 'Unknown')}")
        
        elif response.status_code == 404:
            print(f"   ❌ Endpoint not found")
    
    except Exception as e:
        print(f"   ❌ Error: {e}")

# Step 3: Check for GraphQL endpoint
print("\n\n�� Step 3: Checking for GraphQL endpoint...")
print("-" * 70)

graphql_endpoints = [
    "https://up.gov.cz/graphql",
    "https://up.gov.cz/api/graphql",
    "https://www.uradprace.cz/graphql",
    "https://www.uradprace.cz/api/graphql",
]

for endpoint in graphql_endpoints:
    try:
        response = session.post(endpoint, json={"query": "{ offers { id title } }"}, timeout=10, verify=False)
        print(f"{endpoint}: HTTP {response.status_code}")
        if response.status_code != 404:
            print(f"   Response: {response.text[:200]}")
    except:
        pass

print("\n" + "=" * 70)
print("NEXT STEPS:")
print("=" * 70)
print("""
1. Open browser DevTools (F12) on https://up.gov.cz/volna-mista-v-cr
2. Go to Network tab
3. Look for XHR/Fetch requests - these are API calls
4. Click on the request to see:
   - URL (the API endpoint)
   - Request headers
   - Response (the JSON data)
5. Share the endpoint URL and a sample response

The real API should:
- Return JSON with job listings
- Have fields like: title, employer, salary, location, description, etc.
- Be paginated (with limit/offset or page parameters)
- Return proper HTTP 200 status with valid JSON
""")