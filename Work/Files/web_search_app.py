"""
Flask web application for searching Úřad práce ČR job listings
"""
from flask import Flask, render_template_string, request, jsonify
from urad_prace_search import UradPraceSearcher
import logging
import traceback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
searcher = UradPraceSearcher()

@app.before_request
def before_request():
    logger.info(f"Request: {request.method} {request.path}")

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS,HEAD')
    response.headers.add('X-Content-Type-Options', 'nosniff')
    return response

@app.route('/api/search', methods=['GET', 'POST', 'OPTIONS'])
def search():
    if request.method == 'OPTIONS':
        return '', 200

    try:
        keyword  = request.args.get('keyword',  '').strip() or request.form.get('keyword',  '').strip()
        location = request.args.get('location', '').strip() or request.form.get('location', '').strip()

        try:
            limit = int(request.args.get('limit', 20) or request.form.get('limit', 20))
        except Exception:
            limit = 20

        exclude_driver = (request.args.get('exclude_driver_license', 'false').lower() == 'true' or
                          request.form.get('exclude_driver_license', 'false').lower() == 'true')

        try:
            min_salary = int(request.args.get('min_salary', 0) or request.form.get('min_salary', 0))
            min_salary = min_salary if min_salary > 0 else None
        except Exception:
            min_salary = None

        try:
            max_salary = int(request.args.get('max_salary', 0) or request.form.get('max_salary', 0))
            max_salary = max_salary if max_salary > 0 else None
        except Exception:
            max_salary = None

        education    = (request.args.get('education',    '') or request.form.get('education',    '')).strip() or None
        exclude_isco = (request.args.get('exclude_isco', '') or request.form.get('exclude_isco', '')).strip() or None

        full_time_only = (request.args.get('full_time_only', 'false').lower() == 'true' or
                          request.form.get('full_time_only', 'false').lower() == 'true')

        # exclude_shifts arrives as comma-separated slugs: "nocni,nepretrzity,turnus"
        raw_shifts     = (request.args.get('exclude_shifts', '') or request.form.get('exclude_shifts', '')).strip()
        exclude_shifts = [s.strip() for s in raw_shifts.split(',') if s.strip()] if raw_shifts else None

        logger.info(f"Search: keyword={keyword} location={location} limit={limit} "
                    f"min={min_salary} max={max_salary} full_time={full_time_only} "
                    f"shifts_excl={exclude_shifts}")

        jobs = searcher.search_jobs(
            keyword=keyword if keyword else None,
            location=location if location else None,
            limit=limit,
            exclude_driver_license=exclude_driver,
            min_salary=min_salary,
            max_salary=max_salary,
            education=education,
            exclude_isco=exclude_isco,
            full_time_only=full_time_only,
            exclude_shifts=exclude_shifts,
        )

        logger.info(f"Search returned {len(jobs)} jobs")
        return jsonify({'success': True, 'jobs': jobs, 'count': len(jobs),
                        'message': f'Found {len(jobs)} job listings'}), 200

    except Exception as e:
        logger.error(f"Search error: {e}")
        logger.error(traceback.format_exc())
        return jsonify({'success': False, 'error': str(e), 'jobs': [], 'count': 0,
                        'message': f'Error: {str(e)}'}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Server is running'}), 200

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Úřad práce ČR - Vyhledávač pracovních míst</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
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
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p  { opacity: 0.9; }
        .search-form { padding: 40px; background: #f8f9fa; }
        .form-group  { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: 600; color: #333; }
        input, select, textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 16px;
            font-family: inherit;
        }
        input:focus, select:focus, textarea:focus {
            outline: none; border-color: #667eea; background: #fafafa;
        }
        .shift-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
            gap: 10px;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            background: white;
        }
        .shift-grid label {
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 400;
            cursor: pointer;
            margin: 0;
        }
        .shift-grid input[type=checkbox] { width: auto; padding: 0; margin: 0; }
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
            transition: all 0.3s;
        }
        .search-btn:hover { transform: translateY(-2px); box-shadow: 0 5px 20px rgba(102,126,234,0.4); }
        .search-btn:disabled { opacity: 0.5; cursor: not-allowed; }
        .results { padding: 40px; }
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
            box-shadow: 0 5px 20px rgba(102,126,234,0.2);
            transform: translateY(-2px);
        }
        .job-number { color: #999; font-size: 0.9em; }
        .job-title  { font-size: 1.4em; margin: 10px 0; word-break: break-word; }
        .job-title a { color: #667eea; text-decoration: none; font-weight: 600; }
        .job-title a:hover { text-decoration: underline; }
        .job-meta {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 15px;
            margin-top: 15px;
            font-size: 0.95em;
        }
        .meta-item { padding: 10px; background: #f5f5f5; border-left: 4px solid #667eea; border-radius: 4px; }
        .meta-label { font-weight: 600; color: #667eea; margin-bottom: 5px; }
        .meta-value { color: #555; word-break: break-word; }
        .loading { text-align: center; padding: 40px; display: none; }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 50px; height: 50px;
            animation: spin 1s linear infinite;
            margin: 0 auto 20px;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
        .no-results { text-align: center; padding: 60px 40px; color: #666; }
        .error {
            padding: 20px; background-color: #f8d7da; border: 2px solid #f5c6cb;
            color: #721c24; border-radius: 8px; margin-bottom: 20px; font-size: 1.05em;
        }
        .success {
            padding: 15px; background-color: #d4edda; border: 2px solid #c3e6cb;
            color: #155724; border-radius: 8px; margin-bottom: 20px;
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
                    <label for="keyword">🏷️ Klíčové slovo (volitelné):</label>
                    <input type="text" id="keyword" placeholder="např. Python, IT, účetní...">
                </div>

                <div class="form-group">
                    <label for="location">📍 Místo (volitelné):</label>
                    <input type="text" id="location" placeholder="např. Praha, Brno, Ostrava...">
                </div>

                <div class="form-group">
                    <label for="minSalary">💰 Minimální mzda (Kč/měsíc):</label>
                    <input type="number" id="minSalary" placeholder="0" min="0" step="1000">
                </div>

                <div class="form-group">
                    <label for="maxSalary">💰 Maximální mzda (Kč/měsíc):</label>
                    <input type="number" id="maxSalary" placeholder="0" min="0" step="1000">
                </div>

                <div class="form-group">
                    <label style="font-weight:400;">
                        <input type="checkbox" id="excludeDriver" style="width:auto;padding:0;">
                        &nbsp;🚗 Vyloučit nabídky vyžadující řidičský průkaz
                    </label>
                </div>

                <div class="form-group">
                    <label style="font-weight:400;">
                        <input type="checkbox" id="fullTimeOnly" style="width:auto;padding:0;">
                        &nbsp;💼 Pouze plný úvazek a služební poměr (vyloučit zkrácené, DPP, DPČ)
                    </label>
                </div>

                <div class="form-group">
                    <label>🕐 Vyloučit typy směn:</label>
                    <div class="shift-grid">
                        <label><input type="checkbox" class="shiftCheck" value="jednoSm">    Jednosměnný provoz</label>
                        <label><input type="checkbox" class="shiftCheck" value="dvouSm">     Dvousměnný provoz</label>
                        <label><input type="checkbox" class="shiftCheck" value="triSm">      Třísměnný provoz</label>
                        <label><input type="checkbox" class="shiftCheck" value="ctyrSm">     Čtyřsměnný provoz</label>
                        <label><input type="checkbox" class="shiftCheck" value="deleneSm">   Dělené směny</label>
                        <label><input type="checkbox" class="shiftCheck" value="nepretrzity">Nepřetržitý provoz</label>
                        <label><input type="checkbox" class="shiftCheck" value="nocni">      Noční provoz</label>
                        <label><input type="checkbox" class="shiftCheck" value="pruznaPd">   Pružná pracovní doba</label>
                        <label><input type="checkbox" class="shiftCheck" value="turnus">     Turnusové služby</label>
                        <label><input type="checkbox" class="shiftCheck" value="neurceno">   Neurčeno</label>
                    </div>
                </div>

                <div class="form-group">
                    <label for="excludeIsco">🚫 Vyloučit CS-ISCO kódy (jeden per řádek, rozsahy jako 11110-35229):</label>
                    <textarea id="excludeIsco" rows="4"
                        placeholder="72241&#10;72242&#10;11110-35229"
                        style="font-family:monospace; font-size:14px;"></textarea>
                </div>

                <button type="submit" class="search-btn" id="searchBtn">Hledat pracovní místa</button>
            </form>
        </div>

        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p><strong>Hledám pracovní nabídky...</strong></p>
        </div>

        <div class="results" id="results"></div>
    </div>

    <script>
        document.getElementById('searchForm').addEventListener('submit', async (e) => {
            e.preventDefault();

            const keyword       = document.getElementById('keyword').value.trim();
            const location      = document.getElementById('location').value.trim();
            const minSalary     = document.getElementById('minSalary').value.trim();
            const maxSalary     = document.getElementById('maxSalary').value.trim();
            const excludeDriver = document.getElementById('excludeDriver').checked;
            const fullTimeOnly  = document.getElementById('fullTimeOnly').checked;
            const excludeIsco   = document.getElementById('excludeIsco').value.trim();
            const checkedShifts = [...document.querySelectorAll('.shiftCheck:checked')].map(cb => cb.value);

            document.getElementById('loading').style.display = 'block';
            document.getElementById('results').innerHTML = '';

            try {
                const params = new URLSearchParams();
                if (keyword)               params.append('keyword', keyword);
                if (location)              params.append('location', location);
                if (minSalary)             params.append('min_salary', minSalary);
                if (maxSalary)             params.append('max_salary', maxSalary);
                if (excludeDriver)         params.append('exclude_driver_license', 'true');
                if (fullTimeOnly)          params.append('full_time_only', 'true');
                if (excludeIsco)           params.append('exclude_isco', excludeIsco);
                if (checkedShifts.length)  params.append('exclude_shifts', checkedShifts.join(','));
                params.append('limit', '250');

                const response = await fetch(`/api/search?${params.toString()}`, {
                    method: 'GET',
                    headers: { 'Accept': 'application/json' },
                    credentials: 'same-origin'
                });

                if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                const data = await response.json();
                document.getElementById('loading').style.display = 'none';

                if (data.success === false || data.error) {
                    document.getElementById('results').innerHTML =
                        `<div class="error">❌ Chyba: ${data.error || data.message}</div>`;
                } else if (data.jobs && data.jobs.length > 0) {
                    displayResults(data.jobs);
                } else {
                    document.getElementById('results').innerHTML =
                        '<div class="no-results"><h3>😔 Žádné výsledky</h3><p>Zkuste změnit kritéria vyhledávání.</p></div>';
                }
            } catch (error) {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('results').innerHTML =
                    `<div class="error">❌ Chyba: ${error.message}</div>`;
            }
        });

        function displayResults(jobs) {
            const div = document.getElementById('results');
            let html = `<div class="success">✅ Nalezeno <strong>${jobs.length}</strong> pracovních nabídek</div>`;
            jobs.forEach((job, i) => {
                const title    = job.title    || 'Bez názvu';
                const url      = job.url      || '#';
                const salary   = job.salary   || '';
                const location = job.location || '';
                const employer = job.employer || '';
                html += `
                <div class="job-card">
                    <div class="job-number">#${i + 1}</div>
                    <div class="job-title">
                        <a href="${url}" target="_blank" rel="noopener noreferrer">${escapeHtml(title)}</a>
                    </div>
                    <div class="job-meta">
                        ${salary   ? `<div class="meta-item"><div class="meta-label">💰 Mzda</div><div class="meta-value">${escapeHtml(salary)}</div></div>` : ''}
                        ${location ? `<div class="meta-item"><div class="meta-label">📍 Místo</div><div class="meta-value">${escapeHtml(location)}</div></div>` : ''}
                        ${employer ? `<div class="meta-item"><div class="meta-label">🏢 Zaměstnavatel</div><div class="meta-value">${escapeHtml(employer)}</div></div>` : ''}
                    </div>
                </div>`;
            });
            div.innerHTML = html;
        }

        function escapeHtml(text) {
            return String(text).replace(/[&<>"']/g, m =>
                ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]));
        }
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 Úřad práce ČR - Vyhledávač pracovních míst")
    print("="*70)
    print("\n📍 Server running at: http://localhost:5000")
    print("🌐 Open your browser and visit: http://localhost:5000")
    print("\n" + "="*70 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)