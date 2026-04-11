# Web Folder Migration - Verification Checklist ✓

**Use this checklist to verify the migration is correct and won't break after refactoring.**

---

## ✅ Quick Verification Commands

Run these commands to verify everything is working:

```powershell
# 1. Verify folder structure
Write-Host "Checking structure..."
Test-Path "web" # Should be False
Test-Path "src\web" # Should be True

# 2. Verify WEB_DIR configuration
Get-Content "src\main\python\api_server_modular.py" | Select-String "WEB_DIR = "

# 3. Clear cache (important!)
Get-ChildItem "src\main\python" -Recurse -Include __pycache__,*.pyc | Remove-Item -Recurse -Force

# 4. Start server
$env:PYTHONIOENCODING='utf-8'; python src/main/python/api_server_modular.py

# 5. In another terminal, test endpoints
Invoke-WebRequest "http://localhost:5002/" -UseBasicParsing
Invoke-WebRequest "http://localhost:5002/web/css/base.css" -UseBasicParsing
Invoke-WebRequest "http://localhost:5002/web/js/core/api.js" -UseBasicParsing
```

---

## 📋 Detailed Verification Checklist

### Phase 1: Physical Structure ✓

- [ ] **Old `web/` folder removed from root**
  ```powershell
  Test-Path "web" # Should return False
  ```
  ✅ If False → Correct
  ❌ If True → **PROBLEM**: Old folder still exists, will cause conflicts

- [ ] **New `src/web/` folder exists**
  ```powershell
  Test-Path "src\web" # Should return True
  (Get-ChildItem "src\web" -Recurse -File | Measure-Object).Count # Should be 75
  ```
  ✅ If True and 75 files → Correct
  ❌ If False → **PROBLEM**: Files were not moved

- [ ] **Critical files exist in new location**
  ```powershell
  Test-Path "src\web\index-new.html"
  Test-Path "src\web\js\core\api.js"
  Test-Path "src\web\js\features\recorder-inject.js"
  Test-Path "src\web\css\base.css"
  ```
  ✅ All True → Correct
  ❌ Any False → **PROBLEM**: Missing files

---

### Phase 2: Python Configuration ✓

- [ ] **WEB_DIR correctly configured**
  ```powershell
  Get-Content "src\main\python\api_server_modular.py" | Select-String "WEB_DIR = os.path.join"
  ```
  ✅ Should show: `WEB_DIR = os.path.join(PROJECT_ROOT, 'src', 'web')`
  ❌ If shows: `WEB_DIR = os.path.join(PROJECT_ROOT, 'web')` → **PROBLEM**: Old path

- [ ] **browser_executor.py updated**
  ```powershell
  Get-Content "src\main\python\browser\browser_executor.py" | Select-String "recorder-inject.js"
  ```
  ✅ Should show: `'..', '..', 'src', 'web', 'js', 'features', 'recorder-inject.js'`
  ❌ If shows: `'..', '..', 'web', 'js', 'features', 'recorder-inject.js'` → **PROBLEM**: Old path

- [ ] **No hardcoded 'web/' paths in Python**
  ```powershell
  Get-ChildItem "src\main\python" -Recurse -Filter "*.py" | 
    Select-String "PROJECT_ROOT.*'web'" | 
    Where-Object { $_.Line -notlike "*'src', 'web'*" }
  ```
  ✅ No results → Correct
  ❌ Any results → **PROBLEM**: Hardcoded old paths exist

---

### Phase 3: Cache Cleanup ✓

- [ ] **Python cache cleared**
  ```powershell
  Get-ChildItem "src\main\python" -Recurse -Include __pycache__,*.pyc | Remove-Item -Recurse -Force
  Write-Host "✓ Cache cleared"
  ```
  ⚠️ **CRITICAL**: Always clear cache after path changes!

---

### Phase 4: Server Testing ✓

- [ ] **Server starts without errors**
  ```powershell
  $env:PYTHONIOENCODING='utf-8'; python src/main/python/api_server_modular.py
  ```
  ✅ Server shows "Running on http://127.0.0.1:5002" → Correct
  ❌ FileNotFoundError about web/ → **PROBLEM**: Path not updated or cache issue

- [ ] **Main page accessible**
  ```powershell
  $response = Invoke-WebRequest "http://localhost:5002/" -UseBasicParsing
  $response.StatusCode # Should be 200
  $response.Content -like '*AI Test Automation Studio*' # Should be True
  ```
  ✅ 200 and True → Correct
  ❌ 404 or 500 → **PROBLEM**: Routes not working

- [ ] **Static files accessible**
  ```powershell
  Invoke-WebRequest "http://localhost:5002/web/css/base.css" -UseBasicParsing
  Invoke-WebRequest "http://localhost:5002/web/js/core/api.js" -UseBasicParsing
  Invoke-WebRequest "http://localhost:5002/web/js/features/recorder-inject.js" -UseBasicParsing
  ```
  ✅ All return 200 → Correct
  ❌ Any 404 → **PROBLEM**: Static file serving broken

- [ ] **HTML pages accessible**
  ```powershell
  Invoke-WebRequest "http://localhost:5002/web/pages/test-builder.html" -UseBasicParsing
  Invoke-WebRequest "http://localhost:5002/web/pages/test-suite.html" -UseBasicParsing
  ```
  ✅ All return 200 → Correct
  ❌ Any 404 → **PROBLEM**: Page routes broken

---

### Phase 5: Functional Testing ✓

- [ ] **Test Builder loads**
  - Open http://localhost:5002/ in browser
  - Click Test Builder
  - Should load without console errors

- [ ] **Test Recorder loads**
  - Click Test Recorder
  - Should initialize without errors

- [ ] **Browser control works**
  - Initialize browser
  - Navigate to a URL
  - Recorder script should inject (check console: "Recorder initialized")

---

## 🚨 Common Issues & Solutions

### Issue 1: Server starts but pages show 404

**Symptom:**
```
404 Not Found - The requested URL was not found on the server
```

**Cause:** Old `web/` folder still exists, or WEB_DIR points to wrong location

**Solution:**
```powershell
# Check structure
Test-Path "web" # Should be False
Test-Path "src\web" # Should be True

# If old web/ exists, remove it
if (Test-Path "web") { Remove-Item "web" -Recurse -Force }

# Verify WEB_DIR
Get-Content "src\main\python\api_server_modular.py" | Select-String "WEB_DIR"
# Should show: WEB_DIR = os.path.join(PROJECT_ROOT, 'src', 'web')
```

---

### Issue 2: Server crashes with FileNotFoundError

**Symptom:**
```
FileNotFoundError: [Errno 2] No such file or directory: 'C:\\...\\web\\index-new.html'
```

**Cause:** Python cache has stale imports

**Solution:**
```powershell
# Kill all Python processes
Get-Process python* | Stop-Process -Force

# Clear ALL cache
Get-ChildItem . -Recurse -Include __pycache__,*.pyc -Force | Remove-Item -Recurse -Force

# Restart server
$env:PYTHONIOENCODING='utf-8'; python src/main/python/api_server_modular.py
```

---

### Issue 3: Recorder script not injecting

**Symptom:**
Browser console shows "Failed to load recorder script"

**Cause:** Recorder script path not updated in browser_executor.py

**Solution:**
```powershell
# Check path
Get-Content "src\main\python\browser\browser_executor.py" | Select-String "recorder-inject.js"

# Should show: '..', '..', 'src', 'web', 'js', 'features', 'recorder-inject.js'
# If not, update the file
```

---

### Issue 4: CSS/JS not loading (but pages load)

**Symptom:**
Main page loads but has no styling, console shows 404 for CSS/JS

**Cause:** HTML files have wrong paths (unlikely) or route handler broken

**Solution:**
```powershell
# Test route handler directly
Invoke-WebRequest "http://localhost:5002/web/css/base.css" -UseBasicParsing

# Check route definition
Get-Content "src\main\python\api_server_modular.py" | Select-String "@app.route\('/web"

# Should show: @app.route('/web/<path:filename>', methods=['GET'])
```

---

## ✅ Migration Success Criteria

All of these must be TRUE:

1. ✅ `Test-Path "web"` returns `False`
2. ✅ `Test-Path "src\web"` returns `True`
3. ✅ WEB_DIR = `os.path.join(PROJECT_ROOT, 'src', 'web')`
4. ✅ Server starts without FileNotFoundError
5. ✅ http://localhost:5002/ returns 200 OK
6. ✅ http://localhost:5002/web/css/base.css returns 200 OK
7. ✅ http://localhost:5002/web/js/core/api.js returns 200 OK
8. ✅ Browser loads pages without console errors
9. ✅ No Python cache files exist in src/main/python
10. ✅ No hardcoded `PROJECT_ROOT/web` paths in Python files

---

## 🔄 After Future Refactoring

**If you refactor Python code and paths break again:**

1. **Don't panic** - the web files are safe in `src/web/`

2. **Clear cache first:**
   ```powershell
   Get-ChildItem . -Recurse -Include __pycache__,*.pyc -Force | Remove-Item -Recurse -Force
   ```

3. **Verify WEB_DIR:**
   ```powershell
   Get-Content "src\main\python\api_server_modular.py" | Select-String "WEB_DIR"
   ```

4. **Check for hardcoded paths:**
   ```powershell
   Get-ChildItem "src\main\python" -Recurse -Filter "*.py" | 
     Select-String "'web'" | 
     Where-Object { $_.Line -notlike "*'src', 'web'*" }
   ```

5. **Follow this checklist from the top**

---

## 📞 Reference Files

- **Main config:** `src/main/python/api_server_modular.py` (line 101)
- **Recorder path:** `src/main/python/browser/browser_executor.py` (line 768)
- **Route handler:** `src/main/python/api_server_modular.py` (line 216)
- **Documentation:** `WEB_FOLDER_MIGRATION_COMPLETE.md`

---

**Last verified:** April 1, 2026  
**Status:** ✅ All 22 tests passing  
**Files moved:** 75  
**Python files updated:** 2  
**Documentation updated:** 3
