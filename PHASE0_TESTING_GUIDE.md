# 🧪 Phase 0 Testing Guide - Where & How to Test

## 📍 Where Phase 0 is Integrated

### **1. Core Python Modules** (Backend Logic)
```
c:\Users\valaboph\AIAutomation\src\main\python\
├── test_session_manager.py          ← Session management (430 lines)
├── test_case_builder.py             ← Test case generation (550 lines)
├── test_suite_runner.py             ← Test execution (630 lines)
└── api_server_modular.py            ← API endpoints (UPDATED)
```

### **2. API Server Integration** 
**File:** [api_server_modular.py](src/main/python/api_server_modular.py)

**Lines 48-53:** Imports added
```python
# Import Phase 0 modules for multi-prompt test suite builder
from test_session_manager import get_session_manager
from test_case_builder import get_test_case_builder
from test_suite_runner import get_test_runner
from smart_prompt_handler import SmartPromptHandler
```

**Lines 733-980:** 15 new API endpoints added
```python
# ==================== Multi-Prompt Test Suite Endpoints (PHASE 0) ====================

@app.route('/test-suite/session/start', methods=['POST'])
@app.route('/test-suite/session/<session_id>/add-prompt', methods=['POST'])
@app.route('/test-suite/session/<session_id>', methods=['GET', 'DELETE'])
@app.route('/test-suite/session/<session_id>/preview', methods=['GET'])
@app.route('/test-suite/session/<session_id>/save', methods=['POST'])
@app.route('/test-suite/sessions', methods=['GET'])
@app.route('/test-suite/test-cases', methods=['GET'])
@app.route('/test-suite/test-cases/<test_case_id>', methods=['GET', 'DELETE'])
@app.route('/test-suite/execute/<test_case_id>', methods=['POST'])
@app.route('/test-suite/execute-suite', methods=['POST'])
```

### **3. Storage Directories** (Created)
```
c:\Users\valaboph\AIAutomation\src\resources\
├── test_cases\              ← Saved test cases (JSON)
├── test_sessions\           ← Session backups (JSON)
├── test_suites\             ← Test suite definitions
├── execution_results\       ← Test execution results
│   └── screenshots\         ← Test screenshots
```

### **4. Demo Script** (For Testing)
```
c:\Users\valaboph\AIAutomation\
└── test_phase0.py           ← Complete demo workflow
```

---

## 🚀 How to Test Phase 0

### **Method 1: Run the Demo Script** ⭐ EASIEST

**Step 1:** Make sure server is running
```powershell
# Check if server is up
curl http://localhost:5002/health

# If not running, start it:
python src/main/python/api_server_modular.py
```

**Step 2:** Run the demo (Interactive Mode)
```powershell
python test_phase0.py
```

**What it does:**
1. ✅ Creates a test session
2. ✅ Prompts YOU to enter your own test steps
3. ✅ Shows generated code preview
4. ✅ Saves as test case
5. ✅ Lists all test cases
6. ✅ Optionally executes the test

**Try it NOW:**
```powershell
# In your current terminal
python test_phase0.py
```

Then choose:
- **Option 1:** Interactive mode (enter YOUR URLs and prompts)
- **Option 2:** Example mode (uses Saucedemo demo)

---

### **Method 2: Test Individual Endpoints** ⭐ API TESTING

#### **Test 1: Check Available Sessions**
```powershell
curl http://localhost:5002/test-suite/sessions
```
**Expected Response:**
```json
{"count": 0, "sessions": [], "success": true}
```

#### **Test 2: Create a Session**
```powershell
curl -X POST http://localhost:5002/test-suite/session/start `
  -H "Content-Type: application/json" `
  -d '{"name": "My First Test", "description": "Testing Phase 0"}'
```
**Expected Response:**
```json
{
  "success": true,
  "session": {
    "session_id": "abc-123-xyz",
    "name": "My First Test",
    "description": "Testing Phase 0",
    "prompt_count": 0,
    "created_at": "2026-03-16T..."
  }
}
```

**⚠️ Save the `session_id` - you'll need it for next steps!**

#### **Test 3: Add a Prompt to Session**
```powershell
# Replace {SESSION_ID} with the actual ID from Test 2
curl -X POST http://localhost:5002/test-suite/session/{SESSION_ID}/add-prompt `
  -H "Content-Type: application/json" `
  -d '{"prompt": "Click the login button", "url": "https://example.com"}'
```
**Expected Response:**
```json
{
  "success": true,
  "step_number": 1,
  "step_result": {
    "prompt": "Click the login button",
    "url": "https://example.com",
    "parsed": {
      "action": "click",
      "element": "login",
      "value": null
    },
    "resolved_element": { ... },
    "generated_code": "driver.find_element..."
  }
}
```

#### **Test 4: Preview Generated Code**
```powershell
# Replace {SESSION_ID} with your session ID
curl "http://localhost:5002/test-suite/session/{SESSION_ID}/preview?language=python"
```
**Expected Response:**
```json
{
  "success": true,
  "code": "# Auto-generated test case\nfrom selenium import webdriver...",
  "language": "python",
  "prompt_count": 1
}
```

#### **Test 5: Save as Test Case**
```powershell
curl -X POST http://localhost:5002/test-suite/session/{SESSION_ID}/save `
  -H "Content-Type: application/json" `
  -d '{"tags": ["smoke"], "priority": "high"}'
```
**Expected Response:**
```json
{
  "success": true,
  "test_case": {
    "test_case_id": "TC001",
    "name": "My First Test",
    "step_count": 1,
    "tags": ["smoke"],
    "priority": "high"
  },
  "filepath": "C:\\Users\\...\\test_cases\\TC001_My_First_Test.json"
}
```

#### **Test 6: List All Test Cases**
```powershell
curl http://localhost:5002/test-suite/test-cases
```
**Expected Response:**
```json
{
  "success": true,
  "count": 1,
  "test_cases": [
    {
      "test_case_id": "TC001",
      "name": "My First Test",
      "step_count": 1,
      "tags": ["smoke"],
      "priority": "high",
      "status": "active"
    }
  ]
}
```

#### **Test 7: Execute Test Case**
```powershell
curl -X POST http://localhost:5002/test-suite/execute/TC001 `
  -H "Content-Type: application/json" `
  -d '{"headless": false}'
```
**Expected Response:**
```json
{
  "success": true,
  "result": {
    "test_case_id": "TC001",
    "status": "passed",
    "duration": 5.23,
    "steps": [
      {"step": 1, "status": "passed", "duration": 2.1}
    ],
    "screenshots": [
      {"filepath": "...", "description": "Step 1"}
    ]
  }
}
```

---

### **Method 3: Python Script Testing** ⭐ PROGRAMMATIC

Create a test script `my_test.py`:

```python
import requests
import json

BASE_URL = "http://localhost:5002"

# 1. Create session
response = requests.post(f"{BASE_URL}/test-suite/session/start", json={
    "name": "Quick Test",
    "description": "Testing Phase 0 integration"
})
session_id = response.json()['session']['session_id']
print(f"✅ Created session: {session_id}")

# 2. Add prompts with YOUR data
prompts = [
    {"prompt": "Navigate to google.com", "url": "https://google.com"},
    {"prompt": "Type test automation in search box"},
    {"prompt": "Click the search button"}
]

for i, prompt_data in enumerate(prompts, 1):
    response = requests.post(
        f"{BASE_URL}/test-suite/session/{session_id}/add-prompt",
        json=prompt_data
    )
    print(f"✅ Added step {i}: {prompt_data['prompt']}")

# 3. Preview code
response = requests.get(
    f"{BASE_URL}/test-suite/session/{session_id}/preview",
    params={"language": "python"}
)
print(f"\n📄 Generated Code:\n{response.json()['code'][:200]}...")

# 4. Save as test case
response = requests.post(
    f"{BASE_URL}/test-suite/session/{session_id}/save",
    json={"tags": ["demo", "google"], "priority": "medium"}
)
test_case_id = response.json()['test_case']['test_case_id']
print(f"\n✅ Saved as: {test_case_id}")

# 5. List all test cases
response = requests.get(f"{BASE_URL}/test-suite/test-cases")
print(f"\n📋 Total test cases: {response.json()['count']}")

print("\n✅ All tests passed!")
```

**Run it:**
```powershell
python my_test.py
```

---

## 🎯 Quick Test Scenarios

### **Scenario 1: Login Test (3 minutes)**

```powershell
# 1. Create session
$session = (curl -X POST http://localhost:5002/test-suite/session/start `
  -H "Content-Type: application/json" `
  -d '{"name": "Login Test"}' | ConvertFrom-Json)
$id = $session.session.session_id

# 2. Add login steps
curl -X POST "http://localhost:5002/test-suite/session/$id/add-prompt" `
  -H "Content-Type: application/json" `
  -d '{"prompt": "Navigate to login page", "url": "https://yourapp.com/login"}'

curl -X POST "http://localhost:5002/test-suite/session/$id/add-prompt" `
  -H "Content-Type: application/json" `
  -d '{"prompt": "Enter username admin@test.com"}'

curl -X POST "http://localhost:5002/test-suite/session/$id/add-prompt" `
  -H "Content-Type: application/json" `
  -d '{"prompt": "Enter password Test123!"}'

curl -X POST "http://localhost:5002/test-suite/session/$id/add-prompt" `
  -H "Content-Type: application/json" `
  -d '{"prompt": "Click login button"}'

# 3. Save
curl -X POST "http://localhost:5002/test-suite/session/$id/save" `
  -H "Content-Type: application/json" `
  -d '{"tags": ["login", "smoke"], "priority": "high"}'

Write-Host "✅ Login test created! Check: curl http://localhost:5002/test-suite/test-cases"
```

---

### **Scenario 2: Form Submission Test (5 minutes)**

```powershell
# Use the demo script with YOUR data
python test_phase0.py

# When prompted:
# Test name: Contact Form Submission
# 
# Step 1: Navigate to contact form
# URL: https://yoursite.com/contact
#
# Step 2: Enter name John Doe in name field
# Step 3: Enter email john@test.com in email field
# Step 4: Enter message Test message in message box
# Step 5: Click submit button
# Step 6: (press Enter to finish)
#
# Tags: contact, smoke
# Priority: medium
```

---

## 📊 Verify Integration

### **Check if Phase 0 Endpoints are Live**

Run this PowerShell script to test all endpoints:

```powershell
Write-Host "`n🧪 Testing Phase 0 Integration...`n" -ForegroundColor Cyan

# Test 1: Health Check
Write-Host "Test 1: Server Health" -ForegroundColor Yellow
curl http://localhost:5002/health 2>&1 | Select-String "healthy"

# Test 2: List Sessions (should be empty initially)
Write-Host "`nTest 2: List Sessions" -ForegroundColor Yellow
curl http://localhost:5002/test-suite/sessions 2>&1 | Select-String "success"

# Test 3: Create Session
Write-Host "`nTest 3: Create Session" -ForegroundColor Yellow
$response = curl -X POST http://localhost:5002/test-suite/session/start `
  -H "Content-Type: application/json" `
  -d '{"name": "Integration Test"}' 2>&1
$response | Select-String "session_id"

# Test 4: List Test Cases
Write-Host "`nTest 4: List Test Cases" -ForegroundColor Yellow
curl http://localhost:5002/test-suite/test-cases 2>&1 | Select-String "success"

Write-Host "`n✅ All endpoints responding!`n" -ForegroundColor Green
```

**Save as:** `test_integration.ps1`
**Run:** `.\test_integration.ps1`

---

## 🔍 Where to Find Results

### **1. Test Cases** (Saved JSON files)
```
c:\Users\valaboph\AIAutomation\src\resources\test_cases\
├── TC001_Login_Test.json
├── TC002_Contact_Form.json
└── TC003_...
```

**View a test case:**
```powershell
Get-Content src\resources\test_cases\TC001*.json | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

### **2. Execution Results** (Run history)
```
c:\Users\valaboph\AIAutomation\src\resources\execution_results\
├── TC001_result_2026-03-16_10-30-45.json
└── screenshots\
    ├── TC001_step_1_2026-03-16_10-30-46.png
    └── TC001_step_2_2026-03-16_10-30-48.png
```

**View execution result:**
```powershell
Get-Content src\resources\execution_results\TC001*.json | ConvertFrom-Json
```

### **3. Server Logs** (Real-time)
Watch server console output while testing - you'll see:
```
[INFO] Session created: abc-123
[INFO] Added prompt to session abc-123
[INFO] Test case TC001 saved
[INFO] Executing test case TC001
[INFO] Test execution completed: passed
```

---

## ✅ Checklist: Confirm Integration Working

- [ ] Server responds to `/health` endpoint
- [ ] Can create session via `/test-suite/session/start`
- [ ] Can add prompts via `/test-suite/session/{id}/add-prompt`
- [ ] Prompts are processed with NLP (action + element detected)
- [ ] Can preview generated code via `/test-suite/session/{id}/preview`
- [ ] Can save session as test case via `/test-suite/session/{id}/save`
- [ ] Test case file created in `test_cases/` directory
- [ ] Can list test cases via `/test-suite/test-cases`
- [ ] Can execute test case via `/test-suite/execute/{id}`
- [ ] Screenshots captured in `execution_results/screenshots/`
- [ ] Demo script runs without errors

---

## 🚨 Troubleshooting

### **Problem: Server not responding**
```powershell
# Check if Python process is running
Get-Process python*

# If not, start server:
python src/main/python/api_server_modular.py
```

### **Problem: 404 on Phase 0 endpoints**
```powershell
# Restart server to load new endpoints:
Stop-Process -Name python* -Force
python src/main/python/api_server_modular.py
```

### **Problem: Import errors**
```powershell
# Verify Phase 0 modules exist:
Test-Path src/main/python/test_session_manager.py
Test-Path src/main/python/test_case_builder.py
Test-Path src/main/python/test_suite_runner.py
```

---

## 🎯 Summary: Where to Test

| What | Where | How |
|------|-------|-----|
| **Complete Workflow** | `test_phase0.py` | `python test_phase0.py` |
| **Individual Endpoints** | API server | `curl http://localhost:5002/test-suite/*` |
| **Session Management** | `/test-suite/session/*` | POST, GET, DELETE |
| **Test Case Management** | `/test-suite/test-cases` | GET, DELETE |
| **Test Execution** | `/test-suite/execute/{id}` | POST |
| **Results** | `src/resources/execution_results/` | View JSON files |
| **Screenshots** | `src/resources/execution_results/screenshots/` | View PNG files |

---

## 🚀 Ready to Test!

**Run this NOW:**
```powershell
# Quick test in 30 seconds
python test_phase0.py
```

Choose **Option 1** (Interactive) and enter:
- Test name: **My First Phase 0 Test**
- Step 1: **Navigate to google.com** (URL: https://google.com)
- Step 2: **(press Enter to finish)**
- Tags: **test**
- Priority: **medium**

**You'll see:**
✅ Session created
✅ Prompt added with NLP parsing
✅ Code generated
✅ Test case saved as TC001
✅ Listed in test cases

**That's Phase 0 working!** 🎉
