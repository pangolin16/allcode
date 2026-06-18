"""
Flask web application for searching Úřad práce ČR job listings
"""
from flask import Flask, render_template_string, request, jsonify
from urad_prace_search import UradPraceSearcher
import logging
import traceback
import requests as _req
import os
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
searcher = UradPraceSearcher()

ORS_API_KEY = os.environ.get("ORS_API_KEY", "")


def geocode_address(address: str):
    """
    Geocode a free-text address to (lat, lon) using OSM Nominatim.
    Returns (lat, lon) floats or (None, None) on failure.
    """
    try:
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": address, "format": "json", "limit": 1, "countrycodes": "cz"}
        headers = {"User-Agent": "UradPraceJobSearch/1.0 (job-search-app)"}
        r = _req.get(url, params=params, headers=headers, timeout=8)
        r.raise_for_status()
        results = r.json()
        if results:
            return float(results[0]["lat"]), float(results[0]["lon"])
    except Exception as e:
        logger.warning(f"Geocoding failed for {address!r}: {e}")
    return None, None

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

        # exclude_languages arrives as comma-separated slugs: "english,czech,other"
        raw_langs = (request.args.get('exclude_languages', '') or request.form.get('exclude_languages', '')).strip()
        exclude_languages = [s.strip() for s in raw_langs.split(',') if s.strip()] if raw_langs else None

        # exclude_education arrives as comma-separated slugs: "bakalar,magister"
        raw_edus = (request.args.get('exclude_education', '') or request.form.get('exclude_education', '')).strip()
        exclude_education = [s.strip() for s in raw_edus.split(',') if s.strip()] if raw_edus else None

        raw_regions = (request.args.get('regions', '') or request.form.get('regions', '')).strip()
        regions     = [r.strip() for r in raw_regions.split(',') if r.strip()] if raw_regions else None

        # Travel-time / isochrone params
        raw_max_minutes = (request.args.get('max_minutes', '') or request.form.get('max_minutes', '')).strip()
        travel_mode     = (request.args.get('travel_mode', 'car') or request.form.get('travel_mode', 'car')).strip() or 'car'
        lat_center, lon_center = None, None
        max_minutes = None

        if raw_max_minutes and raw_max_minutes != '0':
            try:
                max_minutes = int(raw_max_minutes)
            except ValueError:
                max_minutes = None

        if location and max_minutes:
            logger.info(f"Geocoding address: {location!r}")
            lat_center, lon_center = geocode_address(location)
            if lat_center:
                logger.info(f"Geocoded to ({lat_center}, {lon_center})")
            else:
                logger.warning("Geocoding failed — falling back to text search")

        logger.info(f"Search: keyword={keyword} location={location} limit={limit} "
                    f"min={min_salary} max={max_salary} full_time={full_time_only} "
                    f"shifts_excl={exclude_shifts} langs_excl={exclude_languages} edus_excl={exclude_education} "
                    f"isochrone=({lat_center},{lon_center},{max_minutes}min,{travel_mode})")

        jobs, iso_status = searcher.search_jobs(
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
            exclude_languages=exclude_languages,
            exclude_education=exclude_education,
            regions=regions,
            lat_center=lat_center,
            lon_center=lon_center,
            max_minutes=max_minutes,
            travel_mode=travel_mode,
            ors_api_key=ORS_API_KEY,
        )

        employer_count = len({j.get('employer') for j in jobs if j.get('employer')})
        logger.info(f"Search returned {len(jobs)} jobs from {employer_count} employers | isochrone: {iso_status}")
        return jsonify({'success': True, 'jobs': jobs, 'count': len(jobs),
                'employer_count': employer_count,
                'isochrone_status': iso_status,
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
                    <label>📍 Místo / dojezdová vzdálenost (volitelné):</label>
                    <div style="display:grid; grid-template-columns: 1fr 160px 160px; gap: 10px; align-items: end;">
                        <div>
                            <label for="location" style="font-size:0.85em; color:#666; font-weight:400;">Adresa / město</label>
                            <input type="text" id="location" placeholder="např. Příbram, Chodov Praha...">
                        </div>
                        <div>
                            <label for="max_minutes" style="font-size:0.85em; color:#666; font-weight:400;">Max. dojezd</label>
                            <select id="max_minutes">
                                <option value="0">Kdekoli</option>
                                <option value="15">15 minut</option>
                                <option value="30">30 minut</option>
                                <option value="45">45 minut</option>
                                <option value="60">60 minut</option>
                            </select>
                        </div>
                        <div>
                            <label for="travel_mode" style="font-size:0.85em; color:#666; font-weight:400;">Dopravní prostředek</label>
                            <select id="travel_mode">
                                <option value="car">🚗 Auto</option>
                                <option value="bike">🚲 Kolo</option>
                                <option value="walk">🚶 Pěšky</option>
                            </select>
                        </div>
                    </div>
                    <small style="color:#888; margin-top:6px; display:block;">Dojezdový čas vyžaduje API klíč OpenRouteService (viz ORS_API_KEY). Bez něj se použije textové hledání.</small>
                </div>

                <div class="form-group">
                    <label for="regions">🗺️ Kraj (volitelné, lze vybrat více):</label>
                    <select id="regions" multiple size="5" style="height:auto;">
                        <option value="Kraj/19">Praha</option>
                        <option value="Kraj/27">Středočeský kraj</option>
                        <option value="Kraj/35">Jihočeský kraj</option>
                        <option value="Kraj/43">Plzeňský kraj</option>
                        <option value="Kraj/51">Karlovarský kraj</option>
                        <option value="Kraj/60">Ústecký kraj</option>
                        <option value="Kraj/78">Liberecký kraj</option>
                        <option value="Kraj/86">Královéhradecký kraj</option>
                        <option value="Kraj/94">Pardubický kraj</option>
                        <option value="Kraj/108">Kraj Vysočina</option>
                        <option value="Kraj/116">Jihomoravský kraj</option>
                        <option value="Kraj/124">Olomoucký kraj</option>
                        <option value="Kraj/132">Moravskoslezský kraj</option>
                        <option value="Kraj/141">Zlínský kraj</option>
                    </select>
                    <small style="color:#888; margin-top:4px; display:block;">Ctrl+klik pro výběr více krajů. Bez výběru = všechny kraje.</small>
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
                    <label>🗣️ Vyloučit podle požadované jazykové znalosti:</label>
                    <div class="shift-grid">
                        <label><input type="checkbox" class="langCheck" value="czech">   Čeština</label>
                        <label><input type="checkbox" class="langCheck" value="slovak">  Slovenština</label>
                        <label><input type="checkbox" class="langCheck" value="english"> Angličtina</label>
                        <label><input type="checkbox" class="langCheck" value="french">   Francouzština</label>
                        <label><input type="checkbox" class="langCheck" value="spanish">  Španělština</label>
                        <label><input type="checkbox" class="langCheck" value="other">    Ostatní</label>
                    </div>
                </div>

                <div class="form-group">
                    <label>🎓 Vyloučit podle požadovaného vzdělání:</label>
                    <div class="shift-grid">
                        <label><input type="checkbox" class="eduCheck" value="zakladni">      Základní vzdělání</label>
                        <label><input type="checkbox" class="eduCheck" value="stredni">      Střední bez maturity</label>
                        <label><input type="checkbox" class="eduCheck" value="maturita">     Střední s maturitou</label>
                        <label><input type="checkbox" class="eduCheck" value="vyssiodborne"> Vyšší odborné</label>
                        <label><input type="checkbox" class="eduCheck" value="bakalar">     Vysoká škola (Bc.)</label>
                        <label><input type="checkbox" class="eduCheck" value="magister">    Vysoká škola (Mgr./Ing.)</label>
                        <label><input type="checkbox" class="eduCheck" value="doktor">      Doktorský stupeň (PhD)</label>
                    </div>
                </div>

                <div class="form-group">
                    <label for="excludeIsco">🚫 Vyloučit CS-ISCO kódy (jeden per řádek, rozsahy jako 11110-35229):</label>
                    <button type="button" onclick="fillDefaultIsco()"
                        style="margin-bottom:8px; padding:6px 14px; background:#667eea; color:white; border:none; border-radius:6px; font-size:14px; cursor:pointer;">
                        Vyplnit výchozí kódy
                    </button>
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
            const maxMinutes    = document.getElementById('max_minutes').value;
            const travelMode    = document.getElementById('travel_mode').value;
            const minSalary     = document.getElementById('minSalary').value.trim();
            const maxSalary     = document.getElementById('maxSalary').value.trim();
            const excludeDriver = document.getElementById('excludeDriver').checked;
            const fullTimeOnly  = document.getElementById('fullTimeOnly').checked;
            const excludeIsco   = document.getElementById('excludeIsco').value.trim();
            const checkedShifts = [...document.querySelectorAll('.shiftCheck:checked')].map(cb => cb.value);
            const checkedLangs  = [...document.querySelectorAll('.langCheck:checked')].map(cb => cb.value);
            const checkedEdus   = [...document.querySelectorAll('.eduCheck:checked')].map(cb => cb.value);
            const selectedRegions = [...document.querySelectorAll('#regions option:checked')].map(o => o.value);

            document.getElementById('loading').style.display = 'block';
            document.getElementById('results').innerHTML = '';

            try {
                const params = new URLSearchParams();
                if (keyword)               params.append('keyword', keyword);
                if (location)              params.append('location', location);
                if (maxMinutes && maxMinutes !== '0') params.append('max_minutes', maxMinutes);
                if (travelMode)            params.append('travel_mode', travelMode);
                if (minSalary)             params.append('min_salary', minSalary);
                if (maxSalary)             params.append('max_salary', maxSalary);
                if (excludeDriver)         params.append('exclude_driver_license', 'true');
                if (fullTimeOnly)          params.append('full_time_only', 'true');
                if (excludeIsco)           params.append('exclude_isco', excludeIsco);
                if (checkedShifts.length)  params.append('exclude_shifts', checkedShifts.join(','));
                if (checkedLangs.length)   params.append('exclude_languages', checkedLangs.join(','));
                if (checkedEdus.length)    params.append('exclude_education', checkedEdus.join(','));
                if (selectedRegions.length) params.append('regions', selectedRegions.join(','));
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
                    const employerCount = data.employer_count ?? new Set(data.jobs.map(j => j.employer).filter(Boolean)).size;
                    displayResults(data.jobs, employerCount, data.isochrone_status);
                } else {
                    const isoHtml = renderIsoStatus(data.isochrone_status);
                    document.getElementById('results').innerHTML =
                        isoHtml + '<div class="no-results"><h3>😔 Žádné výsledky</h3><p>Zkuste změnit kritéria vyhledávání.</p></div>';
                }
            } catch (error) {
                document.getElementById('loading').style.display = 'none';
                document.getElementById('results').innerHTML =
                    `<div class="error">❌ Chyba: ${error.message}</div>`;
            }
        });

        function renderIsoStatus(iso) {
            if (!iso || !iso.requested) return '';
            const modeLabel = {car: '🚗 Auto', bike: '🚲 Kolo', walk: '🚶 Pěšky'}[iso.mode] || iso.mode;

            if (!iso.geocoded) {
                return `<div style="background:#fff3cd;border:1px solid #ffc107;border-radius:8px;padding:12px 16px;margin-bottom:12px;font-size:0.9em;">
                    ⚠️ <strong>Izochrona:</strong> Geocódování adresy selhalo — použito textové hledání místo.
                </div>`;
            }
            if (iso.geocoded && !iso.polygon_fetched) {
                const errMsg = iso.error || 'Neznámá chyba ORS API';
                return `<div style="background:#f8d7da;border:1px solid #f5c6cb;border-radius:8px;padding:12px 16px;margin-bottom:12px;font-size:0.9em;">
                    ❌ <strong>Izochrona selhala:</strong> ${escapeHtml(errMsg)}<br>
                    <small>Souřadnice středu: ${iso.lat?.toFixed(5)}, ${iso.lon?.toFixed(5)} | ${iso.max_minutes} min | ${modeLabel}</small><br>
                    <small>Zkontrolujte ORS_API_KEY a dostupnost API. Bylo použito textové hledání místo.</small>
                </div>`;
            }
            // Success
            return `<div style="background:#d4edda;border:1px solid #c3e6cb;border-radius:8px;padding:12px 16px;margin-bottom:12px;font-size:0.9em;">
                ✅ <strong>Izochrona aktivní</strong> — ${iso.max_minutes} min | ${modeLabel}<br>
                <small>Střed: ${iso.lat?.toFixed(5)}, ${iso.lon?.toFixed(5)} | Polygon: ${iso.polygon_vertices} vrcholů |
                Nabídky se souřadnicemi (PSČ): ${iso.jobs_with_coords} | Bez souřadnic (textový fallback): ${iso.jobs_without_coords}</small>
            </div>`;
        }

        function displayResults(jobs, employerCount, isoStatus) {
            const div = document.getElementById('results');
            let html = renderIsoStatus(isoStatus);
            html += `<div class="success">✅ Nalezeno <strong>${jobs.length}</strong> pracovních nabídek od <strong>${employerCount}</strong> zaměstnavatelů</div>`;
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

        const DEFAULT_ISCO_CODES = `1101
1102
1103
2100
3101
3102
3103
3109
11110
11121
11122
11123
11124
11125
11126
11127
11129
11130
11140
11201
11202
11203
11204
12111
12112
12113
12119
12121
12122
12123
12129
12130
12191
12192
12193
12194
12195
12196
12197
12199
12211
12212
12213
12214
12215
12219
12221
12222
12231
12232
12233
12239
13111
13112
13113
13114
13115
13121
13122
13211
13212
13213
13214
13215
13221
13222
13223
13231
13232
13233
13234
13235
13239
13241
13242
13243
13244
13245
13249
13301
13302
13303
13309
13411
13412
13413
13421
13422
13423
13424
13425
13429
13431
13432
13433
13434
13439
13441
13442
13443
13451
13452
13453
13454
13455
13456
13459
13461
13462
13491
13492
13493
13494
13495
13499
14111
14112
14113
14119
14121
14122
14123
14124
14125
14126
14129
14201
14202
14311
14312
14313
14314
14319
14391
14392
14393
14394
14395
14399
21111
21112
21113
21114
21119
21120
21131
21132
21133
21134
21135
21139
21141
21142
21143
21144
21149
21201
21202
21203
21311
21312
21313
21314
21315
21316
21317
21318
21319
21321
21322
21323
21324
21325
21326
21329
21330
21411
21412
21413
21414
21415
21416
21419
21421
21422
21423
21424
21425
21426
21427
21428
21429
21430
21441
21442
21443
21444
21445
21446
21449
21451
21452
21453
21454
21455
21456
21459
21461
21462
21463
21464
21465
21466
21469
21491
21492
21493
21494
21495
21496
21497
21498
21499
21511
21512
21513
21514
21515
21516
21517
21518
21519
21521
21522
21523
21524
21525
21526
21529
21531
21532
21533
21534
21535
21536
21539
21610
21620
21631
21632
21640
21650
21660
22111
22112
22113
22119
22121
22122
22123
22124
22125
22126
22127
22128
22129
22211
22212
22213
22214
22215
22216
22217
22218
22219
22221
22222
22223
22224
22229
22300
22400
22500
22611
22612
22613
22614
22619
22621
22622
22623
22629
22630
22641
22642
22643
22644
22649
22650
22661
22662
22663
22669
22671
22672
22673
22679
22691
22692
22693
22699
23101
23102
23103
23104
23105
23106
23107
23201
23202
23203
23204
23301
23302
23303
23411
23412
23420
23511
23512
23513
23514
23515
23519
23521
23522
23523
23524
23525
23526
23527
23529
23530
23540
23550
23560
23591
23592
23593
23594
23595
23596
23599
24111
24112
24113
24114
24115
24116
24119
24121
24122
24123
24124
24125
24129
24131
24132
24133
24134
24135
24136
24139
24210
24221
24222
24223
24224
24225
24226
24227
24228
24229
24230
24240
24311
24312
24313
24320
24331
24332
24333
24334
24335
24336
24337
24339
24340
25110
25120
25130
25210
25220
25230
25290
26111
26112
26113
26114
26119
26121
26122
26123
26124
26129
26191
26192
26193
26194
26195
26196
26199
26211
26212
26213
26220
26311
26312
26321
26322
26323
26324
26325
26326
26329
26330
26341
26342
26343
26344
26345
26349
26351
26352
26353
26354
26355
26356
26357
26359
26360
26410
26421
26422
26423
26424
26429
26431
26432
26511
26512
26513
26514
26519
26521
26522
26523
26524
26525
26529
26531
26532
26533
26534
26539
26541
26542
26543
26544
26549
26550
26561
26562
26569
26590
31111
31112
31113
31114
31115
31116
31117
31119
31121
31122
31123
31124
31125
31126
31127
31128
31129
31131
31132
31133
31134
31135
31136
31137
31138
31139
31141
31142
31143
31144
31145
31146
31147
31148
31149
31151
31152
31153
31154
31155
31156
31157
31158
31159
31161
31162
31163
31164
31165
31166
31167
31169
31171
31172
31173
31174
31175
31176
31177
31178
31179
31181
31182
31183
31189
31191
31192
31193
31194
31195
31196
31197
31198
31199
31211
31212
31213
31221
31222
31223
31224
31225
31226
31227
31228
31229
31230
31311
31312
31321
31322
31330
31340
31351
31352
31353
31354
31359
31391
31392
31399
31411
31412
31413
31414
31415
31419
31421
31422
31423
31424
31425
31429
31430
31510
31520
31531
31532
31533
31534
31535
31536
31540
31550
32111
32112
32113
32119
32121
32122
32129
32130
32141
32142
32143
32144
32149
32211
32213
32220
32300
32400
32510
32520
32530
32540
32551
32553
32559
32560
32570
32580
32591
32592
32593
32599
33110
33121
33122
33129
33131
33132
33133
33134
33135
33136
33137
33138
33139
33141
33142
33143
33151
33152
33211
33212
33219
33220
33230
33240
33311
33312
33313
33320
33331
33332
33333
33334
33335
33336
33337
33339
33340
33391
33392
33393
33394
33395
33396
33397
33399
33411
33412
33413
33414
33415
33416
33417
33419
33420
33431
33432
33433
33434
33435
33436
33437
33438
33439
33440
33511
33512
33513
33514
33515
33516
33517
33518
33519
33520
33530
33540
33551
33552
33553
33554
33555
33590
34111
34112
34113
34119
34121
34122
34123
34124
34125
34126
34127
34129
34130
34210
34221
34222
34223
34230
34311
34312
34313
34319
34321
34322
34323
34324
34325
34329
34331
34332
34333
34334
34339
34341
34342
34343
34344
34349
34351
34352
34353
34354
34355
34359
35110
35120
35130
35140
35211
35212
35213
35214
35219
35221
35222
35223
35224
35225
35226
35227
35228
35229
42123
42124
42220
42230
43232
51111
51201
51202
51203
51310
51321
51322
51329
51410
51421
51422
51429
51522
51641
51642
51643
51644
51645
51649
51650
52110
52120
52210
52220
52231
52232
52233
52234
52235
52236
52237
52238
52239
52301
52302
52303
52304
52305
52309
52410
52420
52430
52440
52450
52460
53296
54141
62220
62230
71121
71122
71123
71124
71130
71140
71151
71152
71191
71193
71194
71195
71199
71210
71221
71222
71223
71231
71232
71240
71250
71261
71262
71263
71264
71265
71266
71267
71270
71311
71312
71313
71321
71322
71323
71324
71329
71332
72111
72112
72113
72121
72122
72123
72131
72132
72210
72223
72225
72226
72241
72242
72243
72311
72312
72313
72314
72319
72320
72331
72332
72333
72334
72335
72336
72337
72339
72340
73111
73112
73113
73119
73121
73122
73130
73141
73142
73149
73151
73152
73161
73162
73163
73169
73171
73172
73173
73192
73193
73199
74110
74121
74122
74123
74131
74132
74210
74220
75121
75122
75123
75153
75154
75160
75220
75311
75312
75313
75321
75322
75323
75329
75330
75341
75342
75361
75362
75363
75410
75491
75492
75499
81111
81112
81113
81114
81115
81116
81117
81119
81121
81122
81131
81132
81133
81139
83111
83112
83113
83114
83119
83121
83210
83221
83222
83223
83311
83312
83313
83314
83321
83322
83323
83324
83325
83326
83329
83411
83412
83431
83449
83501
83502
83509
93123
93130
93320
94120
95200`;

        function fillDefaultIsco() {
            document.getElementById('excludeIsco').value = DEFAULT_ISCO_CODES;
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