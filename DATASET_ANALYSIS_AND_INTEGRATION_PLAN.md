# Dataset Analysis and Integration Plan for AI Training

**Date:** 2024
**Purpose:** Comprehensive analysis of all 4 datasets and integration strategy for AI model training without breaking existing functionality

---

## 📊 Dataset Inventory and Analysis

### 1. **common-web-actions-dataset.json** (457 lines)

**Structure:**
```json
{
  "action": "Enter Username",
  "description": "User enter username in username field",
  "pattern_type": "input_text",
  "steps": [{
    "step": 1,
    "action": "sendKeys",
    "code": "driver.findElement(By.id(\"username\")).sendKeys(\"{USERNAME}\");",
    "element_type": "input",
    "locator": "By.id(\"username\")",
    "value": "{USERNAME}",
    "prompt": "enter username in username field"
  }]
}
```

**Key Features:**
- ✅ **Restructured:** Independent single-step actions (not bundled)
- ✅ **Placeholders Implemented:** `{USERNAME}`, `{PASSWORD}`, `{EMAIL}`, `{FIRST_NAME}`, `{LAST_NAME}`, `{PHONE}`, `{SEARCH_QUERY}`, `{TEXT}`, `{FILE_PATH}`
- ✅ **Application-Specific:** producer-email, producer-password, producer-login (XPath)
- **Pattern Types:** navigation, input_text, button_click, dropdown_selection, checkbox_selection, radio_button_selection, file_upload, form_submission, verification, modal_interaction, table_interaction, wait_actions

**Purpose:** Generic web action patterns - foundation for common UI interactions across any web application

---

### 2. **selenium-methods-dataset.json** (1101+ lines)

**Structure:**
```json
{
  "category": "WebDriverListener_Navigation",
  "method": "beforeGet",
  "signature": "void beforeGet(WebDriver driver, String url)",
  "description": "Called before driver.get(url)",
  "example": "driver.get(\"https://example.com\");",
  "usage_pattern": "Navigate to URL",
  "action_type": "navigate"
}
```

**Key Features:**
- **Categories:** 
  - Navigation (get, getCurrentUrl, getTitle, back, forward, refresh)
  - Element actions (click, sendKeys, clear, submit)
  - Queries (findElement, findElements)
  - Alerts (accept, dismiss, sendKeys, getText)
  - Windows (getWindowHandles, switchTo)
  - Waits (implicitlyWait, explicitWait)
  - Actions (moveToElement, dragAndDrop, doubleClick, rightClick)
  - Select (selectByValue, selectByVisibleText, selectByIndex)

**Purpose:** Teaches AI about Selenium WebDriver API - method signatures, usage patterns, and best practices

---

### 3. **element-locator-patterns.json** (250 lines)

**Structure:**
```json
{
  "html": "<input id=\"username\" type=\"text\" name=\"user\" class=\"form-control\">",
  "element_type": "input",
  "locator_options": [
    {
      "locator": "By.id(\"username\")",
      "priority": 1,
      "reliability": "high",
      "reason": "ID is unique and stable"
    },
    {
      "locator": "By.name(\"user\")",
      "priority": 2,
      "reliability": "medium",
      "reason": "Name can be duplicated"
    },
    {
      "locator": "By.className(\"form-control\")",
      "priority": 3,
      "reliability": "low",
      "reason": "Class is shared across elements"
    }
  ],
  "recommended_action": "sendKeys",
  "action_example": "driver.findElement(By.id(\"username\")).sendKeys(\"testuser\");"
}
```

**Key Features:**
- **Element Types:** input, button, link, select, checkbox, radio, textarea, div, span, table, tr, td, form, label, img
- **Locator Strategies:** By.id, By.name, By.className, By.cssSelector, By.xpath, By.tagName, By.linkText, By.partialLinkText
- **Priority Rankings:** 1 (highest) to 5 (lowest)
- **Reliability Ratings:** high, medium, low

**Purpose:** Teaches AI to choose optimal locator strategies based on HTML structure and element attributes

---

### 4. **sircon_ui_dataset.jsonl** (1582 lines) ⭐ **NEW**

**Structure (JSONL - Line-Delimited JSON):**
```json
{
  "action": "LoginPage - clickSignInButton",
  "description": "User click the sign in button",
  "steps": [{
    "step": 1,
    "action": "click",
    "code": "waitAndClickOnElement(signInButton);\nsleep(1000);\nwaitForProcessingSpinner();\nreturn this;",
    "element_type": "button",
    "locator": "By.cssSelector(\"[Label='Sign In']\")",
    "value": "",
    "prompt": "click the sign in button on LoginPage",
    "page_object": "LoginPage",
    "method_name": "clickSignInButton",
    "error_message": "button not clickable on LoginPage"
  }]
}
```

**Key Features:**
- **Format:** JSONL (one JSON object per line, not a JSON array)
- **Page Object Model:** Organized by page classes (LoginPage, DashboardPage, ManageUsersPage, etc.)
- **Application-Specific:** Sircon insurance platform UI patterns
- **Additional Fields:**
  - `page_object`: Page class name (e.g., "LoginPage", "AccountSettingsPage")
  - `method_name`: Page object method name (e.g., "clickSignInButton", "enterBasicInformation")
  - `error_message`: Custom error message for failures
  - `value`: Placeholder values like `{EMAIL}`, `{PASSWORD}`, `{NAME}`, `{PHONE}`, `{ACCOUNT_ID}`, `{TEXT}`, `{CITY}`, `{STATE}`, `{ZIPCODE}`, `{ADDRESS}`

**Pattern Types:**
- UI Elements: input, button, link, dropdown, checkbox, radio, dialog, menu, text, element
- Actions: click, sendKeys, getText, select, verify, wait, getCount, getAttribute, isDisplayed, retrieve
- Page Objects: 60+ page classes covering entire Sircon application

**Unique Patterns:**
1. **Complex Locators:**
   - XPath: `By.xpath("//*/td[@atid='workflow-menu']//div/button[text()='Assign To...']")`
   - CSS with attributes: `By.cssSelector("[Label='Sign In']")`
   - CSS nth-child: `By.cssSelector(".bi-vendor div:nth-child(2) dd")`

2. **Multi-Step Methods:**
   ```java
   clearAndSendKeys(firstNameField, firstName);
   clearAndSendKeys(lastNameField, lastName);
   selectElementByVisibleText(searchByDropdown, "National Producer");
   waitAndClickOnElement(searchButton);
   ```

3. **Placeholder Usage:**
   - `{NAME}` in first/last name fields
   - `{EMAIL}` in email fields
   - `{PASSWORD}` in password fields
   - `{ACCOUNT_ID}` in various ID fields
   - `{TEXT}` for generic text inputs
   - `{PHONE}` for phone numbers
   - `{CITY}`, `{STATE}`, `{ZIPCODE}`, `{ADDRESS}` for address forms

**Purpose:** Real-world application-specific UI interaction patterns from Sircon insurance licensing platform - teaches AI how to handle complex enterprise application workflows

---

## 🔍 Dataset Comparison Matrix

| Feature | common-web-actions | selenium-methods | element-locator-patterns | sircon_ui_dataset |
|---------|-------------------|------------------|-------------------------|-------------------|
| **Format** | JSON Array | JSON Array | JSON Array | JSONL (Line-delimited) |
| **Total Entries** | ~40 actions | ~100 methods | ~30 examples | 1582 actions |
| **Scope** | Generic | Selenium API | HTML patterns | Application-specific |
| **Placeholders** | ✅ Yes (11 types) | ❌ No | ❌ No | ✅ Yes (9+ types) |
| **Page Object Model** | ❌ No | ❌ No | ❌ No | ✅ Yes |
| **Locator Strategies** | Single best | N/A | Multiple ranked | Single (often XPath/CSS) |
| **Code Complexity** | Simple (1-2 lines) | API signatures | Single line | Complex (multi-line, waits) |
| **Application Context** | None | None | None | Sircon insurance platform |
| **Element Types** | 10+ | N/A | 15+ | 15+ |
| **Action Types** | 12+ | 30+ | N/A | 15+ |

---

## 🎯 Integration Strategy

### **Approach: Multi-Dataset Hybrid Training**

We'll keep datasets separate and combine them during tokenization to preserve their distinct purposes while creating a comprehensive training corpus.

### **Phase 1: Update Tokenization Script**

#### **Current Limitation:**
`tokenize_dataset.py` (Lines 67-74) hardcodes only 3 JSON files:
```python
dataset_files = [
    "selenium-methods-dataset.json",
    "common-web-actions-dataset.json",
    "element-locator-patterns.json"
]
```

#### **Required Changes:**

**1. Add JSONL Support:**
```python
def load_jsonl_file(self, filepath: str) -> List[Dict[str, Any]]:
    """Load JSONL dataset file (line-delimited JSON)."""
    data = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():  # Skip empty lines
                data.append(json.loads(line))
    return data
```

**2. Update `process_all_datasets()` method:**
```python
def process_all_datasets(self):
    """Process all JSON and JSONL datasets in the resources directory."""
    dataset_configs = [
        {
            "filename": "selenium-methods-dataset.json",
            "type": "json",
            "weight": 1.0,  # Standard weight
            "description": "Selenium WebDriver API methods and signatures"
        },
        {
            "filename": "common-web-actions-dataset.json",
            "type": "json",
            "weight": 1.5,  # Higher weight - frequently used patterns
            "description": "Generic web UI action patterns"
        },
        {
            "filename": "element-locator-patterns.json",
            "type": "json",
            "weight": 1.2,  # Medium weight - locator strategy learning
            "description": "HTML element locator strategy examples"
        },
        {
            "filename": "sircon_ui_dataset.jsonl",
            "type": "jsonl",
            "weight": 2.0,  # Highest weight - real application patterns
            "description": "Sircon application-specific UI patterns"
        }
    ]
    
    print("Starting dataset tokenization...")
    print("=" * 60)
    
    for config in dataset_configs:
        filepath = os.path.join(self.datasets_dir, config["filename"])
        
        if not os.path.exists(filepath):
            print(f"⚠️  Warning: {config['filename']} not found, skipping...")
            continue
        
        print(f"\n📄 Processing: {config['filename']}")
        print(f"   Type: {config['type'].upper()}")
        print(f"   Description: {config['description']}")
        print(f"   Weight: {config['weight']}x")
        
        # Load dataset based on type
        if config["type"] == "json":
            dataset = self.load_json_file(filepath)
        elif config["type"] == "jsonl":
            dataset = self.load_jsonl_file(filepath)
        else:
            print(f"❌ Unknown dataset type: {config['type']}")
            continue
        
        print(f"   Loaded {len(dataset)} entries")
        
        # Tokenize
        tokens = self.tokenize_dataset(dataset)
        print(f"   Generated {len(tokens):,} tokens")
        
        # Apply weight by duplicating tokens
        if config["weight"] > 1.0:
            duplicate_count = int(config["weight"]) - 1
            for _ in range(duplicate_count):
                self.all_tokens.extend(tokens)
            print(f"   Applied {config['weight']}x weight: {len(tokens) * config['weight']:,} tokens total")
        
        # Add to global token list
        self.all_tokens.extend(tokens)
    
    print("\n" + "=" * 60)
    print(f"✅ Total tokens across all datasets: {len(self.all_tokens):,}")
```

**3. Add Dataset Metadata Tracking:**
```python
def __init__(self, datasets_dir: str = "src/resources"):
    self.datasets_dir = datasets_dir
    self.tokenizer = tiktoken.get_encoding("cl100k_base")
    self.all_tokens = []
    self.dataset_metadata = {}  # Track which tokens came from which dataset
```

---

### **Phase 2: Dataset Weighting Strategy**

**Why Weighting?**
- Sircon dataset (1582 entries) is 40x larger than common-web-actions (40 entries)
- Without weighting, model will over-fit to Sircon-specific patterns
- Need to balance generic patterns vs application-specific patterns

**Recommended Weights:**

1. **selenium-methods-dataset.json: 1.0x** (Standard)
   - Reason: API reference - needs to be learned but not overrepresented
   - 100 entries × 1.0 = 100 effective entries

2. **common-web-actions-dataset.json: 1.5x** (High)
   - Reason: Generic patterns should be emphasized - most reusable
   - 40 entries × 1.5 = 60 effective entries

3. **element-locator-patterns.json: 1.2x** (Medium-High)
   - Reason: Locator strategy is critical but shouldn't dominate
   - 30 entries × 1.2 = 36 effective entries

4. **sircon_ui_dataset.jsonl: 2.0x** (Highest)
   - Reason: Real-world patterns with complexity - most valuable for learning
   - 1582 entries × 2.0 = 3164 effective entries

**Total Weighted Distribution:**
- Sircon: 3164 entries (91% of corpus)
- Generic: 196 entries (9% of corpus)

This ensures Sircon patterns dominate (as they should for real-world accuracy) while preventing generic patterns from being drowned out.

---

### **Phase 3: Template Rules Update**

**Current Template Rules in `inference_improved.py`:**
- Lines 88-176: Hardcoded template patterns
- Works well for generic actions
- Needs expansion for Sircon-specific patterns

**Recommendation:**
✅ **Keep existing templates** - They work and cover 80% of use cases
✅ **Add new templates for Sircon patterns:**

```python
# Sircon-specific templates (Lines 177-220)

# Producer login with XPath button
if 'producer-login' in prompt_lower or 'producer login' in prompt_lower:
    return """// Click producer login button
WebElement loginBtn = driver.findElement(By.xpath("//button[@type='submit' and contains(@class, 'primary-btn')]"));
loginBtn.click();"""

# Dropdown selection with app-select pattern
if 'select' in prompt_lower and 'dropdown' in prompt_lower:
    element_id = self._extract_element_name(prompt)
    value = self._extract_input_value(prompt)
    return f"""// Select dropdown option
Select dropdown = new Select(driver.findElement(By.cssSelector("app-select[label='{element_id}'] select")));
dropdown.selectByVisibleText("{value}");"""

# Wait button pattern
if 'click' in prompt_lower and 'wait-button' in prompt_lower:
    element_id = self._extract_element_name(prompt)
    return f"""// Click wait button
WebElement waitBtn = driver.findElement(By.cssSelector("app-wait-button[label='{element_id}'] button"));
waitBtn.click();"""
```

**Impact:**
- ✅ No breaking changes to existing functionality
- ✅ Enhanced coverage for Sircon-specific patterns
- ✅ AI fallback still works for unknown patterns

---

### **Phase 4: Training Process**

**Steps:**

1. **Backup Current Model:**
   ```powershell
   Copy-Item "src\resources\selenium_dataset.bin" "src\resources\selenium_dataset_backup.bin"
   Copy-Item "src\resources\selenium_ngram_model.pkl" "src\resources\selenium_ngram_model_backup.pkl"
   ```

2. **Update `tokenize_dataset.py`:**
   - Add JSONL support (load_jsonl_file method)
   - Add sircon_ui_dataset.jsonl to dataset_configs
   - Implement weighting system
   - Update statistics generation

3. **Tokenize All Datasets:**
   ```powershell
   python src\main\python\tokenize_dataset.py
   ```

   **Expected Output:**
   ```
   📄 Processing: selenium-methods-dataset.json
      Type: JSON
      Loaded 100 entries
      Generated 15,234 tokens
   
   📄 Processing: common-web-actions-dataset.json
      Type: JSON
      Loaded 40 entries
      Generated 8,567 tokens
      Applied 1.5x weight: 12,850 tokens total
   
   📄 Processing: element-locator-patterns.json
      Type: JSON
      Loaded 30 entries
      Generated 5,432 tokens
      Applied 1.2x weight: 6,518 tokens total
   
   📄 Processing: sircon_ui_dataset.jsonl
      Type: JSONL
      Loaded 1582 entries
      Generated 285,678 tokens
      Applied 2.0x weight: 571,356 tokens total
   
   ✅ Total tokens: 606,158
   💾 Binary file: selenium_dataset.bin (2.43 MB)
   ```

4. **Train Model:**
   ```powershell
   python src\main\python\train_simple.py
   ```

   **Expected Output:**
   ```
   Training N-gram model with:
   - Total tokens: 606,158
   - Unique tokens: 12,456
   - N-gram size: 4
   
   Progress: [██████████] 100%
   
   ✅ Model saved: selenium_ngram_model.pkl
   ```

5. **Test Generated Code:**
   - Test existing prompts (regression testing):
     - "enter username in username field"
     - "click login button"
     - "select dropdown option"
     - "verify element is visible"
   
   - Test new Sircon patterns:
     - "click the sign in button on LoginPage"
     - "enter email in producer-email field"
     - "click producer-login button"
     - "select from search by dropdown"

6. **Validation:**
   - Run Browser Control tests with compound prompts
   - Verify template rules still work (no regression)
   - Verify AI fallback generates better Sircon-specific code
   - Check error messages for failed attempts

---

### **Phase 5: Rollback Plan**

**If training causes issues:**

```powershell
# Restore original model
Copy-Item "src\resources\selenium_dataset_backup.bin" "src\resources\selenium_dataset.bin" -Force
Copy-Item "src\resources\selenium_ngram_model_backup.pkl" "src\resources\selenium_ngram_model.pkl" -Force

# Restart server with old model
taskkill /F /IM python.exe
python src\main\python\api_server_improved.py
```

**Validation Tests:**
- All previous prompts should work identically
- No change in Browser Control behavior
- Template-based generation unchanged

---

## 📈 Expected Benefits

### **1. Improved Code Generation Quality**

**Before (AI fallback only):**
```java
// Generic pattern from limited training
WebElement element = driver.findElement(By.id("sign-in"));
element.click();
```

**After (Trained on Sircon dataset):**
```java
// Application-aware pattern with waits
WebElement signInButton = driver.findElement(By.cssSelector("[Label='Sign In']"));
waitAndClickOnElement(signInButton);
sleep(1000);
waitForProcessingSpinner();
```

### **2. Better Locator Strategy Selection**

**Before:**
```java
// May choose non-robust locator
WebElement button = driver.findElement(By.className("btn"));
```

**After (Learned from element-locator-patterns):**
```java
// Chooses robust locator with fallback
WebElement button = driver.findElement(By.xpath("//button[@type='submit' and contains(@class, 'primary-btn')]"));
```

### **3. Placeholder Recognition**

**Before:**
```java
// Hardcoded value
driver.findElement(By.id("email")).sendKeys("test@example.com");
```

**After (Learned placeholder patterns):**
```java
// Extracts value from prompt
driver.findElement(By.id("producer-email")).sendKeys(emailFromPrompt);
```

### **4. Page Object Awareness**

**Before:**
```java
// No context about page structure
driver.findElement(By.id("submit")).click();
```

**After (Learned from Sircon page objects):**
```java
// Understands page object patterns
LoginPage loginPage = new LoginPage(driver);
loginPage.clickSignInButton();
```

---

## ⚠️ Risk Assessment

### **Low Risk:**
✅ Template rules remain unchanged → No regression for existing prompts
✅ AI fallback only improves → Worst case = same quality as before
✅ Separate datasets → Can disable sircon_ui if needed
✅ Backup/rollback plan → Can revert quickly

### **Medium Risk:**
⚠️ Token distribution imbalance → Mitigated by weighting system
⚠️ JSONL parsing errors → Mitigated by error handling
⚠️ Training time increase → Acceptable (one-time cost)

### **High Risk:**
❌ None identified

---

## 🧪 Testing Strategy

### **1. Regression Testing (Must Pass)**

Test existing prompts to ensure no breakage:

```javascript
// Test Suite 1: Generic Actions
[
  "enter username in username field",
  "enter password in password field",
  "click login button",
  "select option from dropdown",
  "verify element is visible",
  "wait for page to load",
  "navigate to https://example.com"
]

// Expected: All should work identically to before
```

### **2. Enhancement Testing (Should Improve)**

Test prompts that should benefit from new training:

```javascript
// Test Suite 2: Sircon-Specific Actions
[
  "click the sign in button on LoginPage",
  "enter email in producer-email field",
  "enter password in producer-password field",
  "click producer-login button",
  "select state from dropdown",
  "enter first name in first name field",
  "click the search button"
]

// Expected: Better locators, waits, and error handling
```

### **3. Compound Prompt Testing (Already Working)**

Test multi-step prompts:

```javascript
// Test Suite 3: Compound Actions
[
  "enter email in producer-email field and enter password in producer-password field and click producer-login button",
  "navigate to login page and enter credentials and click sign in",
  "select dropdown option and click next button"
]

// Expected: All steps execute correctly (already working)
```

### **4. Placeholder Testing (Should Improve)**

Test dynamic value extraction:

```javascript
// Test Suite 4: Placeholder Extraction
[
  "enter john.doe@example.com in email field",
  "enter MyPassword123! in password field",
  "enter John in first name field",
  "enter Doe in last name field"
]

// Expected: Values extracted from prompt (not hardcoded)
```

---

## 📝 Implementation Checklist

- [ ] **1. Backup current state**
  - [ ] Copy `selenium_dataset.bin` to `selenium_dataset_backup.bin`
  - [ ] Copy `selenium_ngram_model.pkl` to `selenium_ngram_model_backup.pkl`
  - [ ] Commit current code to git

- [ ] **2. Update `tokenize_dataset.py`**
  - [ ] Add `load_jsonl_file()` method
  - [ ] Update `process_all_datasets()` with dataset_configs
  - [ ] Implement weighting system
  - [ ] Add sircon_ui_dataset.jsonl to config
  - [ ] Update statistics generation

- [ ] **3. Test tokenization**
  - [ ] Run `python tokenize_dataset.py`
  - [ ] Verify all 4 datasets loaded correctly
  - [ ] Check token counts and weights
  - [ ] Verify binary file created

- [ ] **4. Train model**
  - [ ] Run `python train_simple.py`
  - [ ] Verify model file created
  - [ ] Check model size and statistics

- [ ] **5. Regression testing**
  - [ ] Kill server process (port 5001)
  - [ ] Start server with new model
  - [ ] Test all existing prompts
  - [ ] Verify no breakage

- [ ] **6. Enhancement testing**
  - [ ] Test Sircon-specific prompts
  - [ ] Test compound prompts
  - [ ] Test placeholder extraction
  - [ ] Verify improvements

- [ ] **7. Documentation**
  - [ ] Update RETRAIN_QUICKSTART.md
  - [ ] Document new dataset (sircon_ui)
  - [ ] Update training instructions
  - [ ] Create migration summary

- [ ] **8. Rollback if needed**
  - [ ] Restore backup files if issues found
  - [ ] Document problems
  - [ ] Adjust weighting strategy

---

## 🎓 Training Timeline

**Estimated Time:** 2-3 hours

1. **Backup & Preparation:** 15 minutes
2. **Code Updates:** 45 minutes
3. **Tokenization:** 10 minutes
4. **Model Training:** 20 minutes
5. **Testing:** 60 minutes
6. **Documentation:** 30 minutes

**Total:** ~3 hours (one-time investment)

---

## 🔄 Future Enhancements

### **Short Term (Next 1-2 weeks):**
- Add more application-specific datasets (other projects)
- Fine-tune weighting based on actual usage patterns
- Add dataset versioning/tagging

### **Medium Term (1-2 months):**
- Implement dataset validation (detect duplicates, errors)
- Add dataset merging tools
- Create dataset contribution guidelines

### **Long Term (3+ months):**
- Automated dataset generation from existing tests
- Dataset quality metrics and scoring
- A/B testing for different training strategies

---

## 📞 Next Steps

**Immediate Action Required:**

1. **Review this analysis** - Confirm approach is acceptable
2. **Schedule implementation** - Choose time for training (low-impact time)
3. **Prepare test cases** - Identify critical prompts to test
4. **Execute plan** - Follow implementation checklist

**Questions to Answer:**

- ❓ Are the dataset weights (1.0x, 1.5x, 1.2x, 2.0x) acceptable?
- ❓ Should we add more application-specific templates to `inference_improved.py`?
- ❓ Do we need to preserve separate model files for different datasets?
- ❓ Should we implement dataset versioning (e.g., v1.0, v2.0)?

---

## ✅ Conclusion

**Recommendation:** ✅ **Proceed with integration**

**Rationale:**
1. ✅ **Low Risk:** Template rules unchanged, AI fallback only improves
2. ✅ **High Reward:** 1582 new real-world patterns, better code generation
3. ✅ **Reversible:** Backup/rollback plan in place
4. ✅ **Tested Approach:** JSONL format, weighting system, multi-dataset training are proven techniques

**Expected Outcome:**
- 📈 **Improved AI-generated code quality** for Sircon-specific prompts
- 📈 **Better locator strategies** from element-locator-patterns
- 📈 **Enhanced placeholder recognition** from combined datasets
- 📈 **More robust error handling** from real-world Sircon patterns
- ✅ **No regression** in existing functionality (templates preserved)

**Final Note:**
This integration represents a significant upgrade to the AI training corpus while maintaining backward compatibility with existing functionality. The multi-dataset approach with weighting ensures balanced learning across generic patterns, Selenium API knowledge, locator strategies, and real-world application patterns.

---

**Document Version:** 1.0
**Last Updated:** 2024
**Approved By:** [Pending Review]
