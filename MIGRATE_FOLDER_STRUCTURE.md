# 📁 Folder Structure Migration Guide

## Overview
Moving test data folders from `src/resources/` to root level for better organization and Git management.

---

## 🎯 Migration Summary

```
OLD Structure (Nested in resources)    →    NEW Structure (Root level)
───────────────────────────────────────────────────────────────────────────
src/resources/test_cases/              →    test_cases/
src/resources/test_sessions/           →    test_sessions/
src/resources/test_suites/             →    test_suites/
src/resources/execution_results/       →    execution_results/

STAY IN src/resources/:
- combined-training-dataset-final.json
- element_patterns.json
- config files
```

---

## 🔄 Recorder Workflow (Important!)

**Understanding Test Sessions vs Saved Test Cases:**

```
┌─────────────────────────────────────────────────────────────────────┐
│  1. USER RECORDS TEST                                                │
│     └─> Saved to: test_sessions/session_001.json (TEMPORARY)       │
│                                                                      │
│  2. USER CAN EXECUTE (Optional)                                     │
│     └─> Test sessions can be executed in test suite before saving   │
│                                                                      │
│  3. USER CLICKS "SAVE"                                              │
│     └─> Move to: test_cases/user_{username}/recorder/test_001.json │
│     └─> Delete from: test_sessions/session_001.json (CLEANUP)      │
│                                                                      │
│  4. NOW PERMANENT                                                   │
│     └─> test_cases/recorder/ is Git-tracked and CI/CD ready        │
└─────────────────────────────────────────────────────────────────────┘
```

**Key Points:**
- ⏳ **test_sessions/** = Temporary (in-progress recordings)
- ✅ **test_cases/recorder/** = Permanent (saved recordings)
- 🗑️ Sessions deleted after save (no duplicates)
- 🎭 Sessions can be executed before saving (preview/test)
- 📦 Only saved tests go to Git and CI/CD

---

## 📋 Step-by-Step Migration

### **Option 1: PowerShell Script (Automated)**

```powershell
# Run this script from: C:\Users\valaboph\AIAutomation\

# Create new root-level folders
New-Item -ItemType Directory -Path "test_cases" -Force
New-Item -ItemType Directory -Path "test_sessions" -Force
New-Item -ItemType Directory -Path "test_suites" -Force
New-Item -ItemType Directory -Path "execution_results" -Force

# Move test_cases
if (Test-Path "src\resources\test_cases") {
    Write-Host "Moving test_cases..." -ForegroundColor Cyan
    Get-ChildItem "src\resources\test_cases" -Recurse | Move-Item -Destination "test_cases\" -Force
    Remove-Item "src\resources\test_cases" -Recurse -Force
}

# Move test_sessions
if (Test-Path "src\resources\test_sessions") {
    Write-Host "Moving test_sessions..." -ForegroundColor Cyan
    Get-ChildItem "src\resources\test_sessions" -Recurse | Move-Item -Destination "test_sessions\" -Force
    Remove-Item "src\resources\test_sessions" -Recurse -Force
}

# Move test_suites
if (Test-Path "src\resources\test_suites") {
    Write-Host "Moving test_suites..." -ForegroundColor Cyan
    Get-ChildItem "src\resources\test_suites" -Recurse | Move-Item -Destination "test_suites\" -Force
    Remove-Item "src\resources\test_suites" -Recurse -Force
}

# Move execution_results
if (Test-Path "src\resources\execution_results") {
    Write-Host "Moving execution_results..." -ForegroundColor Cyan
    Get-ChildItem "src\resources\execution_results" -Recurse | Move-Item -Destination "execution_results\" -Force
    Remove-Item "src\resources\execution_results" -Recurse -Force
}

Write-Host "✅ Migration complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Update code references from 'src/resources/' to root folders"
Write-Host "2. Add .gitignore for execution_results/ and screenshots/"
Write-Host "3. Git add test_cases/ and test_suites/ for version control"
```

---

### **Option 2: Manual Migration (Step-by-step)**

**Step 1: Create New Folders**
```powershell
cd C:\Users\valaboph\AIAutomation
New-Item -ItemType Directory -Path "test_cases"
New-Item -ItemType Directory -Path "test_sessions"
New-Item -ItemType Directory -Path "test_suites"
New-Item -ItemType Directory -Path "execution_results"
```

**Step 2: Move Files**
```powershell
# Move test_cases
Move-Item "src\resources\test_cases\*" -Destination "test_cases\" -Force

# Move test_sessions
Move-Item "src\resources\test_sessions\*" -Destination "test_sessions\" -Force

# Move test_suites
Move-Item "src\resources\test_suites\*" -Destination "test_suites\" -Force

# Move execution_results
Move-Item "src\resources\execution_results\*" -Destination "execution_results\" -Force
```

**Step 3: Remove Old Empty Folders**
```powershell
Remove-Item "src\resources\test_cases" -Force
Remove-Item "src\resources\test_sessions" -Force
Remove-Item "src\resources\test_suites" -Force
Remove-Item "src\resources\execution_results" -Force
```

---

## 🔧 Code Updates Required

### **1. Update File Paths in Python Code**

**Find and replace in all Python files:**

```python
# OLD PATH PATTERNS
src/resources/test_cases/
src\\resources\\test_cases\\

# NEW PATH PATTERNS
test_cases/
test_cases\\
```

**Files to check:**
- `src/main/python/test_case_builder.py`
- `src/main/python/test_session_manager.py`
- `src/main/python/test_executor.py`
- `src/main/python/api_server_modular.py`
- Any other files that reference test folders

**Example Changes:**
```python
# OLD
TEST_CASES_DIR = "src/resources/test_cases"
SESSIONS_DIR = "src/resources/test_sessions"
SUITES_DIR = "src/resources/test_suites"
RESULTS_DIR = "src/resources/execution_results"

# NEW
TEST_CASES_DIR = "test_cases"
SESSIONS_DIR = "test_sessions"
SUITES_DIR = "test_suites"
RESULTS_DIR = "execution_results"
```

### **2. Update API Endpoints (if they expose paths)**

Check Flask routes that return file paths:
```python
# Make sure endpoints return NEW paths
@app.route('/users/me/tests/<test_id>')
def get_test(test_id):
    # OLD: file_path = f"src/resources/test_cases/{user_id}/{test_id}.json"
    # NEW:
    file_path = f"test_cases/{user_id}/{test_id}.json"
    return send_file(file_path)
```

### **3. Update Frontend JavaScript (if it references paths)**

Check `src/web/js/` files for hardcoded paths:
```javascript
// OLD
const testCasesPath = 'src/resources/test_cases/';

// NEW
const testCasesPath = 'test_cases/';
```

---

## 📝 Create .gitignore Files

### **Root .gitignore**
Create `C:\Users\valaboph\AIAutomation\.gitignore`:
```gitignore
# Execution results (NOT version controlled)
execution_results/
screenshots/

# Optional: Exclude active sessions
# test_sessions/

# Python
*.pyc
__pycache__/
.venv/
*.pyo
*.egg-info/
.pytest_cache/

# Environment
.env
*.log

# IDE
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db
```

### **execution_results/.gitignore**
Create `execution_results/.gitignore`:
```gitignore
# Ignore all execution results
*
!.gitignore
```

### **screenshots/.gitignore**
Create `screenshots/.gitignore`:
```gitignore
# Ignore all screenshots
*
!.gitignore
```

---

## ✅ Post-Migration Checklist

**Immediate Actions:**
- [ ] Run migration script (Option 1) or manual steps (Option 2)
- [ ] Verify files moved successfully
- [ ] Update Python code references (TEST_CASES_DIR, etc.)
- [ ] Update API endpoints that reference paths
- [ ] Create .gitignore files
- [ ] Test that test case creation still works
- [ ] Test that test execution still works

**Git Actions:**
- [ ] `git add test_cases/` (add test scripts to version control)
- [ ] `git add test_suites/` (add test suites to version control)
- [ ] `git add .gitignore` (exclude execution results)
- [ ] `git commit -m "Refactor: Move test data to root level"`
- [ ] `git push origin main`

**Validation:**
- [ ] Login to application
- [ ] Create a new test case → Verify saved to `test_cases/user_X/`
- [ ] Execute test → Verify results saved to `execution_results/user_X/`
- [ ] Check Git status → Ensure execution_results/ is ignored
- [ ] Check test_cases/ is tracked by Git

---

## 🚨 Rollback Plan (If Something Breaks)

```powershell
# Move everything back to old location
Move-Item "test_cases\*" -Destination "src\resources\test_cases\" -Force
Move-Item "test_sessions\*" -Destination "src\resources\test_sessions\" -Force
Move-Item "test_suites\*" -Destination "src\resources\test_suites\" -Force
Move-Item "execution_results\*" -Destination "src\resources\execution_results\" -Force

# Restore old folder structure
Remove-Item "test_cases" -Recurse -Force
Remove-Item "test_sessions" -Recurse -Force
Remove-Item "test_suites" -Recurse -Force
Remove-Item "execution_results" -Recurse -Force
```

---

## 📊 Expected Results

**Before Migration:**
```
AIAutomation/
└── src/
    └── resources/
        ├── test_cases/
        ├── test_sessions/
        ├── test_suites/
        ├── execution_results/
        └── combined-training-dataset-final.json
```

**After Migration:**
```
AIAutomation/
├── test_cases/
│   ├── user_{username}/
│   │   ├── builder/       # AI-generated tests (permanent)
│   │   └── recorder/      # Saved recorded tests (permanent)
├── test_sessions/         # Temporary recordings (moved to recorder/ on save)
├── test_suites/
├── execution_results/
└── src/
    └── resources/
        └── combined-training-dataset-final.json  (STAYS HERE)
```

---

## 🎯 Benefits of New Structure

1. **Cleaner Organization**
   - User data separated from application code
   - Follows standard project layout conventions

2. **Git-Friendly**
   - Test cases at root level (easy to find and version)
   - Execution results excluded (doesn't clutter Git history)

3. **CI/CD Ready**
   - Standard location for test files
   - Jenkins/GitHub Actions expect tests at root level

4. **Scalable**
   - Easy to add features per user folder
   - Clear separation of concerns

5. **Professional**
   - Matches industry best practices
   - Makes project structure immediately understandable

---

## 🆘 Troubleshooting

**Problem:** "Access denied" or "File in use" errors
- **Solution:** Stop Python server before migration, close any file explorers

**Problem:** "Cannot find test cases after migration"
- **Solution:** Check `TEST_CASES_DIR` variable in Python code is updated

**Problem:** Git tracking wrong files
- **Solution:** Verify .gitignore is in place BEFORE git add

**Problem:** Tests fail after migration
- **Solution:** Check file paths in generated test code (*.py, *.java)

---

## 📞 Need Help?

If migration fails or tests break:
1. Run rollback script (see above)
2. Check error logs in console
3. Verify Python code updated with new paths
4. Test one folder at a time (start with test_cases/)
