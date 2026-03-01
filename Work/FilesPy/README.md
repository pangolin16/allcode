# Úřad práce ČR - Custom Job Search Tool

Custom search tool for searching job listings from Úřad práce České republiky (Czech Employment Office) with filters for location and keywords.

## Features

- 🔍 **Keyword Search**: Filter jobs by keywords (e.g., "logistika", "IT", "účetní")
- 📍 **Location Filter**: Search jobs in specific cities or regions (e.g., "Praha", "Brno")
- 🌐 **Web Interface**: Beautiful, easy-to-use web interface
- 🐍 **Python API**: Programmatic access via Python class
- 📊 **Flexible Results**: Choose how many results to display (10-100)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. **Install required packages**:
```bash
pip install -r requirements.txt
```

Or install manually:
```bash
pip install requests beautifulsoup4 flask lxml
```

## Usage

### Method 1: Web Interface (Recommended)

Start the Flask web application:

```bash
python web_search_app.py
```

Then open your browser and navigate to:
```
http://localhost:5000
```

You'll see a beautiful web interface where you can:
- Enter keywords (e.g., "logistika", "IT")
- Specify location (e.g., "Praha", "Brno")
- Choose number of results
- View results in an organized, card-based layout

### Method 2: Command Line Interface

Run the example searches:

```bash
python urad_prace_search.py
```

This will run three example searches:
1. Logistics jobs in Prague
2. All jobs in Brno
3. IT jobs anywhere

### Method 3: Use as Python Library

```python
from urad_prace_search import UradPraceSearcher

# Create searcher instance
searcher = UradPraceSearcher()

# Search for logistics jobs in Prague
jobs = searcher.search_jobs(
    keyword="logistika",
    location="Praha",
    limit=20
)

# Print results
searcher.print_results(jobs)

# Or access job data directly
for job in jobs:
    print(f"Title: {job['title']}")
    print(f"Employer: {job['employer']}")
    print(f"Location: {job['location']}")
    print(f"Salary: {job['salary']}")
    print("---")
```

## Search Examples

### By Keyword Only
```python
# Search for IT jobs anywhere
jobs = searcher.search_jobs(keyword="IT", limit=20)
```

### By Location Only
```python
# Search for all jobs in Brno
jobs = searcher.search_jobs(location="Brno", limit=20)
```

### By Keyword + Location
```python
# Search for logistics jobs in Prague
jobs = searcher.search_jobs(
    keyword="logistika",
    location="Praha",
    limit=20
)
```

### Popular Keywords (Czech)
- `logistika` - Logistics
- `IT` - IT/Technology
- `účetní` - Accounting
- `řidič` - Driver
- `skladník` - Warehouse worker
- `prodavač` - Salesperson
- `elektrikář` - Electrician
- `svářeč` - Welder
- `kuchař` - Cook

### Popular Locations
- `Praha` - Prague
- `Brno` - Brno
- `Ostrava` - Ostrava
- `Plzeň` - Pilsen
- `Liberec` - Liberec
- `Olomouc` - Olomouc
- `České Budějovice` - České Budějovice
- `Hradec Králové` - Hradec Králové

## Project Structure

```
.
├── urad_prace_search.py    # Core search functionality
├── web_search_app.py        # Flask web application
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## API Reference

### UradPraceSearcher Class

#### Methods

**`__init__()`**
- Initialize the searcher

**`search_jobs(keyword=None, location=None, limit=20)`**
- Search for jobs with filters
- **Parameters**:
  - `keyword` (str, optional): Search keyword
  - `location` (str, optional): Location filter
  - `limit` (int, optional): Max results (default: 20)
- **Returns**: List of job dictionaries

**`print_results(jobs)`**
- Pretty print job results to console
- **Parameters**:
  - `jobs` (list): List of job dictionaries

### Job Data Structure

Each job result contains:
```python
{
    'title': str,        # Job title
    'employer': str,     # Company name
    'location': str,     # Job location
    'salary': str,       # Salary information
    'type': str,         # Employment type (full-time, part-time, etc.)
    'posted': str,       # Date posted
    'url': str,          # Link to full job posting
    'description': str   # Job description (if available)
}
```

## Important Notes

⚠️ **API Availability**: The actual Úřad práce API endpoints may require authentication or may have changed since this code was written. This tool attempts to use both:
1. A potential JSON API endpoint
2. Web scraping as a fallback

If you encounter issues, you may need to:
- Check the official Úřad práce website for current API documentation
- Update the API endpoints in the code
- Use the web interface directly: https://www.uradprace.cz/volna-mista-v-cr

## Troubleshooting

### "No results found"
- Check if the keyword/location are spelled correctly (use Czech spelling)
- Try broader search terms
- Try searching without location filter first
- Visit the official website to verify data availability

### Connection errors
- Check your internet connection
- The Úřad práce website may be temporarily down
- Rate limiting may be in effect (wait a few minutes)

### Web interface not loading
- Make sure port 5000 is not in use
- Check if Flask is properly installed
- Look for error messages in the terminal

## Contributing

Feel free to:
- Report bugs
- Suggest new features
- Improve the code
- Add more search filters

## License

This tool is for educational and personal use. Please respect the terms of service of Úřad práce ČR when using this tool.

## Disclaimer

This is an unofficial tool and is not affiliated with or endorsed by Úřad práce České republiky or Ministerstvo práce a sociálních věcí ČR. For official job search, please visit: https://www.uradprace.cz

## Resources

- Official Úřad práce website: https://www.uradprace.cz
- Job search: https://www.uradprace.cz/volna-mista-v-cr
- MPSV Portal: https://portal.mpsv.cz
