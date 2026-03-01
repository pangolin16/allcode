"""
Flask web application for searching Úřad práce ČR job listings
Provides a simple web interface with location and keyword filters
"""
from flask import Flask, render_template_string, request, jsonify
from urad_prace_search import UradPraceSearcher
import json
import requests  # Added missing import for the connection test

app = Flask(__name__)
searcher = UradPraceSearcher()

# Simple test to verify connection on startup
try:
    test_url = "https://www.uradprace.cz/api/volnamista?limit=1&location=Praha"
    # Note: verify=False is generally unsafe, but keeping as per your original logic
    requests.get(test_url, verify=False, timeout=5)
    print("✅ SSL Bypass successful: Connection to Úřad práce is working.")
except Exception as e:
    print(f"⚠️ Startup connection test failed: {e}")

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Úřad práce ČR - Vyhledávač pracovních míst</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            opacity: 0.9;
            font-size: 1.1em;
        }
        
        .search-form {
            padding: 40px;
            background: #f8f9fa;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        
        input, select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        input:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .search-btn {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        
        .search-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }
        
        .search-btn:active {
            transform: translateY(0);
        }
        
        .results {
            padding: 40px;
        }
        
        .job-card {
            background: white;
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 20px;
            transition: all 0.3s;
        }
        
        .job-card:hover {
            border-color: #667eea;
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.2);
            transform: translateY(-3px);
        }
        
        .job-title {
            font-size: 1.5em;
            color: #333;
            margin-bottom: 10px;
        }
        
        .job-meta {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        
        .meta-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .meta-label {
            font-weight: 600;
            color: #667eea;
        }
        
        .loading {
            text-align: center;
            padding: 40px;
            display: none;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .no-results {
            text-align: center;
            padding: 60px 40px;
            color: #666;
        }
        
        .no-results h3 {
            font-size: 1.5em;
            margin-bottom: 10px;
        }
        
        .example-searches {
            background: #f0f4ff;
            padding: 20px;
            border-radius: 8px;
            margin-top: 20px;
        }
        
        .example-searches h4 {
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .example-searches ul {
            list-style: none;
            padding-left: 0;
        }
        
        .example-searches li {
            padding: 5px 0;
            color: #555;
        }
        
        .example-searches li:before {
            content: "→ ";
            color: #667eea;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Vyhledávač práce</h1>
            <p>Úřad práce České republiky</p>
        </div>
        
        <div class="search-form">
            <form id="searchForm">
                <div class="form-group">
                    <label for="keyword">🏷️ Klíčové slovo (např. logistika, IT, účetní):</label>
                    <input type="text" id="keyword" name="keyword" placeholder="Zadejte klíčové slovo...">
                </div>
                
                <div class="form-group">
                    <label for="location">📍 Místo (např. Praha, Brno, Ostrava):</label>
                    <input type="text" id="location" name="location" placeholder="Zadejte město nebo region...">
                </div>
                
                <div class="form-group">
                    <label for="minSalary">💰 Minimální mzda (Kč/měsíc):</label>
                    <input type="number" id="minSalary" name="minSalary" placeholder="např. 30000" min="0" step="1000">
                </div>
                
                <div class="form-group">
                    <label for="maxSalary">💰 Maximální mzda (Kč/měsíc):</label>
                    <input type="number" id="maxSalary" name="maxSalary" placeholder="např. 50000" min="0" step="1000">
                </div>
                
                <div class="form-group">
                    <label for="education">🎓 Požadované vzdělání:</label>
                    <select id="education" name="education">
                        <option value="">Všechny</option>
                        <option value="basic">Základní</option>
                        <option value="vocational">Vyučení / Střední odborné</option>
                        <option value="secondary">Střední s maturitou</option>
                        <option value="higher">Vyšší odborné</option>
                        <option value="bachelor">Vysokoškolské (Bc.)</option>
                        <option value="master">Vysokoškolské (Mgr./Ing.)</option>
                        <option value="phd">Doktorské (Ph.D.)</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="limit">📊 Počet výsledků:</label>
                    <select id="limit" name="limit">
                        <option value="10">10</option>
                        <option value="20" selected>20</option>
                        <option value="50">50</option>
                        <option value="100">100</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label style="display: flex; align-items: center; gap: 10px; cursor: pointer;">
                        <input type="checkbox" id="excludeDriverLicense" name="excludeDriverLicense" 
                               style="width: auto; cursor: pointer;">
                        <span>🚗 Vyloučit nabídky vyžadující řidičský průkaz</span>
                    </label>
                </div>
                
                <button type="submit" class="search-btn">Hledat pracovní místa</button>
            </form>
            
            <div class="example-searches">
                <h4>💡 Příklady vyhledávání:</h4>
                <ul>
                    <li>Klíčové slovo: "logistika" + Místo: "Praha"</li>
                    <li>Klíčové slovo: "IT" + Min. mzda: 40000 Kč</li>
                    <li>Vzdělání: "Vysokoškolské (Bc.)" + Místo: "Brno"</li>
                    <li>Min. mzda: 35000 + Max. mzda: 50000 (rozsah platů)</li>
                    <li>Zaškrtnout "Vyloučit ŘP" pro pozice bez požadavku na řidičský průkaz</li>
                </ul>
            </div>
        </div>
        
        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Vyhledávání pracovních míst...</p>
        </div>
        
        <div class="results" id="results"></div>
    </div>
    
    <script>
        document.getElementById('searchForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const keyword = document.getElementById('keyword').value;
            const location = document.getElementById('location').value;
            const limit = document.getElementById('limit').value;
            const excludeDriverLicense = document.getElementById('excludeDriverLicense').checked;
            const minSalary = document.getElementById('minSalary').value;
            const maxSalary = document.getElementById('maxSalary').value;
            const education = document.getElementById('education').value;
            
            // Show loading
            document.getElementById('loading').style.display = 'block';
            document.getElementById('results').innerHTML = '';
            
            try {
                const params = new URLSearchParams();
                if (keyword) params.append('keyword', keyword);
                if (location) params.append('location', location);
                params.append('limit', limit);
                if (excludeDriverLicense) params.append('exclude_driver_license', 'true');
                if (minSalary) params.append('min_salary', minSalary);
                if (maxSalary) params.append('max_salary', maxSalary);
                if (education) params.append('education', education);
                
                const response = await fetch(`/api/search?${params}`);
                const data = await response.json();
                
                // Hide loading
                document.getElementById('loading').style.display = 'none';
                
                displayResults(data.jobs);
            } catch (error) {
                console.error('Error:', error);
                document.getElementById('loading').style.display = 'none';
                document.getElementById('results').innerHTML = 
                    '<div class="no-results"><h3>Chyba při vyhledávání</h3><p>Zkuste to prosím znovu.</p></div>';
            }
        });
        
        function displayResults(jobs) {
            const resultsDiv = document.getElementById('results');
            
            if (!jobs || jobs.length === 0) {
                resultsDiv.innerHTML = `
                    <div class="no-results">
                        <h3>😔 Žádné výsledky</h3>
                        <p>Zkuste změnit kritéria vyhledávání.</p>
                    </div>
                `;
                return;
            }
            
            let html = `<h2 style="margin-bottom: 30px; color: #333;">Nalezeno ${jobs.length} pracovních míst</h2>`;
            
            jobs.forEach((job, index) => {
                html += `
                    <div class="job-card">
                        <div class="job-title">${index + 1}. ${job.title || 'Bez názvu'}</div>
                        <div class="job-meta">
                            ${job.employer ? `
                                <div class="meta-item">
                                    <span class="meta-label">🏢 Zaměstnavatel:</span>
                                    <span>${job.employer}</span>
                                </div>
                            ` : ''}
                            ${job.location ? `
                                <div class="meta-item">
                                    <span class="meta-label">📍 Místo:</span>
                                    <span>${job.location}</span>
                                </div>
                            ` : ''}
                            ${job.salary ? `
                                <div class="meta-item">
                                    <span class="meta-label">💰 Mzda:</span>
                                    <span>${job.salary}</span>
                                </div>
                            ` : ''}
                            ${job.type ? `
                                <div class="meta-item">
                                    <span class="meta-label">⏰ Typ:</span>
                                    <span>${job.type}</span>
                                </div>
                            ` : ''}
                            ${job.posted ? `
                                <div class="meta-item">
                                    <span class="meta-label">📅 Zveřejněno:</span>
                                    <span>${job.posted}</span>
                                </div>
                            ` : ''}
                        </div>
                        ${job.url ? `
                            <div style="margin-top: 15px;">
                                <a href="${job.url}" target="_blank" style="color: #667eea; text-decoration: none; font-weight: 600;">
                                    Zobrazit detail →
                                </a>
                            </div>
                        ` : ''}
                    </div>
                `;
            });
            
            resultsDiv.innerHTML = html;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    """Render the main search page"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/search')
def search():
    """API endpoint for job search"""
    keyword = request.args.get('keyword')
    location = request.args.get('location')
    limit = int(request.args.get('limit', 20))
    
    # These parameters are extracted from the request
    exclude_driver_license = request.args.get('exclude_driver_license', 'false').lower() == 'true'
    min_salary = request.args.get('min_salary')
    max_salary = request.args.get('max_salary')
    min_salary = int(min_salary) if min_salary else None
    max_salary = int(max_salary) if max_salary else None
    education = request.args.get('education') or None

    jobs = searcher.search_jobs(
        keyword=keyword, 
        location=location, 
        limit=limit,
        exclude_driver_license=exclude_driver_license,
        min_salary=min_salary,
        max_salary=max_salary,
        education=education
    )
    
    return jsonify({
        'jobs': jobs,
        'count': len(jobs)
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("Úřad práce ČR - Web Search Application")
    print("="*60)
    print("\nStarting web server...")
    print("Open your browser and go to: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)