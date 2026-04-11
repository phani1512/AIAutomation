# How to Add New Patterns (No Code Changes Required!)

## Method 1: Add to custom-helper-patterns.json ✅ RECOMMENDED

### Example: Adding a Calendar Date Picker Pattern

**File**: `src/resources/custom-helper-patterns.json`

```json
{
  "patterns": [
    // ... existing patterns ...
    {
      "category": "calendar_actions",
      "keywords": ["calendar", "date", "pick", "select date"],
      "method_patterns": ["selectDate", "pickDate", "setCalendarDate"],
      "xpath_template": "//input[@type='date'] | //div[contains(@class, 'datepicker')]//input",
      "action_type": "input",
      "description": "Calendar date selection actions"
    }
  ]
}
```

### Pattern Structure

| Field | Required | Description | Example |
|-------|----------|-------------|---------|
| `category` | ✅ Yes | Unique identifier | `"calendar_actions"` |
| `keywords` | ✅ Yes | Trigger words in prompts | `["calendar", "date"]` |
| `method_patterns` | ✅ Yes | Custom helper method names | `["selectDate"]` |
| `xpath_template` | ✅ Yes | XPath to find element | `"//input[@type='date']"` |
| `action_type` | ✅ Yes | Action: `click`, `input`, `select`, `verify` | `"input"` |
| `description` | ⚠️ No | Human-readable description | `"Date selection"` |

### Action Types

1. **`click`** - Button/link clicks
   ```json
   "action_type": "click",
   "xpath_template": "//button[contains(text(), '{param0}')]"
   ```

2. **`input`** - Text entry
   ```json
   "action_type": "input",
   "xpath_template": "//input[@name='{param0}']"
   ```

3. **`select`** - Dropdown selection
   ```json
   "action_type": "select",
   "xpath_template": "//select[@id='{param0}']"
   ```

4. **`verify`** - Element verification
   ```json
   "action_type": "verify",
   "xpath_template": "//div[contains(@class, '{param0}')]"
   ```

### Parameters in XPath Templates

Use `{param0}`, `{param1}`, etc. for dynamic values:

```json
{
  "xpath_template": "//button[@data-test='{param0}' and contains(text(), '{param1}')]"
}
```

This matches prompts like: "click the Submit button with data-test submit-btn"

### Testing Your New Pattern

1. **Add pattern to JSON file**
2. **Restart the server**:
   ```powershell
   Stop-Process -Name python -Force
   python src/main/python/api_server_modular.py
   ```
3. **Test with a prompt**:
   ```python
   import requests
   response = requests.post('http://localhost:5002/generate', json={
       'prompt': 'select date from calendar',
       'language': 'python'
   })
   print(response.json()['generated'])
   ```

## Method 2: Extend ComprehensiveCodeGenerator (For Complex Logic)

**File**: `src/main/python/comprehensive_code_generator.py`

### When to Use This Method:
- Complex multi-step actions
- Conditional logic required
- Special handling needed

### Example: Adding Slider Support

```python
def _parse_simple_code(self, code: str) -> dict:
    # ... existing code ...
    
    # Add slider detection
    elif 'slider' in code_lower or 'range' in code_lower:
        action = 'slider'
        value_match = re.search(r'setValue\((\d+)\)', code)
        value = value_match.group(1) if value_match else '50'
    
    # ... rest of method ...

def _generate_slider(self, locator_method: str, locator_value: str, value: str, language: str) -> str:
    """Generate comprehensive slider interaction code."""
    if language == 'python':
        by_map = {'id': 'By.ID', 'xpath': 'By.XPATH', 'cssselector': 'By.CSS_SELECTOR'}
        by_constant = by_map.get(locator_method.lower(), 'By.ID')
        return f'''# Set slider value with wait
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

wait = WebDriverWait(driver, 10)
slider = wait.until(EC.presence_of_element_located(({by_constant}, "{locator_value}")))

# Get slider dimensions
slider_width = slider.size['width']
target_position = int(slider_width * ({value} / 100))

# Move slider
actions = ActionChains(driver)
actions.click_and_hold(slider).move_by_offset(target_position, 0).release().perform()'''
    
    elif language == 'java':
        method_cap = locator_method[0].upper() + locator_method[1:]
        return f'''// Set slider value with wait
WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
WebElement slider = wait.until(ExpectedConditions.presenceOfElementLocated(By.{method_cap}("{locator_value}")));

// Get slider dimensions
int sliderWidth = slider.getSize().getWidth();
int targetPosition = (int)(sliderWidth * ({value} / 100.0));

// Move slider
Actions actions = new Actions(driver);
actions.clickAndHold(slider).moveByOffset(targetPosition, 0).release().perform();'''
    
    # ... JavaScript and C# versions ...
```

### Then Update enhance_to_comprehensive():

```python
def enhance_to_comprehensive(self, simple_code: str, prompt: str, language: str = 'java') -> str:
    parsed = self._parse_simple_code(simple_code)
    
    # ... existing code ...
    
    elif action == 'slider':
        return self._generate_slider(locator_method, locator_value, value or '50', language)
    
    # ... rest of method ...
```

## Method 3: Add to Datasets (For Specific Prompts)

**Files**: `src/resources/*.json` (dataset files)

Add exact prompt-to-code mappings:

```json
{
  "prompt": "scroll to bottom of page",
  "code": "driver.executeScript('window.scrollTo(0, document.body.scrollHeight);');",
  "locator": "",
  "action": "scroll",
  "element_type": "page"
}
```

## Best Practices

### ✅ DO:
- Use descriptive category names
- Include multiple keywords for better matching
- Test your XPath templates in browser DevTools first
- Add comments to explain complex patterns
- Use parameters (`{param0}`) for dynamic values

### ❌ DON'T:
- Use absolute XPath (fragile)
- Hardcode values in XPath
- Create duplicate patterns
- Use generic keywords that match everything

## Examples: Common Patterns

### 1. Multi-Select Dropdown
```json
{
  "category": "multiselect_actions",
  "keywords": ["multiselect", "select multiple", "choose multiple"],
  "method_patterns": ["selectMultipleOptions"],
  "xpath_template": "//select[@multiple and @id='{param0}']",
  "action_type": "select",
  "description": "Multi-select dropdown actions"
}
```

### 2. Drag and Drop
```json
{
  "category": "drag_drop_actions",
  "keywords": ["drag", "drop", "drag and drop"],
  "method_patterns": ["dragAndDrop", "dragElementTo"],
  "xpath_template": "//div[@draggable='true' and contains(text(), '{param0}')]",
  "action_type": "click",
  "description": "Drag and drop interactions"
}
```

### 3. Toggle Switch
```json
{
  "category": "toggle_actions",
  "keywords": ["toggle", "switch", "enable", "disable"],
  "method_patterns": ["toggleSwitch", "flipSwitch"],
  "xpath_template": "//input[@type='checkbox' and @role='switch']",
  "action_type": "click",
  "description": "Toggle switch actions"
}
```

### 4. Autocomplete
```json
{
  "category": "autocomplete_actions",
  "keywords": ["autocomplete", "search suggestion", "type ahead"],
  "method_patterns": ["selectFromAutocomplete"],
  "xpath_template": "//input[@role='combobox']",
  "action_type": "input",
  "description": "Autocomplete field interactions"
}
```

## Troubleshooting

### Pattern Not Matching?

1. **Check keywords**: Are they present in your test prompts?
   ```python
   # Add logging to see matching
   print(f"Prompt keywords: {prompt.lower().split()}")
   ```

2. **Test XPath**: Copy XPath to browser DevTools Console
   ```javascript
   $x("//button[contains(text(), 'Submit')]")
   ```

3. **Check method_patterns**: Does the generated code contain this method name?

4. **Verify action_type**: Is the action type correct for the operation?

### Pattern Conflicts?

Patterns are checked in order. More specific patterns should come first:

```json
{
  "patterns": [
    {
      "category": "submit_button",  // Specific
      "keywords": ["submit button"],
      // ...
    },
    {
      "category": "button_click",  // General
      "keywords": ["button"],
      // ...
    }
  ]
}
```

## Testing Checklist

- [ ] Added pattern to JSON file
- [ ] Restarted server
- [ ] Tested with sample prompt
- [ ] Verified generated code has WebDriverWait
- [ ] Tested in all languages (Java, Python, JavaScript, C#)
- [ ] Added pattern to this documentation

## Summary

**No Code Changes Required!** Just:
1. Edit `custom-helper-patterns.json`
2. Restart server
3. Test your prompts

For complex cases, extend `ComprehensiveCodeGenerator` class.
