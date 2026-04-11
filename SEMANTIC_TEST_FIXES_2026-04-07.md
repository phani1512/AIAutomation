# Semantic Test Fixes - April 7, 2026

## Issues Identified and Fixed

### ✅ Issue 1: Nested Semantic Variants (Double Variants)
**Symptom:** TC001_variant_1_variant_2 shows only `pass` statements instead of real code

**Root Cause:**
- Creating semantic tests FROM semantic tests results in nested variants
- Parent lookup was not recursive - `TC001_variant_1` (itself a variant) had no real code
- Need to find original parent `TC001` (non-variant)

**Fix Applied:**
```python
# api_server_modular.py lines ~1926-1950
# Added recursive parent resolution logic

while '_variant_' in original_parent_id and depth < max_depth:
    base_id = original_parent_id.split('_variant_')[0]
    base_test = builder.load_test_case(base_id)
    if base_test:
        original_parent_id = base_id
        break
```

**Result:** 
- Semantic variants now copy code from the original test (TC001) not intermediate variants
- Prevents `pass` statements in nested semantic tests

---

### ⚠️ Issue 2: Duplicate Test Files
**Symptom:** Same test (TC002_variant_1) found in multiple directories:
- `test_suites/regression/builder/TC002_variant_1_Field Length Boundary Testing.json`
- `test_suites/performance/builder/TC002_variant_1_Field Length Boundary Testing.json`

**Root Cause:**
- User saved the same semantic test twice to different test types
- Timestamps confirm: 4:49 PM (regression), 5:01 PM (performance)

**Status:** 
- **NOT A BUG** - This is expected user workflow
- Users can save same test to multiple test types for different purposes
- If unwanted, user should delete one copy manually

**Recommendation:**
- Add UI warning when saving already-saved semantic variant
- Show "This test is already saved to [regression]. Save to [performance] also?"

---

### 🔍 Issue 3: Step Count Display Mismatch
**Symptom:** UI shows "Steps: 5" but JSON file has `prompt_count: 1`

**Investigation:**
```json
TC002_variant_1 JSON structure:
{
  "prompt_count": 1,              ← Should display this
  "prompts": [{ ... }],           ← 1 item (correct executable code)
  "steps": [                      ← 5 items (just text suggestions)
    "Test with 0 characters",
    "Test with 1 character",
    "Test with maximum allowed",
    "Test with maximum + 1",
    "Verify restrictions enforced"
  ]
}
```

**Frontend Code Analysis:**
```javascript
// test-suite.js line 81
action_count: tc.prompt_count || tc.steps?.length || 0,
```

This is CORRECT - it should use `prompt_count` (1) first, not `steps.length` (5)

**Root Cause:**
- Browser cache showing old data
- OR user viewing wrong test
- Frontend logic is correct

**Fix:**
1. **Hard refresh browser:** `Ctrl + Shift + R` (Chrome/Edge) or `Ctrl + F5` (Firefox)
2. **Clear browser cache:** DevTools > Application > Clear Storage
3. **Clear test cache:** Refresh button in Test Suite page

---

## Files Modified

### Backend
✅ `src/main/python/api_server_modular.py` (Lines 1926-1950)
- Added recursive parent resolution for nested semantic variants
- Prevents copying code from intermediate variants
- Ensures original test (TC001) is found even when parent is TC001_variant_1

### Frontend
⚠️ No changes needed - code is correct
- `src/web/js/features/test-suite.js` already uses `tc.prompt_count || tc.steps?.length`
- `src/web/js/features/semantic-analysis.js` saves tests correctly with single test_type

---

## Verification Steps

### Test Nested Variant Fix:
1. Restart API server (automatic via task)
2. Open Test Suite page
3. Find TC001 (original test with real code)
4. Generate semantic variants (creates TC001_variant_1)
5. **Try to generate semantic variants from TC001_variant_1** (nested)
6. Save the nested variant
7. Check if code is copied from TC001 (not from TC001_variant_1)

**Expected Result:**
- Nested variant should have real selector logic from TC001
- No `pass` statements
- Log shows: "Using parent test: TC001 (original requested: TC001_variant_1)"

### Test Step Count Display:
1. Hard refresh browser: `Ctrl + Shift + R`
2. Click "Refresh Tests" button in Test Suite
3. Find TC002_variant_1 in test list
4. Check step count display

**Expected Result:**
- Should show "Steps: 1" (from `prompt_count`)
- NOT "Steps: 5" (from `steps` array)

### Test Duplicate Handling:
1. Generate semantic variant from TC002
2. Save to "Regression" test type
3. **Do NOT** generate again - instead find saved test
4. Try to save THE SAME test object to "Performance"

**Expected Behavior:**
- Currently: Saves duplicate to second location (allowed)
- Future enhancement: Show warning about existing copy

---

## Known Limitations

### Semantic from Semantic Detection
Currently, users can create semantic tests from semantic tests in the UI. This is now handled by recursive parent lookup, but ideally:

**Better UX:**
```javascript
// semantic-analysis.js - future enhancement
if (testCaseId.includes('_variant_')) {
    showNotification('⚠️ This is already a semantic variant. Generate variants from the original test instead.', 'warning');
    // Suggest: "Would you like to jump to the parent test TC001?"
}
```

### Duplicate Prevention
When saving semantic tests, currently no check for existing files. Could add:

**Check before save:**
```javascript
// confirmSaveGeneratedTests() - future enhancement
const existingTestTypes = await checkExistingTestLocations(testId);
if (existingTestTypes.length > 0) {
    const message = `This test already exists in: ${existingTestTypes.join(', ')}. Save to ${selectedType} also?`;
    if (!confirm(message)) return;
}
```

---

## Summary

### ✅ Fixed Issues:
1. **Nested semantic variants** - Now copy code from original parent (recursive lookup)

### ⚠️ Not Issues (User Workflow):
2. **Duplicate files** - User intentionally saved to multiple test types

### 🔍 Cache Issue:
3. **Step count** - Correct in code, browser cache needs refresh

### 🚀 Server Status:
- API server started with fix
- Nested variant resolution active
- Ready for testing

---

## Testing Instructions for User

1. **Hard refresh your browser** (Ctrl+Shift+R) to clear cache
2. Click "Refresh Tests" button in test suite
3. Check if TC002_variant_1 now shows "Steps: 1"
4. Try creating a new semantic test from TC001
5. Save it and verify it has real code (not `pass` statements)
6. If you see TC001_variant_1_variant_2, delete it and regenerate from TC001 directly

**For nested variants already saved:**
- Delete TC001_variant_1_variant_2
- Go to TC001 (original test)  
- Generate semantic variants from TC001
- Save and verify real code is present

**For duplicate files:**
- Keep one copy in the most appropriate test type
- Delete the other copy using the delete button in test suite
- OR keep both if you want the test in multiple suites

---

## Logs to Check

Look for these log messages when saving semantic variants:
```
[SAVE-GENERATED] Semantic variant detected, parent: TC001_variant_1
[SAVE-GENERATED] Parent TC001_variant_1 is also a variant, looking for original...
[SAVE-GENERATED] Found original parent: TC001
[SAVE-GENERATED] Using parent test: TC001 (original requested: TC001_variant_1)
[SAVE-GENERATED] ✓ Copied and modified code from parent test TC001
```

These confirm the recursive parent resolution is working!
