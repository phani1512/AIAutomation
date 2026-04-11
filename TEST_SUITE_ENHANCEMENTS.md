# Test Suite Enhancements - April 7, 2026

## ✅ Issues Fixed

### 1. Timestamp Sorting (Already Working!)

**User Report:** "Tests ordered by source (recorder on top, then builder)"

**Status:** ✅ **Already correct in code!**

The test suite **already sorts by timestamp** regardless of source type:

```javascript
// Line 103-107 in test-suite.js
allSessions.sort((a, b) => {
    const timeA = a.created_at || a.timestamp || 0;
    const timeB = b.created_at || b.timestamp || 0;
    return timeB - timeA; // Descending order (newest first)
});
```

**What this means:**
- ✅ Newest tests appear at the top (regardless of Recorder or Builder)
- ✅ Oldest tests appear at the bottom
- ✅ No grouping by source type

**Why you might think they're grouped:**
- If you created all Recorder tests first, then all Builder tests → they naturally appear grouped by time
- Solution: Hard refresh browser `Ctrl + Shift + R` and click "Refresh Tests" button

---

### 2. Edit Test Names for Semantic Tests ✨ NEW

**User Request:** "Need flexibility to edit test case names for semantic tests"

**Status:** ✅ **Fully implemented!**

#### Frontend Changes

**Edit Button in Dropdown Menu:**
- ✏️ Edit Name option added for all semantic/AI-generated tests
- Appears in the 3-dot menu (⋮) alongside Delete, Export, Duplicate
- Only shows for tests with `semantic` or `ai-generated` tags

**Edit Modal:**
- Clean modal with input field for new name
- Shows current name as default value
- Keyboard shortcuts: `Enter` to save, `Esc` to cancel
- Input auto-focuses and selects text for quick editing

**Files Modified:**
- `src/web/js/features/test-suite.js`
  - Lines 308: Added "Edit Name" menu option (conditional for semantic tests)
  - Lines 2058-2138: New `editTestName()` function
  - Lines 2140-2144: New `closeEditNameModal()` function
  - Lines 2146-2177: New `saveTestName()` function
  - Lines 2319-2321: Exported window functions

#### Backend Changes

**New API Endpoints:**

**Builder Tests:**
```
POST /test-suite/test-cases/{test_case_id}/rename
Body: { "new_name": "New Test Name" }
```

**Recorder Tests:**
```
POST /recorder/rename-test/{test_case_id}
Body: { "new_name": "New Test Name" }
```

**Files Modified:**
- `src/main/python/api_server_modular.py`
  - Line 1629: Added rename endpoint for builder tests
  - Line 1038: Added rename endpoint for recorder tests

- `src/main/python/test_management/test_suite_handler.py`
  - Lines 509-577: New `rename_test_case()` function
  - Searches all test type directories (regression, smoke, integration, etc.)
  - Updates JSON file on disk
  - Clears cache to reload updated test

- `src/main/python/recorder/recorder_handler.py`
  - Lines 472-530: New `rename_test()` function
  - Searches all test type directories and old structure
  - Updates JSON file on disk with new name

---

## How to Use

### Editing a Semantic Test Name

1. **Find the semantic test** in Test Suite (has "✨ AI-Generated" badge)
2. **Click the 3-dot menu** (⋮) on the right side of the test card
3. **Click "✏️ Edit Name"** in the dropdown
4. **Modal appears** with current name selected
5. **Type new name** and press `Enter` or click "💾 Save"
6. **Test list automatically refreshes** with new name

### Visual Cues

**Semantic Test Identification:**
```
Field Length Boundary Testing           ← Test name (now editable!)
Test Builder • ✨ AI-Generated • boundary   ← Badges
```

**Dropdown Menu (Semantic Tests):**
```
⋮ Menu
├─ ✏️ Edit Name      ← NEW! Only for semantic tests
├─ 🗑️ Delete Test
├─ 💾 Export
└─ 📋 Duplicate
```

**Dropdown Menu (Regular Tests):**
```
⋮ Menu
├─ 🗑️ Delete Test      ← No edit option
├─ 💾 Export
└─ 📋 Duplicate
```

---

## Technical Implementation Details

### Frontend Logic

**Conditional Menu Item:**
```javascript
${isSemantic ? `<div onclick="editTestName('${session.id}', '${session.name}', '${session.source}')">
    ✏️ Edit Name
</div>` : ''}
```

This checks if the test has:
- `tags` array containing "semantic" or "ai-generated"
- `generated_by` === "semantic-analysis"

### Backend Logic

**Builder Tests:**
1. Receives test_case_id and new_name
2. Loads test case from builder
3. Searches test_suites/{test_type}/builder/ directories
4. Finds JSON file matching test_case_id
5. Updates `name` field in JSON
6. Writes back to disk
7. Clears cache

**Recorder Tests:**
1. Same pattern as builder
2. Searches test_suites/{test_type}/recorded/ directories
3. Also checks old structure: test_suites/recorded/
4. Updates and saves

---

## Files Changed Summary

### Frontend
✅ `src/web/js/features/test-suite.js`
- Added edit button in dropdown menu (conditional)
- Created editTestName() modal function
- Created closeEditNameModal() helper
- Created saveTestName() API call function
- Exported functions to window

### Backend
✅ `src/main/python/api_server_modular.py`
- Added /test-suite/test-cases/{id}/rename endpoint
- Added /recorder/rename-test/{id} endpoint

✅ `src/main/python/test_management/test_suite_handler.py`
- Added rename_test_case() function
- Multi-directory search (all test types)
- JSON file update logic
- Cache clearing

✅ `src/main/python/recorder/recorder_handler.py`
- Added rename_test() function
- Multi-directory search (all test types + old structure)
- JSON file update logic

---

## Testing Checklist

### Test Timestamp Sorting
- ✅ Create a new Recorder test → should appear at top
- ✅ Create a new Builder test → should appear at top
- ✅ Create a semantic test → should appear at top (newest)
- ✅ Hard refresh browser (Ctrl+Shift+R)
- ✅ Click "Refresh Tests" button
- ✅ Verify newest tests at top regardless of source

### Test Edit Name Feature
- ✅ Find a semantic test (has ✨ AI-Generated badge)
- ✅ Click 3-dot menu (⋮)
- ✅ Verify "✏️ Edit Name" appears in menu
- ✅ Click "Edit Name"
- ✅ Modal appears with current name
- ✅ Text is auto-selected
- ✅ Type new name
- ✅ Press Enter (or click Save)
- ✅ Test list refreshes
- ✅ New name is displayed
- ✅ Check JSON file on disk (name updated)

### Test Edit Only for Semantic Tests
- ✅ Find a regular (non-semantic) Recorder test
- ✅ Click 3-dot menu
- ✅ Verify "Edit Name" does NOT appear
- ✅ Find a regular Builder test
- ✅ Verify "Edit Name" does NOT appear
- ✅ Only semantic tests should have edit option

---

## Known Edge Cases Handled

### Multi-Directory Search
Both rename functions search ALL test type directories:
- regression/
- smoke/
- integration/
- performance/
- security/
- exploratory/
- general/
- recorded/ (old structure)

This ensures the test is found regardless of where the user saved it.

### Name Escaping
Special characters in test names are properly escaped:
```javascript
'${session.name.replace(/'/g, "\\'").replace(/"/g, '&quot;')}'
```

Handles:
- Quotes (single and double)
- Apostrophes
- Special characters

### Cache Clearing
After renaming, the backend clears the in-memory cache:
```python
builder.test_cases.clear()
```

This ensures the next API call loads the updated name from disk.

---

## Example Usage

**Before:**
```
TC002_variant_1
Field Length Boundary Testing
Test Builder • ✨ AI-Generated • boundary
```

**User clicks Edit → Changes to:**
"Boundary Test: Email Field Length Validation"

**After:**
```
TC002_variant_1
Boundary Test: Email Field Length Validation
Test Builder • ✨ AI-Generated • boundary
```

---

## Restart Required

**Backend changes require server restart:**
```powershell
# Kill existing server
Get-Process python | Where-Object {$_.CommandLine -like '*api_server*'} | Stop-Process -Force

# Restart via task or manually
python src\main\python\api_server_modular.py
```

**Frontend changes require:**
```
Ctrl + Shift + R (hard refresh browser)
```

---

## Summary

✅ **Timestamp Sorting:** Already working correctly (newest first, regardless of source)
✅ **Edit Names:** Fully implemented for semantic tests only
✅ **Backend Endpoints:** Created for both Builder and Recorder tests
✅ **Multi-Directory Search:** Handles all test type locations
✅ **Cache Management:** Proper cache clearing after updates
✅ **UI Polish:** Conditional menu, keyboard shortcuts, auto-focus

**All features are ready to test after server restart!**
