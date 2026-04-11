# 🐛 Feedback System Troubleshooting Guide

## Issue: Feedback Features Not Showing

You mentioned: "I don't find the Click 👍 on suggestion, bug report modal, etc."

---

## ✅ Backend Fixed
I fixed the test execution error:
- **Error**: `'str' object has no attribute 'get'` at line 577
- **Cause**: Semantic tests have string steps, not dictionary steps
- **Fix**: Added proper handling for semantic tests to execute generated code

---

## 🔍 Frontend Diagnosis Steps

### Step 1: Run Diagnostic Page
1. Navigate to: `http://localhost:5002/diagnostic-feedback.html`
2. Click **"▶️ Run Diagnostic"**
3. Check the results:
   - ✅ `window.feedbackManager` should be defined
   - ✅ `window.fieldAwareSuggestions` should be defined
   - ✅ Script tags should show `v=20260407030`

### Step 2: Hard Refresh Browser
**Important**: Browser cache might be serving old files.

**Windows/Linux**: `Ctrl + Shift + F5`  
**Mac**: `Cmd + Shift + R`

**Or use DevTools**:
1. Press `F12` to open Developer Tools
2. Right-click the Refresh button
3. Select **"Empty Cache and Hard Reload"**

### Step 3: Check Browser Console
1. Press `F12` to open Developer Tools
2. Go to **Console** tab
3. Look for errors containing:
   - `feedback-system`
   - `semantic-suggestions`
   - `test-suite`
   - `SyntaxError`
   - `Uncaught`

**Common errors**:
- **`feedbackManager is not defined`** → Script didn't load
- **`Unexpected token`** → JavaScript syntax error
- **`Failed to fetch`** → File URL wrong or server not serving

### Step 4: Check Network Tab
1. In DevTools, go to **Network** tab
2. Hard refresh (`Ctrl + Shift + F5`)
3. Filter for: `feedback-system.js`
4. Check:
   - ✅ Status should be `200 OK`
   - ❌ `404 Not Found` → File path wrong
   - ❌ `304 Not Modified` → Still cached (clear cache)

### Step 5: Verify Files Exist
Check these files exist on disk:
```
c:\Users\valaboph\AIAutomation\src\web\js\modules\feedback-system.js
c:\Users\valaboph\AIAutomation\src\web\js\modules\semantic-suggestions.js
c:\Users\valaboph\AIAutomation\src\web\js\features\test-suite.js
c:\Users\valaboph\AIAutomation\src\web\pages\test-suite.html
```

### Step 6: Check Page Cache
The Test Suite page (`test-suite.html`) is cached by `navigation.js`. To force reload:

**Option 1**: Clear page cache
```javascript
// In browser console:
delete window.pageCache;
location.reload(true);
```

**Option 2**: Restart server
- Stop the Python server
- Start it again
- This clears server-side caching

---

## 🧪 Manual Testing

### Test 1: Check FeedbackManager in Console
1. Open Browser Console (`F12`)
2. Type: `window.feedbackManager`
3. Press Enter

**Expected**: Should show `FeedbackManager` object with methods  
**If undefined**: Script didn't load → Hard refresh

### Test 2: Check Feedback Stats Button
1. Navigate to **Test Suite** tab
2. Look in the header for: **"📊 Feedback Stats"** button
3. It should be purple, next to "Clear All" button

**If not there**:
- Page cache issue → Clear browser cache
- HTML not updated → Hard refresh

### Test 3: Test Suggestion Rating
1. Find a semantic test (has ✨ AI-Generated badge)
2. Click **▶️ Execute**
3. Data override modal opens
4. Click on a field's suggestion area

**Expected**: Should see field-aware suggestions with 👍/👎 buttons  
**If not**: 
- Check console for errors
- Verify `window.fieldAwareSuggestions` exists

### Test 4: Test Bug Report Modal
1. Execute a semantic test with suggestions
2. After test completes, wait 1.5 seconds

**Expected**: Bug report modal should appear  
**If not**:
- Check console for: `[Test Suite] 🎯 Semantic test completed`
- Verify `dataOverrides` were used (check console logs)
- Manually trigger: `feedbackManager.showBugReportModal('TC001', ['scenario1'])`

---

## 🔧 Quick Fixes

### Fix 1: Force Module Reload
In browser console:
```javascript
// Clear cache version marker
localStorage.removeItem('test_suite_version');

// Force reload all modules
delete window.feedbackManager;
delete window.fieldAwareSuggestions;

// Hard reload page
location.reload(true);
```

### Fix 2: Clear All Caches
```javascript
// Clear localStorage
localStorage.clear();

// Clear sessionStorage
sessionStorage.clear();

// Clear page cache
if (window.pageCache) delete window.pageCache;

// Reload
location.reload(true);
```

### Fix 3: Check Script Load Order  
Verify scripts load in this order in `index-new.html`:
1. `semantic-suggestions.js` (loads first)
2. `feedback-system.js` (loads second)
3. `test-suite.js` (loads third)

---

## 📊 Expected Cache Versions

All scripts should have version: **v=20260407030**

Check in HTML:
```html
<script src="/web/js/modules/semantic-suggestions.js?v=20260407030"></script>
<script src="/web/js/modules/feedback-system.js?v=20260407030"></script>
<script src="/web/js/features/test-suite.js?v=20260407030"></script>
```

---

## 🆘 If Still Not Working

### Share These Details:
1. **Browser Console Screenshot** (F12 → Console tab)
2. **Network Tab Screenshot** (F12 → Network tab, filter: `feedback`)
3. **Test These Commands** in console:
   ```javascript
   console.log('feedbackManager:', typeof window.feedbackManager);
   console.log('fieldAwareSuggestions:', typeof window.fieldAwareSuggestions);
   console.log('loadTestCases:', typeof window.loadTestCases);
   ```
4. **Check Diagnostic Page Results**: `http://localhost:5002/diagnostic-feedback.html`

---

## ✅ Success Checklist

After fixing, you should see:

- [ ] **Console**: No JavaScript errors
- [ ] **Test Suite Header**: "📊 Feedback Stats" button visible (purple)
- [ ] **Semantic Test Modal**: Shows field suggestions with 👍/👎 buttons
- [ ] **After Test Execution**: Bug report modal appears automatically
- [ ] **Click 👍**: Border turns green, toast notification appears
- [ ] **Click Stats Button**: Dashboard modal opens with statistics

---

## 💡 Most Likely Issue

**90% of the time, it's browser cache.**

**Solution**:
1. Press `Ctrl + Shift + F5` (hard refresh)
2. If that doesn't work: Clear browser cache completely
3. If still stuck: Restart browser entirely
4. Last resort: Restart Python server

---

*Updated: 2026-04-08*  
*Backend fixes applied to: test_suite_runner.py*  
*Frontend modules: feedback-system.js, semantic-suggestions.js, test-suite.js*
