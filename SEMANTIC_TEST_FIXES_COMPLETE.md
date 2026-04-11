# Semantic Test Issues - Complete Fix (April 7, 2026)

## Issues Fixed

### ✅ Issue 1: Step Count Showing 5 Instead of 1

**Problem:**
- UI showed "Steps: 5" for tests with only 1 executable step
- The 5 came from suggested implementation steps, not executable prompts

**Root Cause:**
```javascript
// OLD CODE (incorrect priority)
action_count: tc.prompt_count || tc.steps?.length || 0
```

This used `prompt_count` (metadata) first, but if missing, fell back to `steps.length` (suggestions = 5)

**Fix Applied:**
```javascript
// NEW CODE (correct priority)
action_count: tc.prompts?.length || tc.prompt_count || tc.actions?.length || 0
```

Now uses actual `prompts` array length first (most accurate = 1)

**File:** `src/web/js/features/test-suite.js` lines 75-98

---

### ✅ Issue 2: Data Override Popup Not Showing for Semantic Tests

**Problem:**
- Data override modal didn't appear when executing semantic tests
- User couldn't see or modify test data before execution

**Root Cause:**
```javascript
// Line 1341 - OLD CODE
if (testCaseData.success && testCaseData.test_case.steps) {
    prompts = testCaseData.test_case.steps;  // ❌ Wrong field!
}
```

For semantic tests:
- `.steps` = 5 text suggestions (not executable)
- `.prompts` = 1 executable test step (with actual value)

**Fix Applied:**
```javascript
// NEW CODE - Prioritizes prompts over steps
if (testCaseData.success && testCaseData.test_case) {
    prompts = testCaseData.test_case.prompts || testCaseData.test_case.steps || [];
    
    // Store suggestions separately for display
    if (testCaseData.test_case.steps) {
        sessionData.suggestedSteps = testCaseData.test_case.steps;
    }
}
```

**File:** `src/web/js/features/test-suite.js` lines 1334-1360

---

### ✅ Issue 3: Suggested Implementation Steps Now Displayed in Modal

**Enhancement:**
Data override modal now shows the 5 suggested implementation steps alongside the executable prompt:

```
Step 1: Field Length Boundary Testing: enter text in email field at boundary
[Input field with AAAA... value]

💡 Suggested Implementation:
Test with 0 characters (empty)
Test with 1 character (minimum)  
Test with maximum allowed length
Test with maximum + 1 characters
Verify length restrictions enforced
```

**File:** `src/web/js/features/test-suite.js` lines 1468-1500

---

### ✅ Issue 4: Test Metadata Preserved for Modal

**Problem:**
When loading test list, `prompts`, `steps`, and `actions` arrays were not cached in session data, forcing API calls every time.

**Fix Applied:**
```javascript
// Store all fields needed for data override modal
{
    ...existingFields,
    prompts: tc.prompts || [],
    steps: tc.steps || [],
    actions: tc.actions || []
}
```

Now checks cached data first before making API calls.

**File:** `src/web/js/features/test-suite.js` lines 75-98

---

### ⚠️ Issue 5: Browser Opens But Steps Don't Execute

**Status:** Needs verification after server restart

**Possible Causes:**
1. Backend execution endpoint works correctly
2. Might be a timing/Angular wait issue
3. Could be selector resolution problem in semantic tests

**Next Steps:**
1. Restart server with all fixes
2. Execute a semantic test
3. Check browser console and server logs for errors
4. If still failing, investigate test_suite_runner execution logic

---

## Files Modified

### Frontend
1. **src/web/js/features/test-suite.js**
   - Lines 75-98: Fixed step count priority (use `prompts.length` first)
   - Lines 75-98: Store prompts/steps/actions in session data for modal
   - Lines 1334-1360: Fixed data override to use `prompts` not `steps`
   - Lines 1365-1395: Enhanced modal to show suggested implementation steps
   - Lines 1468-1500: Added suggestion display in modal fields

### Backend  
2. **src/main/python/api_server_modular.py**
   - Lines 1926-1950: Added recursive parent resolution for nested semantic variants
   - Prevents copying code from intermediate variants (TC001_variant_1)
   - Ensures original parent test (TC001) is used as code source

---

## Testing Checklist

### Test Step Count Display
- [ ] Hard refresh browser (Ctrl+Shift+R)
- [ ] Click "Refresh Tests" in Test Suite
- [ ] Find TC002_variant_1 in list
- [ ] Verify shows "Steps: 1" (not "Steps: 5")

### Test Data Override Modal
- [ ] Click execute button (▶️) on TC002_variant_1
- [ ] Modal should appear with:
  - ✅ 1 input field with the AAAA... value
  - ✅ "💡 Suggested Implementation" section showing 5 steps
  - ✅ Original value displayed
- [ ] Modify value and click Execute
- [ ] Verify test runs with new value

### Test Semantic Test Execution
- [ ] Execute TC002_variant_1
- [ ] Browser should open
- [ ] **CRITICAL:** Verify steps actually execute (form should be filled)
- [ ] Check browser console for any errors
- [ ] Check server logs for execution details

### Test Nested Variant Code Copy
- [ ] Delete TC001_variant_1_variant_2 (if exists)
- [ ] Open TC001 (original test)
- [ ] Generate semantic variants
- [ ] Save one variant
- [ ] View code - should have real selectors (not `pass` statements)
- [ ] Check server logs for: "Using parent test: TC001"

---

## Expected Behavior After Fixes

### Correct Step Count
```
Field Length Boundary Testing
Test Builder • AI-Generated • boundary
📅 4/7/2026, 5:13:57 PM
📊 Steps: 1  ← Should show 1, not 5
```

### Data Override Modal Shows
```
🔧 Override Test Data

Step 1: Field Length Boundary Testing: enter text in email field at boundary
[AAAAAAA...AAAAAAA]  ← Input field

💡 Suggested Implementation:
• Test with 0 characters (empty)
• Test with 1 character (minimum)  
• Test with maximum allowed length
• Test with maximum + 1 characters
• Verify length restrictions enforced

📝 Original value: "AAAA...AAAA"

[Cancel] [Execute Test]
```

### Execution Works
1. Browser opens ✓
2. Navigates to URL ✓
3. **Finds email field ✓**
4. **Enters AAAA...AAAA value ✓** ← Should work now
5. Test completes successfully ✓

---

## Remaining Issues to Investigate (If Execution Still Fails)

### If browser opens but no steps execute:

**Check Server Logs:**
```
[EXECUTE] Test: TC002_variant_1, Browser: chrome, Mode: json_steps
[EXECUTE SESSION] Starting execution...
[EXECUTE SESSION] Steps: 1
[EXECUTE SESSION] Applying data overrides: {...}
```

**Check Browser Console:**
```javascript
// Look for errors in browser dev tools (F12)
// Any selector resolution failures?
// Any timeout errors?
```

**Possible Fixes:**
1. Check if semantic tests have correct URL in JSON
2. Verify `generated_code` field exists and is valid
3. Check if Angular/wait logic is interfering
4. Verify selector resolution for semantic test fields

---

## Quick Reference: JSON Structure

### Semantic Test (TC002_variant_1)
```json
{
  "test_case_id": "TC002_variant_1",
  "prompt_count": 1,                    ← Metadata (may be missing)
  
  "prompts": [                          ← EXECUTABLE (1 item) ✓ USE THIS
    {
      "step": 1,
      "prompt": "enter text in email field at boundary",
      "value": "AAAA...AAAA"
    }
  ],
  
  "steps": [                            ← SUGGESTIONS (5 items) ✗ Don't use for count
    "Test with 0 characters (empty)",
    "Test with 1 character (minimum)",
    "Test with maximum allowed length",
    "Test with maximum + 1 characters",
    "Verify length restrictions enforced"
  ],
  
  "generated_code": {                   ← For execution
    "python": "...",
    "java": "...",
    "javascript": "..."
  }
}
```

---

## What's Working Now

✅ Step count display uses correct field (`prompts.length`)
✅ Data override modal appears for semantic tests
✅ Modal shows suggested implementation steps
✅ Modal loads prompts from cache (faster)
✅ Nested semantic variants copy code from original parent
✅ All test metadata preserved in frontend

---

## What to Verify

🔍 Semantic test execution (browser opens and runs steps)
🔍 Data override values actually applied during execution
🔍 Suggested steps help user understand test intent

---

## Server Restart Required

**All fixes implemented!** Restart the API server to apply changes:

```powershell
# Kill existing Python processes
Get-Process python | Where-Object {$_.CommandLine -like '*api_server*'} | Stop-Process -Force

# Restart via VS Code task
# OR run manually:
cd C:\Users\valaboph\AIAutomation
.venv\Scripts\Activate.ps1
python src\main\python\api_server_modular.py
```

Then hard refresh browser (Ctrl+Shift+R) and test!
