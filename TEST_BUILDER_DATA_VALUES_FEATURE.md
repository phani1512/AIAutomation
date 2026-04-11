# Test Builder Data Values Feature

**Date:** March 20, 2026  
**Status:** ✅ COMPLETE

---

## Problem Summary

**User Question:**
> "how can user send their defined data as I guess our prompts can't be able to enter as per user, if I am correct we need to change our dataset as per user entering data and even we need to implement such that user can edit the data while execution as same as test cases created from recorder"

**Issues Identified:**
1. ❌ Users couldn't specify **what data** to enter when creating prompts
2. ❌ Values were embedded in prompt text ("enter admin123"), not editable separately
3. ❌ Data override modal used unreliable regex to extract values
4. ❌ No way to change test data during execution

**Root Cause:**
- Prompt structure had no explicit `value` field
- Values were only extracted from prompt text using regex patterns
- This made data reuse and override difficult

---

## Solution Implemented

### ✅ 1. Added Explicit Value Field to Steps

**Data Structure (Before):**
```json
{
  "step": 1,
  "prompt": "enter admin123 in username field",
  "url": "https://example.com"
}
```

**Data Structure (After):**
```json
{
  "step": 1,
  "prompt": "enter username in login field",
  "url": "https://example.com",
  "value": "admin123"  // ← NEW: Explicit data value
}
```

**Benefits:**
- Clear separation of action and data
- Easy to override during execution
- Can reuse same test with different data
- More maintainable and testable

---

### ✅ 2. Updated Test Builder UI

**File:** `src/web/pages/test-builder.html`

**Added New Input Field:**

```html
<div class="form-group">
    <label for="stepValue">Data Value (Optional - for input/type actions):</label>
    <input 
        type="text" 
        id="stepValue" 
        placeholder="e.g., username, password, search query..."
    >
    <div style="font-size: 0.8em; color: var(--text-secondary); margin-top: 5px;">
        💡 Enter the actual data to use (can be changed during execution)
    </div>
</div>
```

**User Workflow:**
1. User writes action: "enter username in login field"
2. User enters value: "admin123"
3. System stores both separately
4. During execution, value can be changed without modifying test

**Display in Step List:**
- Shows value with special styling (blue badge)
- Example: `📝 Data: admin123`

---

### ✅ 3. Updated JavaScript to Collect Values

**File:** `src/web/js/test-builder.js`

**Changes:**

1. **Collect value from input field:**
```javascript
const value = document.getElementById('stepValue').value.trim();

const payload = { prompt };
if (url) payload.url = url;
if (value) payload.value = value;  // ← Send to API
```

2. **Clear value field after adding step:**
```javascript
document.getElementById('stepValue').value = '';
```

3. **Display value in step cards:**
```javascript
${step.value ? `
    <div style="font-size: 0.85em; color: #3b82f6;">
        📝 Data: <code>${step.value}</code>
    </div>
` : ''}
```

---

### ✅ 4. Updated Backend to Store Values

**File:** `src/main/python/test_session_manager.py`

**Updated `add_prompt` Method:**

```python
def add_prompt(self, prompt: str, url: Optional[str] = None, 
               value: Optional[str] = None,  # ← NEW parameter
               parsed: Optional[Dict] = None, 
               resolved_element: Optional[Dict] = None,
               generated_code: Optional[str] = None) -> int:
    """
    Args:
        prompt: Natural language action
        url: Optional URL to navigate to
        value: Optional data value (e.g., username, password)  ← NEW
        ...
    """
    step = {
        'step': step_number,
        'prompt': prompt,
        'url': url_to_store,
        'value': value,  # ← Stored in step
        'timestamp': datetime.now().isoformat(),
        'parsed': parsed,
        'resolved_element': resolved_element,
        'generated_code': generated_code
    }
    self.prompts.append(step)
```

**Updated `update_prompt` Method:**

```python
def update_prompt(self, step_number: int, prompt: str, 
                 url: Optional[str] = None, 
                 value: Optional[str] = None) -> bool:  # ← NEW parameter
    """Update an existing prompt step."""
    if 0 < step_number <= len(self.prompts):
        self.prompts[step_number - 1]['prompt'] = prompt
        if url is not None:
            self.prompts[step_number - 1]['url'] = url
        if value is not None:  # ← Update value
            self.prompts[step_number - 1]['value'] = value
```

**File:** `src/main/python/api_server_modular.py`

```python
data = request.get_json()
prompt = data.get('prompt', '')
url = data.get('url')
value = data.get('value')  # ← Get from request

# Pass to session
step_number = session.add_prompt(
    prompt=prompt,
    url=url,
    value=value,  # ← Pass to session
    parsed=result.get('parsed'),
    resolved_element=result.get('resolved_element'),
    generated_code=result.get('code')
)
```

**Test Case Saving:**
- Values automatically saved when test case is created
- `test_case.steps = session_data['prompts']` includes value field
- Saved to JSON file with full step data

---

### ✅ 5. Improved Data Override Modal

**File:** `src/web/js/test-suite.js`

**Before (Unreliable Regex):**
```javascript
// ❌ Problem: Regex extraction often failed
const typeMatch = prompt.match(/(?:type|enter|input|fill)\s+(.+?)(?:\s+in|\s+into|$)/i);
if (typeMatch) {
    extractedValue = typeMatch[1].trim();
}
```

**After (Use Stored Values):**
```javascript
// ✅ Solution: Use stored value, fallback to extraction
let defaultValue = step.value || '';  // Use stored value first!
if (!defaultValue) {
    // Only extract if no stored value (backward compatibility)
    const typeMatch = prompt.match(/(?:type|enter|input)\s+["']?([^"'\s]+)["']?/i);
    if (typeMatch) {
        defaultValue = typeMatch[1].trim();
    }
}
```

**Enhanced Modal:**
- Fetches FULL test case details (not just summary)
- Uses stored values by default
- Shows indicator: "📝 Stored value" vs "⚠️ Extracted from prompt"
- Includes more action keywords: type, enter, input, fill, search, write

**API Call:**
```javascript
// OLD: Fetched list (no step details)
const response = await fetch(`${API_URL}/test-suite/test-cases`);

// NEW: Fetches single test with full details
const response = await fetch(`${API_URL}/test-suite/test-cases/${testCaseId}`);
```

---

### ✅ 6. Enhanced Execution Logic

**File:** `src/main/python/test_suite_runner.py`

**Before (Simple Override):**
```python
# ❌ Only checked for override, no stored value support
if str(step_number) in data_overrides:
    override_value = data_overrides[str(step_number)]
    # Regex replacement...
```

**After (Priority Chain):**
```python
# ✅ Three-tier priority: override > stored > extracted
step_value = step.get('value')  # Get stored value

# Determine the value to use
effective_value = None
if str(step_number) in data_overrides:
    # 1. User override (highest priority)
    effective_value = data_overrides[str(step_number)]
    logger.info(f"[DATA OVERRIDE] Using override: {effective_value}")
elif step_value:
    # 2. Stored value (from when step was created)
    effective_value = step_value
    logger.info(f"[STORED VALUE] Using stored: {effective_value}")
else:
    # 3. Extract from prompt (fallback for old tests)
    match = re.search(r'(?:type|enter|input)\s+["\']?([^"\'\s]+)["\']?', prompt)
    if match:
        effective_value = match.group(1).strip()
        logger.info(f"[EXTRACTED VALUE] From prompt: {effective_value}")

# Apply value to prompt if we have one
if effective_value:
    prompt = modify_prompt_with_value(prompt, effective_value)
```

**Priority Order:**
1. **User Override** - Value entered in override modal (highest priority)
2. **Stored Value** - Value specified when creating test step
3. **Extracted Value** - Fallback extraction from prompt text (backward compatibility)

**Logging:**
- Clear logs show which value source was used
- Helps debug data flow
- Example: `[STORED VALUE] Step 2: Using stored value: admin123`

---

## Usage Examples

### Example 1: Login Test with Data Values

**Creating Test:**
```
Step 1:
  Prompt: "navigate to login page"
  URL: "https://example.com/login"
  Value: (empty)

Step 2:
  Prompt: "enter username in email field"
  URL: (empty)
  Value: "test.user@example.com"  ← Specified!

Step 3:
  Prompt: "enter password in password field"
  URL: (empty)
  Value: "SecurePass123"  ← Specified!

Step 4:
  Prompt: "click login button"
  URL: (empty)
  Value: (empty)
```

**Saved Test Case:**
```json
{
  "test_case_id": "TC001",
  "name": "User Login",
  "steps": [
    {
      "step": 1,
      "prompt": "navigate to login page",
      "url": "https://example.com/login",
      "value": null
    },
    {
      "step": 2,
      "prompt": "enter username in email field",
      "url": null,
      "value": "test.user@example.com"
    },
    {
      "step": 3,
      "prompt": "enter password in password field",
      "url": null,
      "value": "SecurePass123"
    },
    {
      "step": 4,
      "prompt": "click login button",
      "url": null,
      "value": null
    }
  ]
}
```

**Execution with Different Data:**
1. Click ▶️ Execute on test
2. Modal shows:
   ```
   Step 2: enter username in email field
   [test.user@example.com]  ← Pre-filled with stored value
   
   Step 3: enter password in password field
   [SecurePass123]  ← Pre-filled with stored value
   ```
3. User changes to:
   ```
   [admin@example.com]  ← Override
   [AdminPass456]  ← Override
   ```
4. Test executes with new values!

---

### Example 2: Search Test with Multiple Keywords

**Creating Test:**
```
Step 1:
  Prompt: "enter search query in search box"
  Value: "automation testing"  ← Default search term

Step 2:
  Prompt: "click search button"
```

**Test Reuse:**
- Run 1: Search for "automation testing" (default)
- Run 2: Override with "performance testing"
- Run 3: Override with "security testing"
- Same test, different data!

---

### Example 3: Form Filling Test

**Creating Test:**
```
Step 1: enter first name → "John"
Step 2: enter last name → "Doe"
Step 3: enter email → "john.doe@email.com"
Step 4: enter phone → "555-1234"
Step 5: select country → "United States"
Step 6: click submit
```

**Execution Options:**
- ✅ Run with default data (John Doe)
- ✅ Override with test data (Jane Smith)
- ✅ Override with edge cases (empty fields, special chars)
- ✅ Data-driven testing with different datasets

---

## Key Benefits

### 1. ✅ Data Separation
- Actions and data are separate
- Easier to maintain and update
- Clear intent in test design

### 2. ✅ Test Reusability
- Same test with different data
- No need to duplicate tests for different users
- Supports data-driven testing

### 3. ✅ Runtime Flexibility
- Change data during execution
- No need to edit and re-save test
- Quick exploratory testing

### 4. ✅ Better Data Management
- Explicitly see what data is used
- Easy to identify sensitive data (passwords, etc.)
- Can implement data vaults/secrets later

### 5. ✅ Backward Compatibility
- Old tests without values still work
- System falls back to extracting from prompt
- No breaking changes

### 6. ✅ Just Like Recorder!
- Same user experience as Recorder tests
- Consistent override modal interface
- Users already familiar with the flow

---

## Technical Architecture

### Data Flow

```
┌──────────────────────────────────────────────────────────────┐
│ 1. TEST CREATION (Test Builder)                             │
│                                                                │
│    User Input:                                                │
│    - Prompt: "enter username in field"                       │
│    - Value: "admin123"                                        │
│                                                                │
│    ↓                                                          │
│                                                                │
│    JavaScript (test-builder.js):                             │
│    - Collects value from #stepValue input                    │
│    - Sends to API: { prompt, url, value }                    │
│                                                                │
│    ↓                                                          │
│                                                                │
│    Backend (api_server_modular.py):                          │
│    - Receives value from request                              │
│    - Calls session.add_prompt(..., value=value)              │
│                                                                │
│    ↓                                                          │
│                                                                │
│    Session Manager (test_session_manager.py):                │
│    - Stores in step dict: {'value': 'admin123'}              │
│    - Saved in memory                                          │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ 2. TEST SAVING                                                │
│                                                                │
│    Test Case Builder (test_case_builder.py):                 │
│    - test_case.steps = session_data['prompts']               │
│    - Copies all fields including 'value'                      │
│    - Saves to JSON file                                       │
│                                                                │
│    File: test_cases/builder/TC001_user_login.json            │
│    {                                                           │
│      "steps": [                                                │
│        {"prompt": "...", "value": "admin123"}                 │
│      ]                                                         │
│    }                                                           │
└──────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ 3. TEST EXECUTION                                             │
│                                                                │
│    User clicks Execute →                                      │
│                                                                │
│    Frontend (test-suite.js):                                 │
│    - Fetches full test details                                │
│    - Finds steps with values                                  │
│    - Shows modal with pre-filled values                       │
│    - User can edit values                                     │
│    - Sends: data_overrides: {"2": "newuser@test.com"}        │
│                                                                │
│    ↓                                                          │
│                                                                │
│    Backend (test_suite_runner.py):                           │
│    - For each step:                                           │
│      1. Check data_overrides[step_num]  (highest priority)   │
│      2. Check step.get('value')         (medium priority)    │
│      3. Extract from prompt             (fallback)           │
│    - Uses effective_value in execution                        │
│                                                                │
│    ↓                                                          │
│                                                                │
│    Browser Execution:                                         │
│    - Modified prompt: "enter newuser@test.com in field"      │
│    - Element found and interacted with                        │
│    - Test completes with custom data                          │
└──────────────────────────────────────────────────────────────┘
```

---

## Files Modified

### Frontend
1. **`src/web/pages/test-builder.html`**
   - Added `<input id="stepValue">` field
   - Added tooltip and placeholder

2. **`src/web/js/test-builder.js`**
   - Collect value from input field
   - Send value in API payload
   - Clear value field after adding step
   - Display value in step cards (blue badge)

3. **`src/web/js/test-suite.js`**
   - Updated `showBuilderDataOverrideModal()`:
     - Fetch full test details
     - Use stored values instead of regex extraction
     - Enhanced modal UI
     - Better fallback logic

### Backend
4. **`src/main/python/test_session_manager.py`**
   - Updated `add_prompt()` signature: added `value` parameter
   - Store value in step dict
   - Updated `update_prompt()`: support value updates

5. **`src/main/python/api_server_modular.py`**
   - Extract value from request
   - Pass value to session.add_prompt()

6. **`src/main/python/test_suite_runner.py`**
   - Enhanced execution logic:
     - Check for stored values
     - Three-tier priority (override > stored > extracted)
     - Better logging
     - More reliable value replacement

---

## Testing Checklist

### ✅ Test Scenario 1: Basic Value Storage
1. Open Test Builder
2. Add step: "enter username in login field"
3. Enter value: "testuser"
4. Click Add Step
5. **Expected:** Step shows "📝 Data: testuser"

### ✅ Test Scenario 2: Save and Load
1. Create test with values
2. Save test case
3. Reload page
4. Load test from sessions
5. **Expected:** Values are preserved

### ✅ Test Scenario 3: Override During Execution
1. Create test with value "user1"
2. Save test case
3. Go to Test Suite
4. Click Execute
5. Change value to "user2" in modal
6. **Expected:** Test runs with "user2"

### ✅ Test Scenario 4: Empty Values (Optional)
1. Create step without value
2. Prompt: "click login button"
3. **Expected:** No value shown, works fine

### ✅ Test Scenario 5: Backward Compatibility
1. Load old test (created before this feature)
2. Execute test
3. **Expected:** Values extracted from prompt, test works

### ✅ Test Scenario 6: Multiple Values
1. Create login test:
   - Step 2: username value
   - Step 3: password value
2. Execute with overrides for both
3. **Expected:** Both values changeable

---

## Future Enhancements

### 1. 🔮 Data Templates
```json
{
  "templates": {
    "admin_user": {
      "username": "admin@test.com",
      "password": "AdminPass123"
    },
    "regular_user": {
      "username": "user@test.com",
      "password": "UserPass123"
    }
  }
}
```

### 2. 🔮 Environment Variables
```
${ENV:USERNAME}
${ENV:PASSWORD}
${CONFIG:API_URL}
```

### 3. 🔮 Data Generators
```
${RANDOM:email}
${UUID}
${TIMESTAMP}
${FAKER:name}
```

### 4. 🔮 Secrets Vault Integration
- Store sensitive data securely
- Retrieve during execution
- Mask in logs and reports

### 5. 🔮 CSV/Excel Import
- Bulk data import
- Data-driven test execution
- Multiple test runs with different datasets

---

## Summary

✅ **Problem Solved:** Users can now define and edit test data separately from actions  
✅ **User Experience:** Same as Recorder tests - familiar and consistent  
✅ **Backward Compatible:** Old tests still work with regex fallback  
✅ **Flexible:** Override data at execution time without editing test  
✅ **Maintainable:** Clear separation of action and data  
✅ **Extensible:** Foundation for advanced data features  

**Implementation Quality:**
- Clean code with proper error handling
- Good logging for debugging
- Graceful fallbacks for edge cases
- Follows existing patterns and conventions

---

**Status:** Ready for use! 🎉
