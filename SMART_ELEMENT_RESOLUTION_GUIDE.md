# Smart Element Resolution - How It Works

## 🎯 The Problem You Identified

**Before:** Dataset had hard-coded element names
```json
{
  "prompt": "click the sign in button",
  "locator": "By.cssSelector('[Label=\"Sign In\"]')"
}
```

**Issue:** Only works for that ONE specific button. Not flexible.

---

## ✨ The Solution: 3-Part System

### **Part 1: Generic Dataset with Placeholders**

```json
{
  "prompt": "click <element> button",
  "locator": "By.id('<element-id>')",
  "is_generic": true
}
```

This teaches the model the **pattern** of clicking, not a specific button.

---

### **Part 2: Element Resolver (Auto-Discovery)**

When you say: `"click loginButton"`

The system:
1. **Extracts** element name: `loginButton`
2. **Searches** the page using multiple strategies:
   - ✅ ID = "loginButton" or "login-button"
   - ✅ Name attribute = "loginButton"  
   - ✅ Data-testid = "loginButton"
   - ✅ Aria-label contains "login button"
   - ✅ Class contains "login-button"
   - ✅ Text content = "Login Button"
   - ✅ Fuzzy match across all interactive elements

3. **Returns** actual locator: `By.ID("login-button")`

---

### **Part 3: Smart Code Generation**

Combines the generic pattern + discovered locator:

```python
# Original prompt: "click loginButton"
# Discovered locator: By.ID("login-button")

# Generated code:
elem_loginButton = driver.find_element(By.ID, "login-button")
# Scroll into view
driver.execute_script("arguments[0].scrollIntoView({behavior: 'auto', block: 'center'});", elem_loginButton)
time.sleep(0.5)
elem_loginButton.click()
```

---

## 🚀 How To Use

### **Method 1: Direct Prompts (Recommended)**

```python
from smart_prompt_handler import SmartPromptHandler
from browser_executor import BrowserExecutor

# Initialize
browser = BrowserExecutor()
handler = SmartPromptHandler(browser)

# Open page
result = handler.process_prompt("click loginButton", url="https://example.com")

# Use generated code
if result['success']:
    print(result['code'])  # Working Selenium code!
    exec(result['code'])   # Or execute directly
```

### **Method 2: Via API**

```bash
# Start server
python src/main/python/api_server_modular.py

# Send request
curl -X POST http://localhost:5002/generate-smart \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "click loginButton", 
    "url": "https://example.com"
  }'
```

Response:
```json
{
  "code": "elem_loginButton = driver.find_element(By.ID, 'login-button')...",
  "resolved_element": {
    "name": "loginButton", 
    "locator_type": "By.ID",
    "locator_value": "login-button"
  },
  "success": true
}
```

---

## 📝 Supported Prompt Patterns

### **Clicking**
```
click loginButton          → Finds and clicks login button
click submitBtn            → Finds and clicks submit button  
click cancelLink           → Finds and clicks cancel link
```

### **Entering Text**
```
enter testuser in username       → Finds username field, types "testuser"
type secret_sauce in password    → Finds password field, types "secret_sauce"
input john@example.com in email  → Finds email field, types email
```

### **Verification**
```
verify errorMessage is displayed  → Checks if error message visible
check submitButton is enabled     → Checks if button is enabled
assert usernameField is present   → Checks if field exists
```

### **Getting Text**
```
get text from welcomeMessage  → Retrieves text from welcome banner
retrieve value from totalPrice → Gets price text
```

### **Selecting**
```
select "California" from stateDropdown  → Selects California from dropdown
```

### **Waiting**
```
wait for loadingSpinner  → Waits for spinner to appear
```

---

## 🔍 Element Naming Conventions

The resolver is **smart** and handles multiple formats:

### **camelCase** (Recommended)
```
loginButton, usernameField, submitBtn, errorMessage
```

### **kebab-case**
```
login-button, username-field, submit-btn, error-message
```

### **Natural Names**
```
"Sign In" button → Finds button with text "Sign In"
"Username" field → Finds field with label/placeholder "Username"
```

---

## 🎯 Real-World Example

### **Sircon Login Test**

```python
# Traditional way (hard-coded)
driver.find_element(By.ID, "producer-email").send_keys("test@example.com")
driver.find_element(By.ID, "producer-password").send_keys("password123")
driver.find_element(By.XPATH, "//button[@id='producer-login-btn']").click()
```

### **Smart way (natural language)**

```python
handler.process_prompt("enter test@example.com in producerEmail", url="https://sircon.com")
handler.process_prompt("enter password123 in producerPassword")
handler.process_prompt("click producerLoginBtn")
```

**Benefits:**
- ✅ No need to inspect elements
- ✅ Works even if IDs change (uses fuzzy matching)
- ✅ More readable
- ✅ Easier to maintain

---

## 🔧 Integration with Existing Code

### **Option 1: Enhance `/generate` endpoint**

```python
# In api_server_modular.py

from smart_prompt_handler import SmartPromptHandler

# Add new endpoint
@app.route('/generate-smart', methods=['POST'])
def generate_smart():
    """Generate code with automatic element resolution."""
    data = request.json
    prompt = data.get('prompt', '')
    url = data.get('url', '')
    
    handler = SmartPromptHandler(browser_executor)
    result = handler.process_prompt(prompt, url)
    
    return jsonify(result)
```

### **Option 2: Use in Test Recorder**

```javascript
// In test-recorder.js

async function generateCodeFromAction(action) {
    const response = await fetch(`${API_URL}/generate-smart`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            prompt: `${action.type} ${action.element.name}`,
            url: window.location.href
        })
    });
    
    const result = await response.json();
    return result.code;
}
```

---

## 📊 Enhanced Dataset Format

The enhanced dataset now includes:

### **1. Specific Entries** (for common patterns)
```json
{
  "prompt": "click the sign in button",
  "locator": "By.cssSelector('[Label=\"Sign In\"]')",
  "action": "click"
}
```

### **2. Generic Entries** (for flexibility)
```json
{
  "prompt": "click <element> button",
  "locator": "By.id('<element-id>')",
  "action": "click",
  "is_generic": true
}
```

Training with **both** teaches the model:
- **Specific patterns** → Fast recognition for common cases
- **Generic patterns** → Flexibility for any element

---

## 🎉 Summary

### **What Changed:**

**Before:**
1. User records action
2. System generates code with hard-coded locator
3. Code only works for that specific element

**Now:**
1. User says "click loginButton"
2. System discovers element on page
3. Generates working code with actual locator
4. Works for ANY element, ANY page!

### **Key Benefits:**

✅ **No manual element inspection** - System finds elements automatically  
✅ **Works across pages** - Same prompt works on different sites  
✅ **Robust** - Uses 8 different search strategies  
✅ **Smart caching** - Remembers found elements  
✅ **Natural language** - Write tests like you speak  
✅ **Flexible** - Handles camelCase, kebab-case, natural names  

---

## 🔮 Next Steps

1. **Test the Element Resolver:**
   ```bash
   python src/main/python/element_resolver.py
   ```

2. **Try Smart Prompt Handler:**
   ```bash
   python src/main/python/smart_prompt_handler.py
   ```

3. **Integrate into API:**
   - Add `/generate-smart` endpoint
   - Use in Test Recorder
   - Update frontend to use smart generation

4. **Train model with enhanced dataset:**
   ```bash
   python train_model.py --dataset src/resources/sircon_ui_dataset_enhanced.json
   ```

---

## 💡 Pro Tips

### **Tip 1: Use semantic element IDs**
```html
<button id="loginButton">Login</button>  <!-- ✅ Easy to resolve -->
<button id="btn_1">Login</button>        <!-- ❌ Hard to resolve -->
```

### **Tip 2: Add data-testid for reliability**
```html
<button data-testid="loginButton">Login</button>
```

### **Tip 3: Use consistent naming**
```
loginButton, submitButton, cancelButton  (camelCase)
login-button, submit-button, cancel-button  (kebab-case)
```

### **Tip 4: Descriptive aria-labels**
```html
<button aria-label="Login to account">Login</button>
```

---

**You're now ready to use natural language for test automation! 🚀**
