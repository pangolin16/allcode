"""
Simple CORS Proxy Server for Úřad práce PyScript Application

This server acts as a proxy between the browser-based PyScript app
and the Úřad práce API, solving CORS restrictions.

Usage:
    pip install flask flask-cors requests
    python cors_proxy.py
    
Then update the PyScript HTML to use: http://localhost:5000/api/jobs
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import logging

app = Flask(__name__)

# Enable CORS for all routes
# In production, specify allowed origins instead of '*'
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Úřad práce API base URL
URAD_PRACE_API = "https://www.uradprace.cz/api/volnamista"

def filter_driver_license(jobs):
    """
    Filter out jobs that require a driver's license
    Checks for common Czech terms related to driving requirements
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
        title_lower = job.get('pozice', job.get('title', '')).lower()
        description_lower = job.get('popis', job.get('description', '')).lower()
        
        # Skip if any driver keyword is found
        has_driver_requirement = False
        for keyword in driver_keywords:
            if keyword in title_lower or keyword in description_lower:
                has_driver_requirement = True
                break
        
        if not has_driver_requirement:
            filtered_jobs.append(job)
    
    return filtered_jobs

def filter_salary(jobs, min_salary, max_salary):
    """Filter jobs by salary range"""
    import re
    
    filtered_jobs = []
    for job in jobs:
        salary_text = job.get('mzda', job.get('salary', ''))
        if not salary_text or salary_text == 'N/A':
            filtered_jobs.append(job)
            continue
        
        # Extract numbers
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
        
        job_salary = min(salaries)
        
        if min_salary and job_salary < min_salary:
            continue
        if max_salary and job_salary > max_salary:
            continue
        
        filtered_jobs.append(job)
    
    return filtered_jobs

def filter_education(jobs, education):
    """Filter jobs by education level"""
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
        title_lower = job.get('pozice', job.get('title', '')).lower()
        description_lower = job.get('popis', job.get('description', '')).lower()
        text = title_lower + ' ' + description_lower
        
        # If no education mentioned, include
        has_education_mention = False
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
        
        # Check if matches selected education
        matches = False
        for keyword in keywords:
            if keyword in text:
                matches = True
                break
        
        if matches:
            filtered_jobs.append(job)
    
    return filtered_jobs

@app.route('/')
def index():
    """API information page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Úřad práce CORS Proxy</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 { color: #667eea; }
            code {
                background: #f0f0f0;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: monospace;
            }
            .status {
                padding: 15px;
                background: #e8f5e9;
                border-left: 4px solid #4caf50;
                margin: 20px 0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔗 Úřad práce CORS Proxy Server</h1>
            <div class="status">
                <strong>✅ Server is running!</strong>
            </div>
            
            <h2>API Endpoint</h2>
            <p><code>GET /api/jobs</code></p>
            
            <h2>Parameters</h2>
            <ul>
                <li><code>keyword</code> - Search keyword (optional)</li>
                <li><code>location</code> - Location filter (optional)</li>
                <li><code>limit</code> - Number of results (default: 20)</li>
                <li><code>exclude_driver_license</code> - Exclude jobs requiring driver's license (optional, true/false)</li>
                <li><code>min_salary</code> - Minimum salary in CZK (optional)</li>
                <li><code>max_salary</code> - Maximum salary in CZK (optional)</li>
                <li><code>education</code> - Education level filter (optional: basic, vocational, secondary, higher, bachelor, master, phd)</li>
            </ul>
            
            <h2>Example</h2>
            <p>
                <a href="/api/jobs?keyword=IT&location=Praha&limit=10&exclude_driver_license=true&min_salary=40000&education=bachelor">
                    /api/jobs?keyword=IT&location=Praha&limit=10&exclude_driver_license=true&min_salary=40000&education=bachelor
                </a>
            </p>
            
            <h2>Usage with PyScript</h2>
            <p>Update your PyScript code to use this proxy:</p>
            <pre><code>search_url = "http://localhost:5000/api/jobs"</code></pre>
        </div>
    </body>
    </html>
    """

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    """
    Proxy endpoint for Úřad práce job search
    
    Query Parameters:
        keyword (str): Search keyword
        location (str): Location filter
        limit (int): Number of results (default: 20)
        exclude_driver_license (bool): Exclude jobs requiring driver's license
        min_salary (int): Minimum salary in CZK
        max_salary (int): Maximum salary in CZK
        education (str): Education level filter
    
    Returns:
        JSON response with job listings
    """
    
    # Get query parameters
    keyword = request.args.get('keyword', '')
    location = request.args.get('location', '')
    limit = request.args.get('limit', 20, type=int)
    exclude_driver_license = request.args.get('exclude_driver_license', 'false').lower() == 'true'
    
    # Get salary filters
    min_salary = request.args.get('min_salary', type=int)
    max_salary = request.args.get('max_salary', type=int)
    
    # Get education filter
    education = request.args.get('education', '')
    
    # Build parameters for upstream API
    params = {}
    if keyword:
        params['keyword'] = keyword
    if location:
        params['location'] = location
    params['limit'] = limit
    
    logger.info(f"Proxying request - Keyword: {keyword}, Location: {location}, Limit: {limit}, Exclude Driver License: {exclude_driver_license}, Salary: {min_salary}-{max_salary}, Education: {education}")
    
    try:
        # Make request to Úřad práce API
        response = requests.get(
            URAD_PRACE_API,
            params=params,
            timeout=10,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        
        # Check response status
        if response.status_code == 200:
            try:
                data = response.json()
                
                # Apply filters if requested
                if 'results' in data:
                    if exclude_driver_license:
                        data['results'] = filter_driver_license(data['results'])
                    if min_salary or max_salary:
                        data['results'] = filter_salary(data['results'], min_salary, max_salary)
                    if education:
                        data['results'] = filter_education(data['results'], education)
                
                logger.info(f"Successfully fetched {len(data.get('results', []))} jobs")
                return jsonify(data)
            except Exception as e:
                logger.error(f"JSON parsing error: {e}")
                return jsonify({
                    'error': 'Invalid JSON response from upstream API',
                    'status': 'error'
                }), 500
        else:
            logger.warning(f"Upstream API returned status {response.status_code}")
            return jsonify({
                'error': f'Upstream API error: {response.status_code}',
                'status': 'error'
            }), response.status_code
            
    except requests.exceptions.Timeout:
        logger.error("Request timeout")
        return jsonify({
            'error': 'Request timeout - upstream API did not respond',
            'status': 'error'
        }), 504
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")
        return jsonify({
            'error': f'Request failed: {str(e)}',
            'status': 'error'
        }), 503

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Úřad práce CORS Proxy',
        'version': '1.0.0'
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': ['/api/jobs', '/health'],
        'status': 'error'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({
        'error': 'Internal server error',
        'status': 'error'
    }), 500

if __name__ == '__main__':
    print("\n" + "="*70)
    print("Úřad práce CORS Proxy Server")
    print("="*70)
    print("\nServer starting on http://localhost:5000")
    print("\nAvailable endpoints:")
    print("  - GET  /              (Server info)")
    print("  - GET  /api/jobs      (Job search proxy)")
    print("  - GET  /health        (Health check)")
    print("\nPress Ctrl+C to stop the server")
    print("="*70 + "\n")
    
    # Run the server
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
