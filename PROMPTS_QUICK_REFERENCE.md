# Quick Reference - All Prompts Documentation

**Last Updated:** November 27, 2025  
**Total Prompts:** 1,718 unique prompts across 4 datasets

---

## 📚 Documentation Files Overview

| File | Content | Use When |
|------|---------|----------|
| **ALL_PROMPTS_CATALOG.md** | Detailed guide with usage patterns, examples, and best practices | You need to understand how to use prompts with examples |
| **ALL_DATASETS_PROMPTS_COMPLETE.md** | Complete listing of all 1,718 prompts organized by dataset | You want to see all prompts from all datasets in one place |
| **SIRCON_PROMPTS_APPENDIX.md** | Comprehensive reference with dataset summaries and Sircon A-Z listing | You need detailed reference with statistics and guidelines |
| **SIRCON_PROMPTS_COMPLETE.txt** | Plain text list of 1,579 Sircon prompts | You need a simple text file for searching/filtering |
| **DATASET_ENHANCEMENT_SUMMARY.md** | Documentation of recent enhancements to common-web-actions | You want to understand recent improvements |

---

## 📊 Dataset Statistics

| Dataset | File | Prompts | Weight | Purpose |
|---------|------|---------|--------|---------|
| Common Web Actions | `common-web-actions-dataset.json` | 39 | 1.5x | Generic web patterns |
| Selenium Methods | `selenium-methods-dataset.json` | 99 | 1.0x | WebDriver API |
| Element Locators | `element-locator-patterns.json` | 21 | 1.2x | Locator strategies |
| Sircon UI | `sircon_ui_dataset.json` | 1,579 | 2.0x | Application-specific |
| **TOTAL** | - | **1,718** | - | Complete corpus |

---

## 🎯 Quick Access by Use Case

### I want to...

#### See ALL prompts from ALL datasets
→ **ALL_DATASETS_PROMPTS_COMPLETE.md** (1,718 prompts organized by dataset)

#### Learn how to USE prompts with examples
→ **ALL_PROMPTS_CATALOG.md** (Detailed guide with usage patterns)

#### Find a specific Sircon UI prompt
→ **SIRCON_PROMPTS_APPENDIX.md** (A-Z listing with 1,579 prompts)

#### Get statistics and dataset information
→ **SIRCON_PROMPTS_APPENDIX.md** (Complete statistics and summaries)

#### Search/grep through Sircon prompts
→ **SIRCON_PROMPTS_COMPLETE.txt** (Plain text, easy to search)

#### Understand recent changes
→ **DATASET_ENHANCEMENT_SUMMARY.md** (Enhancement documentation)

---

## 💡 Common Prompt Patterns

### Common Web Actions (Generic Patterns)
- `navigate to {URL}`
- `enter {TEXT} in {FIELD} field`
- `click {BUTTON_NAME} button`
- `select {OPTION} from {DROPDOWN} dropdown`
- `upload file {FILE_PATH}`
- `wait for {ELEMENT} to appear`
- `verify {ELEMENT} {CONDITION}`

### Sircon UI (Application-Specific)
- `enter pvalaboju@vertafore.com in producer-email field`
- `click on producer-login`
- `wait for login to be visible`
- `click access management`
- `enter {NAME} in first name field`

### Selenium Methods (API Calls)
- `findElement`
- `click`
- `sendKeys`
- `getText`
- `isDisplayed`
- `WebDriverWait`
- `Select.selectByVisibleText`

---

## 🔧 Usage Examples

### Single Action
```
Prompt: "click search button"
Result: driver.findElement(By.id("searchBtn")).click();
```

### With Placeholder
```
Prompt: "enter john@example.com in email field"
Result: driver.findElement(By.id("email")).sendKeys("john@example.com");
```

### Multi-Step Workflow
```
Prompt: "navigate to https://example.com and enter John in first name field and click submit button"
Result: 
    driver.get("https://example.com");
    driver.findElement(By.name("firstName")).sendKeys("John");
    driver.findElement(By.id("submitBtn")).click();
```

---

## 📈 Model Information

| Metric | Value |
|--------|-------|
| **Total Entries** | 1,737 |
| **Total Tokens** | 468,602 |
| **Perplexity** | 1.70 (Excellent) |
| **Model Size** | 815 KB |
| **Unique Contexts** | 30,430 |
| **N-gram Size** | 4 |
| **Vocabulary Size** | 4,288 |

---

## 🚀 Getting Started

1. **Browse Available Prompts:**
   - Open `ALL_DATASETS_PROMPTS_COMPLETE.md` to see all 1,718 prompts
   
2. **Find Prompts by Category:**
   - Generic web actions → Common Web Actions section (39 prompts)
   - Selenium API → Selenium Methods section (99 patterns)
   - Sircon-specific → Sircon UI section (1,579 prompts)

3. **Use Prompts in Your Code:**
   - Copy exact prompt text
   - Replace `{PLACEHOLDERS}` with actual values
   - Combine prompts using "and" for multi-step workflows

4. **Get Help:**
   - See `ALL_PROMPTS_CATALOG.md` for detailed examples
   - Check `SIRCON_PROMPTS_APPENDIX.md` for usage guidelines

---

## 📝 File Locations

All documentation files are in the root directory:
```
WebAutomation/
├── ALL_PROMPTS_CATALOG.md
├── ALL_DATASETS_PROMPTS_COMPLETE.md
├── SIRCON_PROMPTS_APPENDIX.md
├── SIRCON_PROMPTS_COMPLETE.txt
├── DATASET_ENHANCEMENT_SUMMARY.md
└── THIS_FILE_QUICK_REFERENCE.md
```

Dataset files are in `src/resources/`:
```
src/resources/
├── common-web-actions-dataset.json
├── selenium-methods-dataset.json
├── element-locator-patterns.json
└── sircon_ui_dataset.json
```

---

## ✨ Recent Updates

**November 27, 2025:**
- ✅ Enhanced common-web-actions-dataset.json (3 → 40 prompts, 100% coverage)
- ✅ Created ALL_DATASETS_PROMPTS_COMPLETE.md (all 1,718 prompts in one file)
- ✅ Updated SIRCON_PROMPTS_APPENDIX.md with all dataset summaries
- ✅ Retrained model with 468,602 tokens
- ✅ Maintained excellent perplexity (1.70)

---

**For detailed information, always refer to the specific documentation file based on your needs.**
