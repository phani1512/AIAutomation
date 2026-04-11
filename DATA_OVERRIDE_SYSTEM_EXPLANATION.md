# 🎯 Data Override System - Complete Explanation

**Date:** March 20, 2026  
**Your Question:** "how can user send their defined data... and edit the data while execution as same as test cases created from recorder"

## ✅ YES - This Already Works!

The system supports **data override for ALL prompts**, not just template-based ones. Here's how:

---

## 🔄 How It Works (3-Tier Priority System)

### Priority Order:
```
1. EXECUTION OVERRIDE (Highest)  ← User changes value in modal before running
   ↓
2. STORED VALUE (Medium)         ← Value entered when creating step
   ↓
3. EXTRACTED VALUE (Fallback)    ← Regex extraction from prompt text
```

---

## 📝 Step-by-Step Example

### Creating a Test (Test Builder):

**Step 1: Add prompt**
```
Prompt: "enter username in login field"
Data Value: "admin123"  ← User enters this in the value field
```

**What gets stored:**
```json
{
  "step": 1,
  "prompt": "enter username in login field",
  "value": "admin123"  ← Stored separately from prompt!
}
```

### Executing the Test:

**1. User clicks ▶️ Execute**

**2. Modal appears automatically:**
```
┌─────────────────────────────────────────┐
│  🔧 Override Test Data                  │
├─────────────────────────────────────────┤
│                                         │
│  Step 1: enter username in login field │
│  ┌─────────────────────────────────┐   │
│  │ admin123                         │   │ ← Pre-filled with stored value
│  └─────────────────────────────────┘   │
│                                         │
│  Step 3: enter password field          │
│  ┌─────────────────────────────────┐   │
│  │ SecurePass123                    │   │ ← Can edit before running
│  └─────────────────────────────────┘   │
│                                         │
│  [▶️ Execute with Data]  [❌ Cancel]   │
└─────────────────────────────────────────┘
```

**3. User can:**
- ✅ Keep original value ("admin123")
- ✅ Change to different value ("testuser@test.com")
- ✅ Clear and leave empty

**4. Backend receives:**
```json
{
  "data_overrides": {
    "1": "testuser@test.com"  ← User's override
  }
}
```

---

## 🔍 Backend Processing

**File:** `test_suite_runner.py`

```python
# For each step during execution:

step_value = step.get('value')  # Get stored value
effective_value = None

# PRIORITY 1: Check for user override (from modal)
if str(step_number) in data_overrides:
    effective_value = data_overrides[str(step_number)]
    logger.info(f"[DATA OVERRIDE] Using override: {effective_value}")

# PRIORITY 2: Use stored value (from when step was created)
elif step_value:
    effective_value = step_value
    logger.info(f"[STORED VALUE] Using stored: {effective_value}")

# PRIORITY 3: Extract from prompt (backward compatibility)
else:
    match = re.search(r'(?:type|enter|input)\s+["\']?([^"\'\s]+)["\']?', prompt)
    if match:
        effective_value = match.group(1).strip()
        logger.info(f"[EXTRACTED VALUE] From prompt: {effective_value}")

# Apply effective_value to the prompt
if effective_value:
    prompt = modify_prompt_with_value(prompt, effective_value)
```

---

## 💡 Integration with Placeholders

### How `{VALUE}` placeholders work with override system:

**1. Dataset Entry (Fixed):**
```json
{
  "prompt": "enter text in username field",
  "code": "element.sendKeys(\"{VALUE}\");"  ← Placeholder in code
}
```

**2. User's Test Step:**
```json
{
  "step": 1,
  "prompt": "enter text in username field",
  "value": "john@test.com"  ← User's data
}
```

**3. During Execution:**

Backend substitutes `{VALUE}` → `"john@test.com"`:

```java
// Generated code:
WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
WebElement element = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id("username")));
element.clear();
element.sendKeys("john@test.com");  ← {VALUE} replaced with actual data
```

**4. If User Overrides in Modal:**

Changes to "jane@test.com" → Backend uses that instead:

```java
element.sendKeys("jane@test.com");  ← Override takes priority!
```

---

## ✅ Works for ALL Prompts (Not Just Templates)

### Example 1: Non-Template Prompt
```
Prompt: "click the login button"
Value: (empty)  ← No value needed for clicks
```
✅ **Works** - Modal doesn't show this step (no input action)

### Example 2: Template Prompt with Parameter
```
Prompt: "enter {username} in username field"  ← Template
Value: "admin123"  ← User's data
```
✅ **Works** - Template matcher extracts {username}, system substitutes with "admin123"

### Example 3: Simple Input Prompt
```
Prompt: "type search query"
Value: "automation testing"  ← User's data
```
✅ **Works** - Stored value used, can override in modal

### Example 4: Old Test (No Value Field)
```
Prompt: "enter admin123 in username"
Value: (null)  ← Old test without value field
```
✅ **Works** - Priority 3: Extracts "admin123" from prompt text

---

## 🎨 User Experience (Same as Recorder!)

### Recorder Tests:
```
1. Record actions (browser records input values)
2. Click Execute
3. Modal shows all input fields with recorded values
4. Edit values
5. Execute with new data
```

### Test Builder Tests:
```
1. Create steps + enter values manually
2. Click Execute
3. Modal shows all steps with stored values  ← Same modal!
4. Edit values
5. Execute with new data
```

**✅ Consistent UX!** Users already familiar with recorder will know exactly what to do.

---

## 🚀 Key Benefits

### 1. **Data Reusability**
Same test, different data without editing:
- Development: `user1@dev.com`
- QA: `user2@qa.com`
- Production: `user3@prod.com`

### 2. **No Dataset Changes Needed**
- Dataset has `{VALUE}` placeholders
- User's data stored separately
- Substitution happens at runtime

### 3. **Flexible Testing**
- Happy path: Use default values
- Edge cases: Override with special chars, empty, long strings
- Data-driven: Run same test with CSV/JSON data

### 4. **Backward Compatible**
- Old tests without values still work
- Regex extraction as fallback
- No breaking changes

---

## 📊 Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ 1. USER CREATES TEST                                        │
│                                                              │
│  Prompt: "enter username in field"                          │
│  Value:  "admin123"              ← Stored in session        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. TEST SAVED                                               │
│                                                              │
│  {                                                           │
│    "step": 1,                                               │
│    "prompt": "enter username in field",                     │
│    "value": "admin123"        ← Persisted in JSON           │
│  }                                                           │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. USER CLICKS EXECUTE                                      │
│                                                              │
│  Modal appears with value pre-filled: "admin123"           │
│  User edits: "testuser@test.com"    ← Override             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. BACKEND EXECUTION                                        │
│                                                              │
│  Priority Check:                                            │
│  ✓ Override exists: "testuser@test.com" → USE THIS         │
│    Stored value: "admin123"          → SKIP                 │
│    Extracted: (none)                  → SKIP                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. CODE GENERATION                                          │
│                                                              │
│  Dataset code: element.sendKeys("{VALUE}")                  │
│  Substitute: {VALUE} → "testuser@test.com"                  │
│  Final: element.sendKeys("testuser@test.com")               │
└─────────────────────────────────────────────────────────────┘
```

---

## ✨ Summary

### Your Question: ✅ ANSWERED

> "how can user send their defined data... edit the data while execution"

**Answer:**
1. ✅ Users enter data in "Data Value" field when creating steps
2. ✅ Data stored separately from prompt
3. ✅ Override modal appears before execution (just like recorder!)
4. ✅ Users can edit values before running
5. ✅ Works for ALL prompts (template and non-template)
6. ✅ No need to change dataset - placeholders handle it

### No Changes Needed:
- ❌ Don't modify dataset for each user's data
- ❌ Don't edit tests to change values
- ✅ Just use the override modal!

### This System is Already Working:
- Test Builder has "Data Value" input field
- Backend stores values with steps
- Execution modal allows editing
- 3-tier priority handles all cases

---

**Status:** ✅ Fully implemented and working!  
**Documentation:** TEST_BUILDER_DATA_VALUES_FEATURE.md
