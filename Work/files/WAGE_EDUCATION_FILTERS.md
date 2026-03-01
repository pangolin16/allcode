# Wage and Education Filters - Feature Documentation

## 🆕 New Features: Salary Range and Education Level Filters

All versions of the Úřad práce job search tool now include advanced filtering options for salary ranges and education requirements.

## ✨ What's New

### 1. Salary Range Filter 💰
Two new input fields allow you to filter jobs by salary:

**Minimum Salary (Kč/měsíc)**
- Filter out jobs paying below your target
- Example: Enter `30000` to only see jobs paying 30,000 CZK or more per month

**Maximum Salary (Kč/měsíc)**
- Filter out jobs paying above your range  
- Example: Enter `50000` to only see jobs paying up to 50,000 CZK per month

You can use both together to define a specific salary range!

### 2. Education Level Filter 🎓
A dropdown menu to filter jobs by required education:

**Options:**
- **Všechny** (All) - No education filter
- **Základní** (Basic) - Elementary education
- **Vyučení / Střední odborné** (Vocational) - Trade school / Vocational secondary
- **Střední s maturitou** (Secondary) - Secondary with diploma
- **Vyšší odborné** (Higher Vocational) - Higher vocational education
- **Vysokoškolské (Bc.)** (Bachelor's) - Bachelor's degree
- **Vysokoškolské (Mgr./Ing.)** (Master's) - Master's degree
- **Doktorské (Ph.D.)** (Doctorate) - PhD degree

## 🎯 How They Work

### Salary Filtering
The system extracts salary information from job postings and compares it with your specified range.

**Detection Examples:**
- "30 000 - 45 000 Kč" → Extracts: 30,000 and 45,000
- "Plat od 35 000 Kč" → Extracts: 35,000
- "40000 Kč/měsíc" → Extracts: 40,000

**Filtering Logic:**
- Uses the **minimum** salary from ranges for comparison
- Jobs without salary information are **included** (not filtered out)
- Example: If min_salary = 35000, job with "30 000 - 45 000 Kč" is included (30,000 ≥ 35000? No, but 45,000 is)

### Education Filtering
The system searches for Czech education terms in job titles and descriptions.

**Detection Keywords:**
```python
{
    'basic': ['základní', 'zakladni'],
    'vocational': ['vyučen', 'vyucen', 'střední odborné', 'sou'],
    'secondary': ['maturita', 'střední s maturitou', 'sš'],
    'higher': ['vyšší odborné', 'vyssi odborne', 'vos'],
    'bachelor': ['bakalář', 'bakalar', 'bc.', 'vysokoškolské'],
    'master': ['magistr', 'mgr.', 'ing.', 'vysokoškolské'],
    'phd': ['doktor', 'ph.d.', 'phd']
}
```

**Filtering Logic:**
- Jobs **without** education requirements mentioned are **included**
- Only filters out jobs explicitly requiring different education levels
- Example: Selecting "Bachelor's" includes jobs without education requirements + jobs requiring bachelor's

## 📦 Usage Examples

### Example 1: IT Jobs Paying 40K+
```
Keyword: IT
Location: Praha
Min Salary: 40000
Max Salary: (leave empty)
Education: (All)
```

**Result:** IT positions in Prague paying at least 40,000 CZK/month

### Example 2: Entry-Level Accounting (30K-40K)
```
Keyword: účetní
Min Salary: 30000
Max Salary: 40000
Education: Střední s maturitou
```

**Result:** Accounting jobs requiring secondary education, paying 30-40K CZK

### Example 3: High-Paying University Graduate Positions
```
Min Salary: 50000
Education: Vysokoškolské (Bc.)
Location: Brno
```

**Result:** Jobs in Brno requiring bachelor's degree, paying 50K+ CZK

### Example 4: Skilled Trades Without Driver's License
```
Keyword: elektrikář
Education: Vyučení
Min Salary: 35000
☑️ Exclude Driver License
```

**Result:** Electrician positions requiring vocational training, 35K+, no driving required

## 🔍 Real-World Scenarios

### Scenario 1: Fresh Graduate Job Search
**Profile:** Recent university graduate, flexible on location, wants market-rate salary

**Search:**
- Education: `Vysokoškolské (Bc.)`
- Min Salary: `35000`
- Keyword: your field

**Result:** Entry-level positions appropriate for your education level with reasonable starting salaries

### Scenario 2: Experienced Professional Filtering
**Profile:** 5+ years experience, looking for senior roles

**Search:**
- Keyword: `vedoucí` or `senior`
- Min Salary: `60000`
- Education: `Vysokoškolské (Mgr./Ing.)`

**Result:** Leadership positions with compensation matching your experience

### Scenario 3: Career Change Without Degree
**Profile:** Experienced worker without university degree

**Search:**
- Education: `Střední s maturitou` or `Vyučení`
- Min Salary: `40000`
- Location: your city

**Result:** Well-paying positions that don't require university education

### Scenario 4: Avoiding Overqualified Positions
**Profile:** Vocational training, don't want jobs requiring degrees

**Search:**
- Keyword: your field
- Education: `Vyučení`
- Location: your region

**Result:** Positions appropriate for your education level (filters out degree requirements)

## 💻 Code Examples

### Python API
```python
from urad_prace_search import UradPraceSearcher

searcher = UradPraceSearcher()

# Search for IT jobs with salary 40-60K, bachelor's degree
jobs = searcher.search_jobs(
    keyword="IT",
    location="Praha",
    min_salary=40000,
    max_salary=60000,
    education="bachelor"
)

searcher.print_results(jobs)
```

### Flask API
```bash
# IT jobs in Prague, 40K+, bachelor's degree required
curl "http://localhost:5000/api/search?keyword=IT&location=Praha&min_salary=40000&education=bachelor"

# Accounting jobs, salary range 30-45K
curl "http://localhost:5000/api/search?keyword=ucetni&min_salary=30000&max_salary=45000"
```

### CORS Proxy API
```bash
# High-paying tech jobs with master's degree
curl "http://localhost:5000/api/jobs?keyword=programator&min_salary=60000&education=master"
```

### PyScript (Browser)
Simply fill in the form fields:
1. Enter min/max salary values
2. Select education level from dropdown
3. Add other filters (keyword, location)
4. Click "Hledat pracovní místa"

## ⚙️ Technical Implementation

### Method Signatures

#### Python
```python
def search_jobs(self, 
               keyword: Optional[str] = None,
               location: Optional[str] = None,
               limit: int = 20,
               exclude_driver_license: bool = False,
               min_salary: Optional[int] = None,
               max_salary: Optional[int] = None,
               education: Optional[str] = None) -> List[Dict]:
    """Search for jobs with all available filters"""
```

#### Flask API
```python
@app.route('/api/search')
def search():
    keyword = request.args.get('keyword')
    location = request.args.get('location')
    min_salary = request.args.get('min_salary', type=int)
    max_salary = request.args.get('max_salary', type=int)
    education = request.args.get('education')
    # ...
```

### Filter Functions

#### Salary Filter
```python
def _filter_salary(self, jobs, min_salary, max_salary):
    """
    Extracts salary from text like:
    - "30 000 - 45 000 Kč"
    - "Plat od 35 000 Kč"
    - "40000 Kč/měsíc"
    
    Compares extracted minimum salary with filters
    """
```

#### Education Filter
```python
def _filter_education(self, jobs, education):
    """
    Searches for education keywords in:
    - Job title
    - Job description
    
    Includes jobs without education requirements
    """
```

## 📊 Filter Combinations

The power of these filters comes from combining them:

### Powerful Combinations

**1. Salary + Education**
```
Min: 50000, Education: Bachelor's
→ Well-paying graduate positions
```

**2. Salary + Location + Education**
```
Location: Praha, Min: 45000, Education: Master's
→ Premium positions for experienced graduates in Prague
```

**3. All Filters Combined**
```
Keyword: logistika
Location: Brno
Min: 35000, Max: 50000
Education: Střední s maturitou
☑️ Exclude Driver License
→ Specific logistics roles with no driving, specific salary range, education level
```

## ⚠️ Important Notes

### Limitations

**Salary Filtering:**
1. **Text-Based Detection**: Relies on salary being mentioned in description
2. **Format Variations**: May miss unusual formats
3. **Jobs Without Salary**: Included by default (not filtered out)
4. **Range Handling**: Uses minimum of salary range for comparison

**Education Filtering:**
1. **Keyword Matching**: Based on Czech education terms
2. **Implicit Requirements**: May miss unstated requirements
3. **Jobs Without Requirements**: Included by default
4. **Language**: Optimized for Czech job postings

### Best Practices

**DO:**
- ✅ Use realistic salary ranges based on market rates
- ✅ Consider your actual education level
- ✅ Combine with location and keyword filters
- ✅ Try multiple search variations
- ✅ Review job descriptions for full requirements

**DON'T:**
- ❌ Set unrealistic salary expectations
- ❌ Filter too strictly (may miss good opportunities)
- ❌ Rely solely on filters (always read descriptions)
- ❌ Assume all requirements are captured
- ❌ Use filters as only decision criteria

## 🔄 Backward Compatibility

✅ **Fully backward compatible**
- All new parameters are optional
- Default behavior unchanged
- Existing code works without modifications
- Empty fields = no filtering applied

## 📈 Performance

- **Salary Filter**: O(n) where n = number of jobs
- **Education Filter**: O(n) where n = number of jobs
- **Combined**: Filters applied sequentially
- **Impact**: Minimal overhead, client-side filtering

## 🎓 Education Level Guide

### Czech Education System

**Základní (Basic)**
- Elementary education
- Ages 6-15
- Jobs: Entry-level, manual labor

**Vyučení / Střední odborné (Vocational)**
- Trade school
- 3-4 years after elementary
- Jobs: Skilled trades, technicians

**Střední s maturitou (Secondary)**
- High school with diploma
- 4 years after elementary
- Jobs: Office work, junior positions

**Vyšší odborné (Higher Vocational)**
- Post-secondary vocational
- 2-3 years after secondary
- Jobs: Specialized technicians

**Vysokoškolské Bc. (Bachelor's)**
- University bachelor's degree
- 3-4 years
- Jobs: Professional entry-level

**Vysokoškolské Mgr./Ing. (Master's)**
- University master's degree
- 2-3 years after bachelor's
- Jobs: Senior professional, specialist

**Doktorské Ph.D. (Doctorate)**
- Doctoral degree
- 3-4 years after master's
- Jobs: Research, academia, senior expert

## 💡 Future Enhancements

Potential improvements:

1. **Salary Intelligence**
   - Average salary by position
   - Salary distribution visualization
   - Market rate comparisons

2. **Education Matching**
   - "Best fit" recommendations
   - Related education equivalents
   - International degree recognition

3. **Advanced Filtering**
   - Experience years
   - Contract type (full-time, part-time, contract)
   - Remote work options
   - Company size

4. **Smart Suggestions**
   - "Similar searches"
   - "Jobs in your range"
   - Salary negotiation tips

## 📝 Change Log

### Version 2.1 - February 2026
- ✨ Added salary range filters (min/max)
- ✨ Added education level filter
- 🔧 Updated all UI versions (PyScript, Flask)
- 📚 Enhanced filter combination logic
- 🧪 Comprehensive Czech education keyword list

### Version 2.0 - February 2026
- ✨ Added driver's license exclusion filter

### Version 1.0 - February 2026
- 🎉 Initial release

## 🤝 Contributing

To improve the filters:

1. **Add Salary Formats**: Extend regex patterns in `_filter_salary`
2. **Add Education Terms**: Update `education_keywords` dictionary
3. **Improve Detection**: Enhance matching algorithms
4. **Test Edge Cases**: Add test cases for various formats

## 📞 Support

If you encounter issues:

1. **Check Input**: Verify salary values are numbers
2. **Test Individual Filters**: Try each filter separately
3. **Review Results**: Compare filtered vs unfiltered
4. **Check Logs**: Browser console or server logs
5. **Report Issues**: Document cases where filters don't work

## 🎉 Summary

The new salary and education filters empower job seekers to:
- ✅ Focus on positions matching their salary expectations
- ✅ Find jobs appropriate for their education level
- ✅ Save time by filtering irrelevant positions
- ✅ Make more informed career decisions
- ✅ Combine multiple criteria for precise searches

Combined with the existing location, keyword, and driver's license filters, you now have a comprehensive job search tool tailored to your specific needs!
