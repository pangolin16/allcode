# Troubleshooting Guide - Úřad práce Job Search Tool

## Common Errors and Solutions

### Error: `AttributeError: currentMode`

**Full Error:**
```
Uncaught (in promise) PythonError: Traceback (most recent call last):
  File "<exec>", line 466, in handle_search
AttributeError: currentMode
```

**Cause:** PyScript trying to access JavaScript variable `currentMode` that isn't properly exposed to Python.

**Solution:** This has been fixed in the latest version. The JavaScript variable is now stored in `window.currentMode` instead of a local variable, making it accessible to PyScript via `js.window.currentMode`.

**If you still see this error:**
1. Download the latest version of the HTML file
2. Clear your browser cache (Ctrl+F5 or Cmd+Shift+R)
3. Reload the page

---

### Error: PyScript Not Loading

**Symptoms:**
- Blank page
- Spinning loader that never finishes
- No response when clicking buttons

**Solutions:**

**1. Check Internet Connection**
```
PyScript loads from CDN - you need internet access
```

**2. Clear Browser Cache**
```
Press Ctrl+F5 (Windows) or Cmd+Shift+R (Mac)
```

**3. Try Different Browser**
```
Chrome 90+, Firefox 90+, Edge 90+, Safari 15.4+
Internet Explorer is NOT supported
```

**4. Check Browser Console**
```
Press F12 → Console tab
Look for error messages
```

**5. Wait for Initial Load**
```
First load takes 10-30 seconds (PyScript downloads ~10MB)
Subsequent loads are faster (cached)
```

---

### Error: `CORS Policy Error`

**Full Error:**
```
Access to fetch at 'https://www.uradprace.cz/...' from origin '...' 
has been blocked by CORS policy
```

**Cause:** Browser security prevents direct API calls to external domains.

**Solutions:**

**Option 1: Use Demo Mode (Recommended for Testing)**
- Click "Demo režim" button
- Uses mock data instead of real API
- No CORS issues

**Option 2: Run CORS Proxy Server**
```bash
# Install dependencies
pip install flask flask-cors requests

# Run proxy server
python cors_proxy.py

# Then in browser:
# 1. Click "Proxy režim"
# 2. Verify proxy URL is http://localhost:5000/api/jobs
# 3. Search as normal
```

**Option 3: Use Flask Version Instead**
```bash
python web_search_app.py
# Open http://localhost:5000 in browser
```

---

### Error: `TypeError: int() argument must be a string`

**Cause:** Empty salary field being converted to integer.

**Solution:** This is fixed in the latest version. Empty fields now default to `None`.

**Manual Fix (if needed):**
```python
# Before (causes error):
min_salary = int(js.document.getElementById('minSalary').value)

# After (fixed):
min_salary_value = js.document.getElementById('minSalary').value
min_salary = int(min_salary_value) if min_salary_value else None
```

---

### Error: Form Submission Doesn't Work

**Symptoms:**
- Clicking "Hledat pracovní místa" does nothing
- No loading spinner appears
- No results shown

**Solutions:**

**1. Check Browser Console**
```
F12 → Console tab
Look for JavaScript errors in red
```

**2. Verify PyScript is Ready**
```
You should see: "PyScript job search application ready!" in console
If not, PyScript didn't load properly
```

**3. Wait for Page Load**
```
Don't click search until page fully loads
Look for "PyScript ready" message
```

**4. Try Different Browser**
```
Some older browsers don't support PyScript
Use Chrome, Firefox, or Edge (recent versions)
```

---

### Error: No Results Found (Always)

**Symptoms:**
- Every search shows "Žádné výsledky"
- Even very broad searches return nothing

**Solutions:**

**In Demo Mode:**
```
Demo data is filtered by your search criteria
Try:
- Broader keywords (e.g., just "IT" not "Senior IT Architect")
- Remove salary filters
- Remove education filter
- Uncheck "Exclude driver license"
```

**In Proxy Mode:**
```
1. Check proxy server is running:
   python cors_proxy.py
   
2. Check proxy URL is correct:
   Should be: http://localhost:5000/api/jobs
   
3. Try demo mode first to verify form works
```

---

### Error: Salary Filter Not Working

**Symptoms:**
- Jobs outside salary range appear in results
- Salary filter seems to have no effect

**Explanation:**
Jobs **without** salary information are **included** by default. This is intentional because many good jobs don't list salaries.

**Behavior:**
```
Min: 40000, Max: 60000

✅ Included:
- Jobs with 45000 CZK
- Jobs with "40000 - 55000 CZK"  
- Jobs with NO salary listed

❌ Excluded:
- Jobs with 30000 CZK
- Jobs with 70000 CZK
```

**If this is a real bug:**
Check browser console for errors in filter function.

---

### Error: Education Filter Not Working

**Symptoms:**
- Jobs with wrong education level appear
- Filter seems to have no effect

**Explanation:**
Jobs **without** education requirements mentioned are **included** by default. The filter only excludes jobs explicitly requiring a *different* education level.

**Behavior:**
```
Selected: "Vysokoškolské (Bc.)"

✅ Included:
- Jobs requiring bachelor's
- Jobs with NO education requirement listed

❌ Excluded:
- Jobs explicitly requiring only "vyučení" (vocational)
- Jobs requiring PhD
```

---

### Performance Issues

**Symptoms:**
- Page is very slow
- Searches take a long time
- Browser becomes unresponsive

**Solutions:**

**1. Reduce Result Limit**
```
Change from 50 to 20 or 10 results
Fewer results = faster processing
```

**2. Close Unused Browser Tabs**
```
PyScript uses significant memory
Close other tabs to free up resources
```

**3. Use Flask Version Instead**
```bash
python web_search_app.py
# Server-side processing is faster
```

**4. Update Browser**
```
Old browsers are slower with PyScript
Update to latest version
```

---

## Browser-Specific Issues

### Chrome
**Issue:** PyScript warnings in console
**Solution:** Ignore warnings, they're normal for PyScript

### Firefox
**Issue:** Slower loading than Chrome
**Solution:** Wait longer on first load, or use Chrome

### Safari
**Issue:** Some PyScript features may not work
**Solution:** Use Chrome or Firefox for best compatibility

### Mobile Browsers
**Issue:** Very slow or crashes
**Solution:** PyScript is not optimized for mobile - use desktop

---

## How to Report Issues

If you encounter an error not listed here:

**1. Open Browser Console (F12)**
```
Copy the full error message
Take a screenshot if possible
```

**2. Note Your Setup**
```
- Browser name and version
- Operating system
- Which file you're using (basic or advanced)
- What mode (demo or proxy)
```

**3. List Steps to Reproduce**
```
1. Opened file in browser
2. Clicked "Proxy režim"  
3. Entered "IT" in keyword field
4. Clicked search button
5. Got error: [paste error here]
```

**4. Provide the Error**
```
Include:
- Console error messages
- Network errors (F12 → Network tab)
- Any red text in console
```

---

## Quick Fixes Checklist

When something goes wrong, try these in order:

- [ ] Refresh the page (F5)
- [ ] Clear cache and hard reload (Ctrl+F5)
- [ ] Check browser console for errors (F12)
- [ ] Try a different browser
- [ ] Switch to Demo mode
- [ ] Reduce result limit to 10
- [ ] Remove all filters and search again
- [ ] Download the latest version
- [ ] Try the Flask version instead (`python web_search_app.py`)

---

## Known Limitations

### PyScript Version
- ⚠️ First load is slow (10-30 seconds)
- ⚠️ Limited to demo mode without proxy server
- ⚠️ High memory usage
- ⚠️ Not ideal for mobile devices
- ⚠️ CORS restrictions prevent direct API access

### Demo Mode
- ⚠️ Shows mock data (not real job listings)
- ⚠️ Limited to ~8 sample jobs
- ⚠️ Useful for testing interface only

### Proxy Mode
- ⚠️ Requires running local Python server
- ⚠️ Need to install Flask and dependencies
- ⚠️ Proxy must be running before searching

---

## Alternative Solutions

If PyScript version doesn't work for you:

### 1. Flask Web App (Recommended)
```bash
pip install flask requests beautifulsoup4
python web_search_app.py
# Open http://localhost:5000
```

**Advantages:**
- Faster
- More reliable
- No CORS issues
- Better performance

### 2. Python CLI
```bash
python urad_prace_search.py
```

**Advantages:**
- No browser needed
- Direct Python execution
- Easy to modify

### 3. Python Library
```python
from urad_prace_search import UradPraceSearcher
searcher = UradPraceSearcher()
jobs = searcher.search_jobs(keyword="IT", location="Praha")
```

**Advantages:**
- Full programmatic control
- Integrate into your own scripts
- No UI needed

---

## Getting Help

**Check Documentation:**
- README.md - General usage
- README_PYSCRIPT.md - PyScript-specific info  
- DRIVER_LICENSE_FILTER.md - Driver license filter
- WAGE_EDUCATION_FILTERS.md - Salary and education filters

**Try Examples:**
- Start with simplest search (no filters)
- Try demo mode first
- Use example searches from documentation

**Debug Mode:**
Open browser console (F12) to see detailed logs from PyScript.

---

## Version Information

**Current Version:** 2.1

**Fixed in This Version:**
- ✅ `AttributeError: currentMode` - Fixed
- ✅ Empty salary field errors - Fixed
- ✅ JavaScript to PyScript communication - Improved
- ✅ Better error handling - Added

**Known Issues:**
- CORS errors in proxy mode (requires proxy server)
- Slow first load (PyScript limitation)
- Demo mode shows limited results (intentional)

---

## Contact & Support

This is an unofficial tool. For official job search, visit:
**https://www.uradprace.cz**

For issues with this tool:
1. Check this troubleshooting guide
2. Review documentation files
3. Try alternative versions (Flask, CLI)
4. Use demo mode for testing
