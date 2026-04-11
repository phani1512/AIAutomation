# 🎯 Using Your Own Data - Quick Guide

## ✅ IMPORTANT: No Hardcoding in the System!

The Phase 0 system is **100% user-configurable**. The hardcoded values you saw were **only in the demo script** as examples. 

**You can use ANY:**
- URLs (your company apps, staging environments, production)
- Test names and descriptions
- Prompts in natural language
- Test data (usernames, passwords, form values)
- Tags and priorities

---

## 🚀 Method 1: Interactive Demo (Recommended)

Run the updated demo in **Interactive Mode**:

```bash
python test_phase0.py
```

**You'll be prompted for:**
1. Test name (e.g., "My Company CRM Login")
2. Test description
3. Each test step with your own prompts
4. URLs for navigation steps
5. Tags (e.g., "regression,critical,crm")
6. Priority level

**Example Session:**
```
Choose mode:
  1. Interactive mode (enter your own URLs, prompts, test data)
  2. Example mode (use pre-configured Saucedemo example)

Choice [1]: 1

Test name: My Company CRM Login Test
Test description: Verify login functionality with valid credentials

Step 1 prompt: Navigate to our CRM login page
  URL: https://crm.mycompany.com/login

Step 2 prompt: Type john.doe@mycompany.com in email field

Step 3 prompt: Enter MyP@ssword123 in the password field

Step 4 prompt: Click the sign in button

Step 5 prompt: Verify dashboard is displayed

Step 6 prompt: (press Enter to finish)

Tags: crm,login,smoke,regression
Priority: high
```

---

## 🔧 Method 2: Direct API Calls (Your Own Scripts)

Use the API with **your own data**:

### **Step-by-Step Example:**

```bash
# 1. Create session with YOUR test name
curl -X POST http://localhost:5002/test-suite/session/start \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Insurance Portal - Policy Creation",
    "description": "Create new auto insurance policy"
  }'

# Response: {"success": true, "session": {"session_id": "abc-123", ...}}

# 2. Add YOUR application URL
curl -X POST http://localhost:5002/test-suite/session/abc-123/add-prompt \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Go to the new policy page",
    "url": "https://portal.insurance.com/policies/new"
  }'

# 3. Add prompts with YOUR test data
curl -X POST http://localhost:5002/test-suite/session/abc-123/add-prompt \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Select Auto Insurance from policy type dropdown"
  }'

curl -X POST http://localhost:5002/test-suite/session/abc-123/add-prompt \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Enter VIN number ABC123XYZ456789 in the vehicle identification field"
  }'

curl -X POST http://localhost:5002/test-suite/session/abc-123/add-prompt \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Type 2025 in model year"
  }'

curl -X POST http://localhost:5002/test-suite/session/abc-123/add-prompt \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Click Calculate Premium button"
  }'

# 4. Save with YOUR tags
curl -X POST http://localhost:5002/test-suite/session/abc-123/save \
  -H "Content-Type: application/json" \
  -d '{
    "tags": ["insurance", "policy", "auto", "critical"],
    "priority": "critical"
  }'

# 5. Execute YOUR test
curl -X POST http://localhost:5002/test-suite/execute/TC001 \
  -H "Content-Type: application/json" \
  -d '{"headless": false}'
```

---

## 🐍 Method 3: Python Script (Your Own Automation)

Create your own script with **your application data**:

```python
import requests

BASE_URL = "http://localhost:5002"

# Your test configuration
MY_TEST_CONFIG = {
    "name": "Banking App - Fund Transfer",
    "description": "Transfer funds between accounts",
    "url": "https://banking.mybank.com/transfer",
    "prompts": [
        "Navigate to fund transfer page",
        "Select checking account from source dropdown",
        "Select savings account from destination dropdown", 
        "Enter amount 500.00 in transfer amount field",
        "Type Test transfer in description field",
        "Click the Transfer button",
        "Verify success message is displayed"
    ],
    "tags": ["banking", "transfer", "smoke"],
    "priority": "high"
}

# Create session
response = requests.post(f"{BASE_URL}/test-suite/session/start", json={
    "name": MY_TEST_CONFIG["name"],
    "description": MY_TEST_CONFIG["description"]
})
session_id = response.json()['session']['session_id']

# Add your prompts
for i, prompt_text in enumerate(MY_TEST_CONFIG["prompts"]):
    prompt_data = {"prompt": prompt_text}
    if i == 0:  # First step gets the URL
        prompt_data["url"] = MY_TEST_CONFIG["url"]
    
    response = requests.post(
        f"{BASE_URL}/test-suite/session/{session_id}/add-prompt",
        json=prompt_data
    )
    print(f"✅ Added step {i+1}: {prompt_text}")

# Save as test case
response = requests.post(
    f"{BASE_URL}/test-suite/session/{session_id}/save",
    json={
        "tags": MY_TEST_CONFIG["tags"],
        "priority": MY_TEST_CONFIG["priority"]
    }
)
test_case_id = response.json()['test_case']['test_case_id']
print(f"\n✅ Test case created: {test_case_id}")

# Execute your test
response = requests.post(
    f"{BASE_URL}/test-suite/execute/{test_case_id}",
    json={"headless": False}
)
result = response.json()['result']
print(f"\n✅ Execution: {result['status']}")
print(f"   Duration: {result['duration']:.2f}s")
```

---

## 🎯 Real-World Examples

### **E-Commerce Application:**
```python
{
  "name": "Product Purchase Flow",
  "url": "https://shop.mystore.com",
  "prompts": [
    "Navigate to products page",
    "Search for wireless headphones in search box",
    "Click on first product in results",
    "Select Black from color dropdown",
    "Click Add to Cart button",
    "Click Cart icon",
    "Click Checkout button",
    "Type john@email.com in email field",
    "Enter 123 Main St in shipping address",
    "Click Place Order button"
  ]
}
```

### **Healthcare System:**
```python
{
  "name": "Patient Registration",
  "url": "https://portal.hospital.org/register",
  "prompts": [
    "Navigate to patient registration page",
    "Enter John in first name field",
    "Enter Doe in last name field",
    "Type 555-1234 in phone number",
    "Enter 01/15/1980 in date of birth",
    "Select Male from gender dropdown",
    "Type 123 Health St in address field",
    "Click Submit Registration button",
    "Verify confirmation message appears"
  ]
}
```

### **Admin Dashboard:**
```python
{
  "name": "User Management - Create User",
  "url": "https://admin.myapp.com/users/new",
  "prompts": [
    "Navigate to create new user page",
    "Type jane.smith@company.com in email field",
    "Enter Jane in first name",
    "Enter Smith in last name",
    "Select Manager from role dropdown",
    "Select Sales from department dropdown",
    "Click Create User button",
    "Verify user appears in user list"
  ]
}
```

---

## 📝 Best Practices

### **1. Use Natural Language (No Specific Format Required)**
```
✅ GOOD:
- "Click the submit button"
- "I want to type hello in the search box"
- "Please enter my password"
- "Navigate to the dashboard"

✅ ALSO GOOD:
- "submit the form"
- "search for products"
- "log in with credentials"
- "go to settings"
```

### **2. Provide URLs on Navigation Steps**
```python
# First prompt should include URL
{
  "prompt": "Navigate to login page",
  "url": "https://yourapp.com/login"  # ← Your actual URL
}

# Or if changing pages mid-test
{
  "prompt": "Go to the settings page",
  "url": "https://yourapp.com/settings"  # ← Different URL
}
```

### **3. Include Actual Test Data**
```
Instead of: "Enter username"
Use: "Enter admin@mycompany.com in username field"

Instead of: "Type password"
Use: "Type SecureP@ss123 in password field"

Instead of: "Fill form"
Use specific values: "Enter John in first name, Doe in last name, 555-1234 in phone"
```

### **4. Use Descriptive Test Names**
```
✅ GOOD:
- "User Registration - Happy Path"
- "Product Search - Filter by Category"
- "Admin Panel - Delete User Workflow"
- "Payment Processing - Credit Card"

❌ AVOID:
- "Test 1"
- "Login Test"
- "My Test"
```

### **5. Tag for Organization**
```python
{
  "tags": [
    "smoke",           # Test type
    "login",           # Feature area
    "critical",        # Priority
    "regression",      # Suite
    "authentication"   # Domain
  ],
  "priority": "high"
}
```

---

## 🔒 Sensitive Data Handling

### **Option 1: Environment Variables**
```python
import os

username = os.getenv("TEST_USERNAME", "default@test.com")
password = os.getenv("TEST_PASSWORD", "default123")

prompt = f"Enter {username} in username field"
```

### **Option 2: Config File**
```json
// test_config.json (add to .gitignore!)
{
  "test_accounts": {
    "admin": {
      "username": "admin@myapp.com",
      "password": "AdminP@ss123"
    },
    "standard_user": {
      "username": "user@myapp.com",
      "password": "UserP@ss456"
    }
  },
  "base_urls": {
    "staging": "https://staging.myapp.com",
    "production": "https://myapp.com"
  }
}
```

```python
import json

with open('test_config.json') as f:
    config = json.load(f)

username = config['test_accounts']['admin']['username']
base_url = config['base_urls']['staging']
```

### **Option 3: Vault/Secrets Manager**
```python
# Use HashiCorp Vault, AWS Secrets Manager, etc.
from vault_client import get_secret

credentials = get_secret("test/credentials/admin")
username = credentials['username']
password = credentials['password']
```

---

## ✅ Summary

**Phase 0 System = 100% User-Configurable**

| Component | User-Customizable? | How to Customize |
|-----------|-------------------|------------------|
| URLs | ✅ YES | Add `"url"` to any prompt |
| Prompts | ✅ YES | Natural language, any text |
| Test Data | ✅ YES | Include in prompt text |
| Test Names | ✅ YES | `name` field in session/start |
| Tags | ✅ YES | `tags` array when saving |
| Priority | ✅ YES | `priority` when saving |
| Languages | ✅ YES | Python/Java/JS/Cypress |
| Execution | ✅ YES | Headless true/false |

**No hardcoding required - use YOUR data!** 🎉

---

## 🚀 Next Steps

1. **Try Interactive Mode:** `python test_phase0.py` → Choose option 1
2. **Create Your First Real Test:** Use your own application
3. **Build Test Library:** Save multiple test cases for your app
4. **Execute Tests:** Run saved tests anytime with one API call
5. **Generate Reports:** Get HTML reports with screenshots

**Ready to test YOUR application with YOUR data!** 🎯
