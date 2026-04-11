# Comprehensive Code Cleanup Plan
**Generated:** April 7, 2026

## 🎯 Objective
Remove all unused, broken, and obsolete code across the entire project to reduce technical debt.

## 📋 Files to Delete

### 1. Backup Files (Root Directory)
- ❌ `inference_improved.py.backup_phase2_20260324_121744`
- ❌ `debug_slm.py` (one-off debug script)
- ❌ `demo_ml_suggestions.py` (one-off demo)
- ❌ `test_endpoint.py` (one-off test)
- ❌ `test_import.py` (one-off test)
- ❌ `test_path_debug.py` (one-off test)
- ❌ `test_recorder_diagnostic.py` (one-off diagnostic)

### 2. Legacy JavaScript Files
- ❌ `src/web/js/test-suite.js.backup`
- ❌ `src/web/js/*.LEGACY.js.bak` (18 files total)
  - app.LEGACY.js.bak
  - auth.LEGACY.js.bak
  - code-generation-new.LEGACY.js.bak
  - code-generation.LEGACY.js.bak
  - config.LEGACY.js.bak
  - dashboard.LEGACY.js.bak
  - navigation.LEGACY.js.bak
  - recorder.LEGACY.js.bak
  - semantic.LEGACY.js.bak
  - sidebar-debug.LEGACY.js.bak
  - sidebar-enhanced.LEGACY.js.bak
  - snippets.LEGACY.js.bak
  - test-suite.LEGACY.js.bak
  - app-functions-full.LEGACY_DO_NOT_USE.html.bak

### 3. Dataset Backup Files (Keep only latest 2)
- ❌ `resources/backups/combined-training-dataset-final.json.backup_20260318_185717`
- ❌ `resources/backups/combined-training-dataset-final.json.backup_20260318_190454`
- ❌ `resources/backups/combined-training-dataset-final.json.backup_20260318_190948`
- ❌ `resources/backups/combined-training-dataset-final.json.backup_20260318_192046`
- ❌ `resources/backups/combined-training-dataset-final.json.backup_20260318_211147`
- ❌ `resources/backups/combined-training-dataset-final.json.backup_20260318_211748`
- ❌ `resources/backups/combined-training-dataset-final.json.backup2`
- ❌ `resources/backups/combined-training-dataset-final.json.backup`
- ❌ `resources/backups/combined-training-dataset-final.json.backup_concrete_only_20260318_194400`
- ❌ `resources/backups/combined-training-dataset-final.json.backup_comprehensive`
- ✅ KEEP: `combined-training-dataset-final.json.backup-20260322_010534` (latest)
- ✅ KEEP: `combined-training-dataset-final.json.backup-advanced` (named backup)

### 4. Obsolete Documentation Files
Need to consolidate these - too many overlapping guides:
- ❌ Multiple status reports that are outdated
- ❌ Redundant quick reference guides

## 🔧 Code to Clean Up

### Python Files
1. **Remove unused imports and dead code in:**
   - `src/main/python/api_server_modular.py` - commented debug code
   - `src/main/python/browser/browser_executor.py` - TODO comments
   - `src/main/python/test_management/test_suite_handler.py` - TODO placeholders
   - `src/main/python/test_management/test_case_builder.py` - TODO placeholders

2. **Check if these are actually used:**
   - `src/main/python/generators/generation_handler_reference.py` - only imported, not used?

### JavaScript Files
1. **Remove/fix broken wait functions:**
   - `waitForProcessingSpinner()` - doesn't work in test builder
   - `waitForPageLoading()` - doesn't work in test builder
   - `searchTable()` - custom helper that won't work

2. **Clean up files with "Old code removed" comments:**
   - `src/web/js/features/test-recorder.js` (lines 209, 597, 661)

3. **Fix hardcoded user values:**
   - `src/web/js/features/healing-ui.js` - TODO: Get from auth system (lines 146, 184)
   - `src/web/js/features/test-recorder.js` - TODO: Get from logged-in user (line 890)

## 📊 Next Steps
1. Delete all backup and legacy files
2. Remove commented-out code
3. Replace TODOs with actual implementations or remove
4. Consolidate documentation files
5. Run tests to ensure nothing breaks
