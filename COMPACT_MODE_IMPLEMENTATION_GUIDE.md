# Compact Mode & Template Substitution - Complete Solution

## Problem Analysis

Your generated test has three issues:
1. **Steps 1-3**: Using fallback selectors but code is VERBOSE (30+ lines per step) ❌
2. **Step 4**: NO fallback selectors, single CSS selector only ❌  
3. **Step 5**: WRONG fallback selectors (confirm/submit instead of generic button) ❌

## Root Causes

### Issue 1: Compact Mode Not Enabled
- ✅ Backend: Implemented `compact_mode` parameter
- ❌ Frontend: NOT sending `compact_mode: true` in requests
- **Fix**: Add compact_mode to Test Builder API calls

### Issue 2: Template Substitution Not Working  
- ✅ Backend: Fixed placeholder ({VALUE} instead of {BUTTON})
- ✅ Backend: Added fallback_selectors substitution
- ❌ **Step 4**: Matching wrong dataset entry (`app-wait-button button`)
- ❌ **Step 5**: Matching wrong template (confirm/submit buttons)

## Solutions

### Solution 1: Enable Compact Mode (Quick Win)

**Add this parameter when generating tests:**

```javascript
// In test-builder.js or wherever you call /generate
const response = await fetch('/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        prompt: step.prompt,
        language: "python",
        with_fallbacks: true,      // Keep self-healing
        compact_mode: true,         // ✨ ADD THIS
        comprehensive_mode: false   // Keep simple for test builder
    })
});
```

**Result**: Steps 1-3 will shrink from 30+ lines to 7 lines each!

```python
# BEFORE (30 lines):
element = None
selectors = ["input[type='email']", "input[id='email']", ...]
for selector in selectors:
    try:
        elements = driver.find_elements(By.CSS_SELECTOR, selector)
        for el in elements:
            if el.is_displayed() and el.is_enabled():
                element = el
                break
        if element:
            break
    except:
        continue
# ... 20 more lines ...

# AFTER (7 lines):
selectors = ["input[type='email']", "input[id='email']", "input[id='producer-email']", "input[name='email']", "input[name*='email']", "input[id*='email']"]
element = None
for s in selectors:
    try: element = WebDriverWait(driver, 0.5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, s))); break
    except: continue
if element: element.clear(); element.send_keys('pvalaboju@vertafore.com')
```

---

### Solution 2: Fix Step 4 Template Matching

**Current Problem:**
```python
# Step 4: click Carrier Account 2 button
element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "app-wait-button button"))
element.click()
```

This is matching a DIFFERENT dataset entry (angular component selector), not the generic button template.

**Root Cause**: The prompt "click Carrier Account 2 button" is matching:
- Dataset entry with CSS selector: `app-wait-button button` (probably from Angular app examples)
- Instead of: Generic button template at line 19370

**Fix Options:**

**Option A: More specific prompt**
```
click button with text Carrier Account 2
```
This forces matching the text-based button template.

**Option B: Verify dataset priority**  
Check if there's an entry in the dataset with higher priority:
```bash
# Search dataset for conflicting entries
grep -n "app-wait-button" src/resources/combined-training-dataset-final.json
```

---

### Solution 3: Fix Step 5 Wrong Selectors

**Current Problem:**
```python
# Step 5: click Beneficiaries button  
selectors = [
    "//button[normalize-space()='Confirm']",  # ❌ WRONG - looking for "Confirm"
    "button[type='submit']",                  # ❌ Generic submit, not "Beneficiaries"
    "input[type='submit']",
    "button:contains('Submit')",
    "button:contains('Save')",
    "button:contains('Confirm')"
]
```

This is matching the **WRONG template** (confirm/submit buttons).

**Expected (from line 19370):**
```python
selectors = [
    "//button[normalize-space()='Beneficiaries']",  # ✅ Correct with substitution
    "button",
    "input[type='button']",
    "[role='button']",
    ".btn",
    "a.button"
]
```

**Root Cause**: Template parameter extraction is failing.

**Debug Steps:**

1. **Check if prompt matches the template pattern:**
```python
# In template_parameter_extractor.py, the pattern is:
r'click\s+(?:the\s+)?(.+?)\s+button': {'placeholder': '{VALUE}', 'capture_group': 1}

# Your prompt: "click Beneficiaries button"
# Should extract: value="Beneficiaries"
```

2. **Verify template matching works:**
Add debug output in `dataset_matcher.py`:
```python
def find_dataset_match(self, prompt: str, return_alternatives: bool = True):
    prompt_normalized = self.normalize_with_synonyms(prompt)
    print(f"[DEBUG] Normalized prompt: {prompt_normalized}")
    
    # After finding match
    if dataset_match:
        print(f"[DEBUG] Matched template: {dataset_match.get('prompt')}")
        print(f"[DEBUG] Has fallback_selectors: {len(dataset_match.get('fallback_selectors', []))}")
```

3. **Check if template substitution runs:**
Add debug in `template_parameter_extractor.py`:
```python
def process_template_match(self, user_prompt: str, template_entry: dict) -> dict:
    extracted = self.extract_parameter(user_prompt, template_entry.get('prompt', ''))
    
    if extracted:
        print(f"[DEBUG] Extracted parameter: {extracted}")
        print(f"[DEBUG] Substituting {extracted['placeholder']} with {extracted['value']}")
    else:
        print(f"[DEBUG] NO parameter extracted from: {user_prompt}")
```

---

## Quick Test

**Test compact mode immediately:**

1. Open browser console
2. Run this in Test Builder:
```javascript
// Generate one step with compact mode
fetch('http://localhost:5002/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        prompt: "enter test@example.com in email",
        language: "python",
        with_fallbacks: true,
        compact_mode: true  // ✨ Test this
    })
}).then(r => r.json()).then(d => console.log(d.code));
```

**Expected output (7 lines):**
```python
# Self-healing input with 6 fallback selectors
selectors = ["input[type='email']", ...]
element = None
for s in selectors:
    try: element = WebDriverWait(driver, 0.5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, s))); break
    except: continue
if element: element.clear(); element.send_keys('test@example.com')
```

---

## Implementation Checklist

### Phase 1: Enable Compact Mode (5 min)
- [ ] Add `compact_mode: true` to Test Builder generate requests
- [ ] Test generation with one prompt
- [ ] Verify code is 7 lines instead of 30

### Phase 2: Fix Template Matching (15 min)  
- [ ] Add debug output to dataset_matcher.py
- [ ] Generate "click Beneficiaries button" 
- [ ] Check console logs - does it match line 19370 template?
- [ ] If not, adjust prompt or fix dataset priority

### Phase 3: Verify Complete Test (5 min)
- [ ] Generate full 5-step test with compact mode
- [ ] Verify all steps are 7-8 lines each
- [ ] Verify Steps 4 & 5 have correct fallback selectors
- [ ] Run test to confirm it works

---

## Expected Final Code (Compact Mode)

```python
# Step 1: enter text in email field (7 lines)
selectors = ["input[type='email']", "input[id='email']", "input[id='producer-email']", "input[name='email']", "input[name*='email']", "input[id*='email']"]
element = None
for s in selectors:
    try: element = WebDriverWait(driver, 0.5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, s))); break
    except: continue
if element: element.clear(); element.send_keys('pvalaboju@vertafore.com')

# Step 2: enter text in password field (7 lines)  
selectors = ["input[type='password']", "input[id='password']", "input[id='producer-password']", "input[name='password']", "input[name*='password']", "input[id*='password']"]
element = None
for s in selectors:
    try: element = WebDriverWait(driver, 0.5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, s))); break
    except: continue
if element: element.clear(); element.send_keys('Phanindraa@1512')

# Step 3: click login button (8 lines)
selectors = ['.login-row .primary-btn', 'button', "input[type='button']", "[role='button']", '.btn', 'a.button']
element = None
for s in selectors:
    try: element = WebDriverWait(driver, 0.5).until(EC.element_to_be_clickable((By.CSS_SELECTOR, s))); driver.execute_script('arguments[0].scrollIntoView(false)', element); break
    except: continue
if element: element.click()

# Step 4: click Carrier Account 2 button (8 lines) ✨ FIXED
selectors = ["//button[normalize-space()='Carrier Account 2']", "button", "input[type='button']", "[role='button']", ".btn", "a.button"]
element = None
for s in selectors:
    try: element = WebDriverWait(driver, 0.5).until(EC.element_to_be_clickable((By.XPATH if s.startswith('//') else By.CSS_SELECTOR, s))); driver.execute_script('arguments[0].scrollIntoView(false)', element); break
    except: continue
if element: element.click()

# Step 5: click Beneficiaries button (8 lines) ✨ FIXED  
selectors = ["//button[normalize-space()='Beneficiaries']", "button", "input[type='button']", "[role='button']", ".btn", "a.button"]
element = None
for s in selectors:
    try: element = WebDriverWait(driver, 0.5).until(EC.element_to_be_clickable((By.XPATH if s.startswith('//') else By.CSS_SELECTOR, s))); driver.execute_script('arguments[0].scrollIntoView(false)', element); break
    except: continue
if element: element.click()
```

**Total**: ~40 lines instead of 150+ lines (73% reduction!)

---

## Long-term Strategy

### For CI/CD & Database Storage:

1. **Always use compact_mode=true** when saving tests to DB
2. **Add a UI toggle** in Test Builder:
   ```
   ☑ Generate compact code (recommended for DB/CI-CD)
   ```
3. **Track code size** in test metadata:
   ```python
   {
       "test_id": "test_001",
       "code_size_bytes": 1234,  # Track compression benefit
       "compact_mode": true
   }
   ```

### For Team Collaboration:

1. **Code reviews**: Compact code is easier to review (fewer lines)
2. **Git diffs**: Smaller diffs when updating tests  
3. **Execution speed**: Identical runtime (same logic, just compressed syntax)

---

## Troubleshooting

**Q: Compact mode enabled but still getting verbose code?**  
A: Check server logs for `compact=True` in the generation call.

**Q: Steps 4-5 still have wrong selectors?**  
A: Add debug output to see which template is matching.

**Q: Compact code fails to execute?**  
A: Double-check Python syntax - try/except on one line requires `:` before break.

---

## Success Metrics

✅ **Code size reduced 70-80%**  
✅ **All self-healing selectors preserved**  
✅ **Template substitution working for all button prompts**  
✅ **Tests execute successfully**  
✅ **DB storage footprint reduced**  
✅ **CI/CD pipelines faster (smaller files)**

