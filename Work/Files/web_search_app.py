"""
Flask web application for searching Úřad práce ČR job listings
Provides a simple web interface with location and keyword filters
"""
from flask import Flask, render_template_string, request, jsonify
from urad_prace_search import UradPraceSearcher
import json
import requests

app = Flask(__name__)
searcher = UradPraceSearcher()

# Simple test to verify connection on startup
try:
    test_url = "https://www.uradprace.cz/volna-mista-v-cr"
    requests.get(test_url, verify=False, timeout=5)
    print("✅ Connection to Úřad práce is working.")
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
            word-break: break-word;
        }
        
        .job-title a {
            color: #667eea;
            text-decoration: none;
            word-break: break-word;
        }
        
        .job-title a:hover {
            text-decoration: underline;
        }
        
        .job-meta {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        
        .meta-item {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }
        
        .meta-label {
            font-weight: 600;
            color: #667eea;
            font-size: 0.9em;
        }
        
        .meta-value {
            color: #555;
            word-break: break-word;
            padding: 5px 0;
        }
        
        .job-description {
            margin-top: 15px;
            padding: 15px;
            background: #f5f5f5;
            border-left: 4px solid #667eea;
            border-radius: 4px;
            color: #555;
            font-size: 0.95em;
            line-height: 1.5;
            word-break: break-word;
        }
        
        .job-url {
            margin-top: 15px;
            padding: 12px;
            background: #e8f0ff;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }
        
        .job-url-label {
            font-weight: 600;
            color: #667eea;
            margin-bottom: 8px;
            display: block;
            font-size: 0.9em;
        }
        
        .job-url a {
            color: #667eea;
            word-break: break-all;
            text-decoration: none;
            font-size: 0.85em;
            display: block;
        }
        
        .job-url a:hover {
            text-decoration: underline;
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
        // Helper function to safely convert to string and escape HTML
        function safeText(value) {
            if (value === null || value === undefined) {
                return '';
            }
            // Convert to string if needed
            const text = String(value);
            // Escape HTML special characters
            const map = {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#039;'
            };
            return text.replace(/[&<>"']/g, m => map[m]);
        }
        
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
                // Safely handle all job properties
                const title = safeText(job.title || 'Bez názvu');
                const employer = safeText(job.employer || '');
                const location = safeText(job.location || '');
                const salary = safeText(job.salary || '');
                const type = safeText(job.type || '');
                const posted = safeText(job.posted || '');
                const description = safeText(job.description || '');
                const url = safeText(job.url || '');
                
                const hasUrl = url && url !== '#' && url !== '';
                
                html += `
                    <div class="job-card">
                        <div class="job-title">
                            ${index + 1}. 
                            ${hasUrl ? 
                                `<a href="${url}" target="_blank" title="Otevřít nabídku práce">${title}</a>` 
                                : title
                            }
                        </div>
                        
                        <div class="job-meta">
                            ${employer ? `
                                <div class="meta-item">
                                    <span class="meta-label">🏢 Zaměstnavatel</span>
                                    <span class="meta-value">${employer}</span>
                                </div>
                            ` : ''}
                            ${location ? `
                                <div class="meta-item">
                                    <span class="meta-label">📍 Místo</span>
                                    <span class="meta-value">${location}</span>
                                </div>
                            ` : ''}
                            ${salary ? `
                                <div class="meta-item">
                                    <span class="meta-label">💰 Mzda</span>
                                    <span class="meta-value">${salary}</span>
                                </div>
                            ` : ''}
                            ${type ? `
                                <div class="meta-item">
                                    <span class="meta-label">⏰ Typ práce</span>
                                    <span class="meta-value">${type}</span>
                                </div>
                            ` : ''}
                            ${posted ? `
                                <div class="meta-item">
                                    <span class="meta-label">📅 Zveřejněno</span>
                                    <span class="meta-value">${posted}</span>
                                </div>
                            ` : ''}
                        </div>
                        
                        ${description ? `
                            <div class="job-description">
                                <strong>Popis:</strong><br>
                                ${description.substring(0, 500)}${description.length > 500 ? '...' : ''}
                            </div>
                        ` : ''}
                        
                        ${hasUrl ? `
                            <div class="job-url">
                                <span class="job-url-label">🔗 Odkaz na nabídku:</span>
                                <a href="${url}" target="_blank">${url}</a>
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