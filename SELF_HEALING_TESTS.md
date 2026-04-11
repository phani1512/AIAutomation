# Self-Healing Test Automation - Fallback Locators

## Overview

The system now supports **self-healing test automation** that automatically tries alternative locators if the primary one fails during test execution. This makes tests more resilient to UI changes.

## How It Works

### Traditional Approach (Without Fallbacks)
```java
// If this fails, test fails immediately
WebElement element = driver.findElement(By.id("loginBtn"));
element.click();
```

### Self-Healing Approach (With Fallbacks)
```java
// Tries multiple locators automatically
WebElement element = null;
try {
    // Primary locator (100% confidence)
    element = driver.findElement(By.id("loginBtn"));
    System.out.println("Element found using: Primary locator");
} catch (NoSuchElementException e) {
    try {
        // Fallback #1 (85% confidence)
        element = driver.findElement(By.xpath("//button[text()='Login']"));
        System.out.println("Element found using: Fallback #1");
    } catch (NoSuchElementException e2) {
        // Fallback #2 (

75% confidence)
        element = driver.findElement(By.cssSelector("button.login-btn"));
        System.out.println("Element found using: Fallback #2");
    }
}
element.click();
```

## Features

### 1. **Automatic Fallback Selection**
- System analyzes similar prompts in the dataset
- Finds up to 3 alternative locators for the same action
- Ranks them by confidence score

### 2. **Multi-Language Support**
- **Java**: Full try-catch with WebDriverWait
- **Python**: Exception handling with fallback logic
- **JavaScript**: Coming soon
- **C#**: Coming soon

### 3. **Intelligent Matching**
For prompt: `"click login button"`

The system finds:
1. **Primary**: `By.id("loginBtn")` - 100% confidence (exact dataset match)
2. **Fallback #1**: `By.xpath("//button[contains(text(),'Login')]")` - 85% confidence
3. **Fallback #2**: `By.cssSelector("button.btn-login")` - 75% confidence

### 4. **Execution Logging**
Generated code logs which locator worked:
```
Element found using: Locator 1: By.id("loginBtn")
```

If primary fails:
```
Primary locator failed, trying fallbacks...
Element found using: Locator 2: By.xpath("//button[text()='Login']")
```

## Usage

### API Endpoint

**POST** `/generate`

```json
{
  "prompt": "click login button",
  "language": "java",
  "with_fallbacks": true,
  "max_fallbacks": 3
}
```

**Parameters:**
- `prompt`: Your test instruction
- `language`: Target language (java, python, javascript, csharp)
- `with_fallbacks`: Enable self-healing (default: `true`)
- `max_fallbacks`: Max number of fallback locators (default: 3, max: 5)

**Response:**
```json
{
  "generated": "// Self-healing code with fallbacks...",
  "has_fallbacks": true,
  "fallback_count": 3,
  "alternatives": [
    {
      "prompt": "press login button",
      "score": 0.85,
      "code": "...",
      "strategy": "fuzzy_fallback"
    }
  ]
}
```

### Python Example

```python
import requests

response = requests.post('http://localhost:5002/generate', json={
    "prompt": "enter username in input field",
    "language": "python",
    "with_fallbacks": True,
    "max_fallbacks": 3
})

code = response.json()['generated']
print(code)
```

### Frontend Usage

In the Generate Code page, fallbacks are enabled by default. The system:
1. Generates code with try-catch fallback logic
2. Shows alternatives in the "Did you mean?" modal
3. Logs which locator worked during execution

To disable fallbacks (use simple code):
```javascript
const response = await fetch('/generate', {
  method: 'POST',
  body: JSON.stringify({
    prompt: userPrompt,
    language: 'java',
    with_fallbacks: false  // Disable self-healing
  })
});
```

## Benefits

### 1. **Reduced Test Maintenance**
If developers change:
- Button ID from `loginBtn` → `login_button`
- Test still works! Fallback uses text-based locator

### 2. **Better Debugging**
Logs show exactly which locator worked:
```
Test execution log:
  ✓ Step 1: Element found using Locator 2
  ✓ Step 2: Element found using Locator 1
  ✗ Step 3: All fallback locators failed
```

### 3. **Higher Test Success Rate**
Tests adapt to:
- ID changes
- CSS class changes
- Text changes (uses multiple strategies)

### 4. **Dataset-Driven Intelligence**
Fallbacks come from your training dataset:
- No random guessing
- Based on similar real-world examples
- Confidence scores for each option

## Configuration

### Enable/Disable Globally

In `api_server_modular.py`:
```python
@app.route('/generate', methods=['POST'])
def generate_code():
    data = request.get_json()
    
    # Change default here
    with_fallbacks = data.get('with_fallbacks', True)  # True = enabled by default
```

### Adjust Fallback Count

```json
{
  "prompt": "click submit button",
  "max_fallbacks": 5  // Try up to 5 alternative locators
}
```

### Confidence Thresholds

In `intelligent_prompt_matcher.py`:
```python
def match_with_fallbacks(self, user_prompt: str, max_fallbacks: int = 3):
    # Adjust these thresholds
    if similarity >= 0.70:  # Exact alternatives
        fallbacks.append(...)
    
    if 0.60 <= similarity < 0.70:  # Fuzzy fallbacks
        fallbacks.append(...)
```

## Testing

Run the test suite:
```bash
python test_fallback_generation.py
```

This tests:
1. ✅ Java code with fallbacks
2. ✅ Python code with fallbacks
3. ✅ Standard generation without fallbacks
4. ✅ Alternative locator discovery
5. ✅ Confidence scoring

## Example Output

### Prompt: "click login button"

**Generated Code:**
```java
// Self-healing element finder with fallback locators
WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
WebElement element = null;
String usedLocator = null;

// Primary locator (confidence: 100%)
// Matched from: "click login button"
try {
    element = wait.until(ExpectedConditions.elementToBeClickable(By.id("loginBtn")));
    usedLocator = "Locator 1: By.id(\"loginBtn\")";
} catch (TimeoutException | NoSuchElementException e) {
    System.out.println("Primary locator failed, trying fallbacks...");
}

// Fallback #1 (confidence: 85%)
// Matched from: "press login button"
if (element == null) {
    try {
        element = wait.until(ExpectedConditions.elementToBeClickable(By.xpath("//button[contains(text(),'Login')]")));
        usedLocator = "Locator 2: By.xpath(\"//button[contains(text(),'Login')]\")";
    } catch (TimeoutException | NoSuchElementException e) {
        // Continue to next fallback
    }
}

// Fallback #2 (confidence: 75%)
// Matched from: "tap login button"
if (element == null) {
    try {
        element = wait.until(ExpectedConditions.elementToBeClickable(By.cssSelector("button.btn-login")));
        usedLocator = "Locator 3: By.cssSelector(\"button.btn-login\")";
    } catch (TimeoutException | NoSuchElementException e) {
        // Continue to next fallback
    }
}

// Verify element was found
if (element == null) {
    throw new NoSuchElementException("All fallback locators failed");
}

System.out.println("Element found using: " + usedLocator);

element.click();
```

## Advanced Features

### Custom Fallback Strategies

Extend `FallbackCodeGenerator` to add custom logic:
```python
class FallbackCodeGenerator:
    def _generate_java_fallback(self, locators, action, primary_match):
        # Add your custom fallback logic
        # Example: Try shadow DOM locators
        # Example: Try iframe switching
        pass
```

### Fallback Analytics

Track which locators work in production:
```java
// Add to your test framework
logger.info("Locator success: " + usedLocator);
metrics.recordLocatorUsage(usedLocator);
```

### A/B Testing Locators

Compare fallback strategies:
```python
{
    "with_fallbacks": True,
    "fallback_strategy": "conservative"  # Only high-confidence fallbacks
}

{
    "with_fallbacks": True,
    "fallback_strategy": "aggressive"  # Try more fallbacks
}
```

## Troubleshooting

### Issue: All fallbacks fail

**Solution 1**: Increase max_fallbacks
```json
{"max_fallbacks": 5}
```

**Solution 2**: Lower confidence threshold
```python
# In intelligent_prompt_matcher.py
if similarity >= 0.50:  # Lower from 0.70
```

**Solution 3**: Add more dataset examples
- Add variations to `combined-training-dataset-final.json`
- More examples = better fallback discovery

### Issue: Wrong fallback selected

**Solution**: Check confidence scores
```python
alternatives = response['alternatives']
for alt in alternatives:
    print(f"{alt['strategy']}: {alt['score']:.2%}")
```

Adjust confidence thresholds if needed.

### Issue: Performance (code too verbose)

**Solution**: Disable fallbacks for simple tests
```json
{"with_fallbacks": false}
```

Or reduce fallback count:
```json
{"max_fallbacks": 1}
```

## Future Enhancements

### Planned Features
- [ ] JavaScript/TypeScript fallback generation
- [ ] C# fallback generation
- [ ] Machine learning for fallback ranking
- [ ] Runtime fallback learning (adapt from failures)
- [ ] Visual fallback (use screenshot similarity)
- [ ] Fallback analytics dashboard

### Experimental Features
- Shadow DOM fallback strategies
- iFrame auto-switching
- Custom element fallback
- AI-powered locator healing

## References

- **FallbackCodeGenerator**: `src/main/python/fallback_code_generator.py`
- **IntelligentPromptMatcher**: `src/main/python/intelligent_prompt_matcher.py`
- **API Endpoint**: `src/main/python/api_server_modular.py` - `/generate`
- **Test Suite**: `test_fallback_generation.py`

## Summary

Self-healing tests with fallback locators provide:
✅ **Resilience** - Tests adapt to UI changes  
✅ **Debugging** - Know which locator worked  
✅ **Intelligence** - Dataset-driven fallback selection  
✅ **Flexibility** - Enable/disable per test  
✅ **Performance** - Try-catch adds minimal overhead  

**Enable by default** for production tests!
