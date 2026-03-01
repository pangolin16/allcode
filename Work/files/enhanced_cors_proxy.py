"""
Enhanced CORS Proxy Server with File Serving
Serves both the HTML interface AND the API proxy
Run this single server for complete solution!

Usage:
    python enhanced_cors_proxy.py
    
Then open: http://localhost:8080
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import logging
import os

app = Flask(__name__)

# Enable CORS for all routes - this allows browser to make requests
CORS(app, resources={r"/*": {"origins": "*"}})

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Úřad práce API base URL
URAD_PRACE_API = "https://www.uradprace.cz/api/volnamista"

# Path to HTML files (same directory as this script)
HTML_DIR = os.path.dirname(os.path.abspath(__file__))

def filter_driver_license(jobs):
    """Filter out jobs requiring driver's license"""
    driver_keywords = [
        'řidič', 'ridic', 'řidičský průkaz', 'ridicsky prukaz', 'řp',
        'vozidlo', 'auto', 'doprava', 'řízení', 'řidičák', 'ridicak',
        'kategorie', 'c+e', 'c e', 'b+e', 'driving', 'driver', 'license',
        'vzv', 'vysokozdvižný vozík', 'vysokozdvizny vozik'
    ]
    
    filtered_jobs = []
    for job in jobs:
        title_lower = job.get('pozice', job.get('title', '')).lower()
        description_lower = job.get('popis', job.get('description', '')).lower()
        
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
        
        numbers = re.findall(r'\d+[\s\d]*', salary_text.replace(' ', ''))
        if not numbers:
            filtered_jobs.append(job)
            continue
        
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
    """Serve the main HTML page"""
    try:
        return send_from_directory(HTML_DIR, 'urad_prace_pyscript_advanced.html')
    except:
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Enhanced CORS Proxy Server</title>
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
                .status { background: #e8f5e9; padding: 15px; border-left: 4px solid #4caf50; }
                .error { background: #ffebee; padding: 15px; border-left: 4px solid #f44336; }
                code { background: #f0f0f0; padding: 2px 6px; border-radius: 3px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔗 Enhanced CORS Proxy Server</h1>
                <div class="status">
                    <strong>✅ Server is running!</strong>
                </div>
                
                <div class="error" style="margin-top: 20px;">
                    <strong>⚠️ HTML file not found</strong>
                    <p>Place <code>urad_prace_pyscript_advanced.html</code> in the same folder as this script.</p>
                </div>
                
                <h2>API Endpoint</h2>
                <p><code>GET /api/jobs</code></p>
                
                <h2>Available Files</h2>
                <ul>
                    <li><a href="/api/jobs?keyword=IT&location=Praha&limit=5">Sample API Call</a></li>
                    <li><a href="/health">Health Check</a></li>
                </ul>
                
                <h2>Setup Instructions</h2>
                <ol>
                    <li>Stop this server (Ctrl+C)</li>
                    <li>Copy <code>urad_prace_pyscript_advanced.html</code> to this folder</li>
                    <li>Restart the server: <code>python enhanced_cors_proxy.py</code></li>
                    <li>Open <a href="http://localhost:8080">http://localhost:8080</a></li>
                </ol>
            </div>
        </body>
        </html>
        """

@app.route('/<path:filename>')
def serve_file(filename):
    """Serve any file from the same directory"""
    try:
        return send_from_directory(HTML_DIR, filename)
    except:
        return f"File not found: {filename}", 404

@app.route('/api/jobs', methods=['GET'])
def get_jobs():
    """Proxy endpoint for Úřad práce job search"""
    
    # Get query parameters
    keyword = request.args.get('keyword', '')
    location = request.args.get('location', '')
    limit = request.args.get('limit', 20, type=int)
    exclude_driver_license = request.args.get('exclude_driver_license', 'false').lower() == 'true'
    min_salary = request.args.get('min_salary', type=int)
    max_salary = request.args.get('max_salary', type=int)
    education = request.args.get('education', '')
    
    # Build parameters for upstream API
    params = {}
    if keyword:
        params['keyword'] = keyword
    if location:
        params['location'] = location
    params['limit'] = limit
    
    logger.info(f"Proxying request - Keyword: {keyword}, Location: {location}, Limit: {limit}")
    
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
        
        if response.status_code == 200:
            try:
                data = response.json()
                
                # Apply filters
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
        'service': 'Enhanced Úřad práce CORS Proxy',
        'version': '2.1',
        'features': ['file_serving', 'api_proxy', 'cors_enabled']
    })

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'available_endpoints': ['/', '/api/jobs', '/health'],
        'status': 'error'
    }), 404

if __name__ == '__main__':
    print("\n" + "="*70)
    print("Enhanced Úřad práce CORS Proxy Server with File Serving")
    print("="*70)
    print("\n🚀 Server starting on http://localhost:8080")
    print("\n📁 Serving files from:", HTML_DIR)
    print("\n✅ Available endpoints:")
    print("  - http://localhost:8080              (Main HTML interface)")
    print("  - http://localhost:8080/api/jobs     (Job search API)")
    print("  - http://localhost:8080/health       (Health check)")
    print("\n📝 To use:")
    print("  1. Make sure urad_prace_pyscript_advanced.html is in this folder")
    print("  2. Open http://localhost:8080 in your browser")
    print("  3. Click 'Proxy režim' button")
    print("  4. Update proxy URL to: http://localhost:8080/api/jobs")
    print("  5. Search for jobs!")
    print("\n⏹️  Press Ctrl+C to stop the server")
    print("="*70 + "\n")
    
    # Run the server on port 8080 (different from default 5000)
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=True
    )
