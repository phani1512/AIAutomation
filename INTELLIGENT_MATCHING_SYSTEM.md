# Intelligent Prompt Matching System

**Date:** March 20, 2026  
**Status:** ✅ COMPLETE

---

## Overview

The Test Builder now uses a **Multi-Strategy Intelligent Matching System** that tries multiple approaches to find the best match for your prompts. This gives you both **precision** (when patterns match exactly) and **flexibility** (for conversational prompts).

---

## How It Works

### Cascading Strategy Priority

```
User enters prompt → System tries strategies in order:

1. ✓ EXACT MATCH (100% confidence)
   ↓ Direct lookup in dataset
   ↓ "click the login button" → Found exact match
   
2. 📋 TEMPLATE MATCH (85-99% confidence)
   ↓ Pattern matching with parameter extraction
   ↓ "click Submit button" → Matches "click {text} button"
   ↓ Extracts: {text} = "Submit"
   
3. ≈ FUZZY MATCH (70-85% confidence)
   ↓ Similarity scoring against dataset
   ↓ "press the login btn" → Similar to "click the login button"
   
4. 🤖 ML INFERENCE (50% confidence)
   ↓ Neural network inference
   ↓ "tap on the save icon" → ML generates code
```

---

## Strategy Details

### 1. ✓ **Exact Match** (100% Confidence)

**How it works:**
- Direct lookup in dataset index
- Fastest and most accurate
- Returns pre-tested, production-ready code

**Example:**
```
User: "click the login button"
System: ✓ Exact match found
Code: WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
      WebElement element = wait.until(ExpectedConditions.elementToBeClickable(By.id("login-btn")));
      element.click();
```

**When to use:**
- When you know the exact wording from the dataset
- For common patterns that are already in the system
- When you want guaranteed accuracy

---

### 2. 📋 **Template Match** (85-99% Confidence)

**How it works:**
- Matches against parameterized templates
- Extracts parameter values from your prompt
- Substitutes parameters into template code

**Templates in Dataset:**
```json
{
  "prompt": "click {text} button",
  "code": "//button[contains(text(), '{TEXT}')]"
}

{
  "prompt": "enter {value} in {field_name}",
  "code": "//input[@name='{FIELD_NAME}']"
}
```

**Example:**
```
User: "click Submit button"
Match: "click {text} button" template
Extract: {text} = "Submit"
Code: //button[contains(text(), 'Submit')]

User: "enter admin@test.com in username field"
Match: "enter {value} in {field_name}" template  
Extract: {value} = "admin@test.com", {field_name} = "username"
Code: driver.findElement(By.name("username")).sendKeys("admin@test.com");
```

**Confidence Calculation:**
- More specific templates (more static text) = higher confidence
- Example: "click {text} button on navigation" (90%) vs "click {text}" (85%)

**When to use:**
- For button clicks with different text
- For form filling with variable data
- When pattern is consistent but values change

---

### 3. ≈ **Fuzzy Match** (70-85% Confidence)

**How it works:**
- Uses sequence matching algorithm
- Compares your prompt to all dataset entries
- Returns best similarity score

**Example:**
```
User: "press the login btn"
Best match: "click the login button" (82% similar)
Code: [uses code from matched entry]

User: "type username in email box"
Best match: "enter username in email field" (78% similar)
Code: [uses code from matched entry]
```

**Also checks:**
- Prompt variations stored in dataset
- Alternative phrasings ("click", "press", "tap")

**When to use:**
- When you're not sure of exact wording
- For slight variations of known patterns
- When exact/template don't match but should

---

### 4. 🤖 **ML Inference** (50% Confidence)

**How it works:**
- Neural network trained on dataset
- Generates code from scratch
- No guarantee of accuracy

**Example:**
```
User: "tap on the gear icon in top right corner"
System: No exact/template/fuzzy match found
Result: ML generates locator based on learned patterns
```

**When to use:**
- For completely novel patterns
- When exploring new UI interactions
- As last resort when nothing matches

**Important:** Always verify ML-generated code before using in production!

---

## Visual Feedback

Each step shows which strategy was used:

### Exact Match (Green)
```
✓ Exact Match 100%
```
- Maximum confidence
- Pre-tested code
- Safe for production

### Template Match (Blue)
```
📋 Template Match 92%
```
- High confidence
- Parameters extracted
- Review extracted values

### Fuzzy Match (Orange)
```
≈ Similar Match 78%
```
- Medium confidence
- Similar to known pattern
- Verify behavior

### ML Inference (Purple)
```
🤖 ML Inference 50%
```
- Unknown confidence
- Generated code
- Test thoroughly

---

## Usage Examples

### Example 1: Button Clicks

**Exact Match:**
```
Prompt: "click the login button"
Result: ✓ Exact Match 100%
```

**Template Match:**
```
Prompt: "click Submit button"
Result: 📋 Template Match 90%
       Matched: "click {text} button"
       Parameter: text="Submit"
```

**Fuzzy Match:**
```
Prompt: "press the submit btn"
Result: ≈ Similar Match 82%
       Similar to: "click the submit button"
```

**ML Inference:**
```
Prompt: "tap the blue circular save icon"
Result: 🤖 ML Inference 50%
       No dataset match, using AI
```

---

### Example 2: Form Filling

**Template Match:**
```
Prompt: "enter john@test.com in email field"
Result: 📋 Template Match 88%
       Matched: "enter {value} in {field_name}"
       Parameters: value="john@test.com", field_name="email"
```

**With Data Value Field:**
```
Prompt: "enter username in email field"
Value: "admin@example.com"
Result: 📋 Template Match 88%
       Will use value="admin@example.com" during execution
```

---

### Example 3: Navigation

**Exact Match:**
```
Prompt: "click the Dashboard link"
Result: ✓ Exact Match 100%
```

**Template Match:**
```
Prompt: "click Settings tab"
Result: 📋 Template Match 87%
       Matched: "click {tab_name} tab"
       Parameter: tab_name="Settings"
```

---

## Configuration

### Dataset Templates

Templates are stored in `combined-training-dataset-final.json`:

```json
{
  "prompt": "click {text} button",
  "metadata": {
    "entry_type": "template",
    "usage": "parameter_substitution",
    "is_universal": true
  }
}
```

### Confidence Thresholds

Default thresholds (can be adjusted):
- Exact: 1.00 (100%)
- Template: 0.85+ (85%+)
- Fuzzy: 0.70+ (70%+)
- ML: < 0.70 (fallback)

---

## Benefits

### ✅ **Precision When Needed**
- Exact matches guarantee accuracy
- Template matches provide consistency
- No guesswork for common patterns

### ✅ **Flexibility When Wanted**
- Fuzzy matching handles typos/variations
- ML inference for novel prompts
- Users not forced into specific wording

### ✅ **Transparency**
- Shows which strategy was used
- Displays confidence score
- Shows extracted parameters

### ✅ **No Limitations**
- Not restricted to templates only
- Conversational prompts still work
- Best of both worlds

---

## Best Practices

### 1. Use Templates for Common Patterns
```
✓ "click Login button"
✓ "click Submit button"  
✓ "click Save button"

Instead of:
✗ "click the blue button in the top right"
```

### 2. Be Specific When Possible
```
✓ "enter username in email field"

Instead of:
≈ "type stuff in the box"
```

### 3. Check Match Strategy
- Green (Exact) → Use confidently
- Blue (Template) → Verify parameters
- Orange (Fuzzy) → Test before production
- Purple (ML) → Always verify!

### 4. Add Data Values for Input Actions
```
Prompt: "enter username in login field"  
Value: "testuser@example.com"

Better than:
Prompt: "enter testuser@example.com in login field"
```

---

## Troubleshooting

### "Getting ML Inference when I expect Template Match"

**Problem:** Your prompt doesn't match template pattern exactly

**Solution:**
```
Template: "click {text} button"

✓ Works: "click Login button"
✓ Works: "click the Submit button"
✗ Doesn't work: "click on the Login button please"

Fix: Remove extra words to match template pattern
```

### "Fuzzy Match Seems Wrong"

**Problem:** Similar wording but different intent

**Solution:**
- Use exact wording from dataset, OR
- Use template pattern, OR
- Add new exact entry to dataset

### "Want to Add New Template"

**Steps:**
1. Add to `combined-training-dataset-final.json`
2. Include `{placeholder}` for variable parts
3. Set `entry_type: "template"`
4. Restart server to reload dataset

**Example:**
```json
{
  "prompt": "select {option} from {dropdown}",
  "code": "new Select(driver.findElement(By.name(\"{DROPDOWN}\"))).selectByVisibleText(\"{OPTION}\");",
  "xpath": "By.name(\"{DROPDOWN}\")",
  "metadata": {
    "entry_type": "template",
    "usage": "parameter_substitution"
  }
}
```

---

## Technical Details

### Implementation Files

1. **`intelligent_prompt_matcher.py`** - Core matching engine
   - Exact matching with indexed lookup
   - Template pattern matching with regex
   - Fuzzy matching with SequenceMatcher
   - Confidence scoring

2. **`api_server_modular.py`** - API integration
   - Uses matcher in `/add-prompt` endpoint
   - Returns match strategy and confidence
   - Falls back to ML if no match

3. **`test-builder.js`** - Frontend display
   - Shows match strategy badge
   - Displays confidence percentage
   - Color-coded visual feedback

### Performance

- **Exact Match:** < 1ms (hash lookup)
- **Template Match:** 1-5ms (regex matching)
- **Fuzzy Match:** 10-50ms (all entries)
- **ML Inference:** 100-500ms (neural network)

### Memory Usage

- Dataset loaded once at startup
- Indexed for fast lookups
- ~10MB for 19,000+ entries

---

## Future Enhancements

### 1. 🔮 User Feedback Loop
```
User sees: ≈ Similar Match 78%
User clicks: "This is correct" ✓
System learns: Adds as exact match variant
```

### 2. 🔮 Custom Templates Per Project
```
Add project-specific templates:
"click {text} in sidebar menu"
"expand {section} accordion"
```

### 3. 🔮 Multi-Language Support
```
Template: "click {text} button"
Languages: Python, Java, JavaScript, C#
Auto-generate code for selected language
```

### 4. 🔮 Context-Aware Matching
```
Previous step: "navigate to login page"
Current step: "click login"
Context: Prioritize login button matches
```

---

## Summary

✅ **Multi-strategy matching** - Tries 4 different approaches  
✅ **No limitations** - Templates AND conversational prompts work  
✅ **Visual feedback** - See strategy and confidence  
✅ **Parameter extraction** - Automatic for templates  
✅ **High accuracy** - Exact/template matches are reliable  
✅ **Flexible fallback** - ML handles novel prompts  

**Result:** Best of both worlds - precision when you want it, flexibility when you need it!

---

**Status:** Production Ready ✅
