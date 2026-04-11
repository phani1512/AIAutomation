# 🎯 Semantic Analysis Workflow - Complete Guide

**Date:** April 1, 2026  
**Status:** ✅ Production Ready  
**Mode:** On-Demand ML Training + Test Case Expansion

---

## 📊 How Semantic Analysis Works (Final Architecture)

### 🌟 Key Concept

**From 1 Test Case → Get 20-50 Complete Test Cases**

The user creates or records ONE test case, and the system generates COMPLETE, READY-TO-RUN test cases covering:
- ✅ Negative scenarios
- ✅ Boundary conditions
- ✅ Edge cases
- ✅ Security tests
- ✅ Data validation
- ✅ Compatibility tests

---

## 🔄 Complete Workflow

```
┌──────────────────────────────────────────────────────┐
│  STEP 1: User Creates Test Case                     │
│  (Builder or Recorder)                               │
└───────────────────┬──────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────────────┐
│  STEP 2: Save to test_suites/                       │
│  • test_suites/builder/{test_id}.json               │
│  • test_suites/recorded_{username}/{test_id}.json   │
└───────────────────┬──────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────────────┐
│  STEP 3: Navigate to Semantic Analysis Page         │
│  • View list of saved test cases                    │
│  • Select the test case to expand                   │
└───────────────────┬──────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────────────┐
│  STEP 4: Click "Generate Test Cases" Button         │
└───────────────────┬──────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────────────┐
│  STEP 5: ML IMMEDIATELY RETRAINS with that test     │
│  • No waiting for 50 tests                          │
│  • No time thresholds                               │
│  • Instant learning from your test                  │
└───────────────────┬──────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────────────┐
│  STEP 6: System Generates 20-50 COMPLETE Tests      │
│  • Full test case objects (not just names)          │
│  • Modified steps for each scenario                 │
│  • Test data variations                             │
│  • Priority and tags                                │
└───────────────────┬──────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────────────┐
│  STEP 7: User Reviews Generated Tests               │
│  • Checkboxes to select wanted tests               │
│  • Preview complete test details                    │
│  • Filter by priority/type                          │
└───────────────────┬──────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────────────┐
│  STEP 8: Save Selected Tests back to test_suites/   │
│  • test_suites/generated/{test_id}.json              │
│  • Now you have 10-50 complete test cases!          │
└──────────────────────────────────────────────────────┘
```

---

## 🎯 What Gets Generated

### Input: 1 Test Case

```json
{
  "test_case_id": "login_valid_001",
  "name": "Login with valid credentials",
  "steps": [
    {"prompt": "navigate to login page"},
    {"prompt": "enter username in username field"},
    {"prompt": "enter password in password field"},
    {"prompt": "click login button"}
  ]
}
```

### Output: 25+ Complete Test Cases

#### Negative Scenarios (5 tests):
1. **Login with invalid email** - Complete test with invalid email data
2. **Login with empty fields** - Complete test with empty username/password
3. **Login with SQL injection** - Complete test with SQL attack patterns
4. **Login with XSS attempt** - Complete test with XSS payload
5. **Login with wrong format** - Complete test with incorrect format

#### Boundary Conditions (5 tests):
6. **Login with minimum length password** - 1 character password
7. **Login with maximum length username** - 255 character username
8. **Login with zero value inputs** - All zeros
9. **Login with negative numbers** - Negative numbers in fields
10. **Login with large dataset** - Massive input data

#### Edge Cases (5 tests):
11. **Login with special characters** - !@#$%^&*() in fields
12. **Login with unicode** - Chinese/emoji characters
13. **Login with rapid repeated actions** - Click login 100 times
14. **Login with timeout** - Delayed responses

#### Security Tests (4 tests):
15. **Login without authentication** - Direct URL access
16. **Login with session hijacking** - Manipulated session
17. **Login with CSRF attack** - Missing CSRF token
18. **Login with privilege escalation** - Admin URL access

#### Data Validation (4 tests):
19. **Verify login response format** - Check JSON structure
20. **Verify session persistence** - Check cookie saved
21. **Verify user data retrieval** - Check profile loaded
22. **Verify redirect after login** - Check URL changed

#### Compatibility (2 tests):
23. **Login on mobile viewport** - 375px width
24. **Login on slow network** - 3G speed simulation

**Each test case includes:**
- ✅ Complete test_case_id
- ✅ Descriptive name
- ✅ Full steps array with modifications
- ✅ Test data variations
- ✅ Expected results
- ✅ Priority (critical/high/medium/low)
- ✅ Tags for filtering
- ✅ Status (draft/active)

---

## 🛠️ Technical Architecture

### Core Components

#### 1. **On-Demand Trainer** (`auto_retrainer.py`)
- **Purpose:** Retrain ML model immediately when requested
- **Replaces:** Old auto-retrain with 50 test threshold
- **Trigger:** User clicks "Generate Test Cases"

```python
# OLD (WRONG):
# Wait for 50 tests → Auto-retrain → Suggest scenarios

# NEW (CORRECT):
# User selects test → Retrain immediately → Generate complete tests
```

#### 2. **Test Case Expander** (`test_case_expander.py`)
- **Purpose:** Generate 20-50 complete test cases from 1 template
- **Input:** Source test case ID
- **Output:** Array of complete test case objects

**Expansion Types:**
- `negative` - Invalid/empty/malicious input tests
- `boundary` - Min/max/zero value tests
- `edge_case` - Special chars/unicode/rapid actions
- `security` - Unauthorized/CSRF/injection tests
- `data_validation` - Format/persistence/retrieval checks
- `compatibility` - Mobile/browser/network variations

#### 3. **API Endpoints**

**A. Expand Test Case**
```http
POST /semantic/expand-test-case

Request:
{
  "test_case_id": "login_001",
  "expansion_types": ["negative", "boundary", "security"]  // Optional
}

Response:
{
  "success": true,
  "source_test": {...},
  "generated_tests": [
    {
      "test_case_id": "negative_invalid_input_123",
      "name": "Login - Test with invalid input data",
      "steps": [...],  // Complete modified steps
      "test_data": {...},
      "priority": "high",
      "tags": ["negative", "invalid_input", "expanded"]
    },
    // ... 24 more complete tests
  ],
  "total_generated": 25,
  "ml_retrained": true
}
```

**B. Save Expanded Tests**
```http
POST /semantic/save-expanded-tests

Request:
{
  "test_cases": [
    {...},  // Complete test case objects
    {...},
    {...}
  ],
  "suite_name": "generated"  // Optional
}

Response:
{
  "success": true,
  "saved_count": 10,
  "suite_name": "generated"
}
```

**C. Manual Training**
```http
POST /ml/trigger-training

Response:
{
  "success": true,
  "results": {
    "f1_score": 0.92,
    "accuracy": 0.89
  }
}
```

**D. Training Status**
```http
GET /ml/training-status

Response:
{
  "success": true,
  "has_trained": true,
  "last_training": {
    "timestamp": "2026-04-01T10:30:00",
    "num_samples": 650,
    "f1_score": 0.92
  }
}
```

---

## 📁 Data Flow

### Storage Structure

```
test_suites/
├── builder/                      # Original test cases from Builder
│   └── login_001.json
│
├── recorded/                     # Original test cases from Recorder (all users)
│   └── session_001.json
│
└── generated/                    # Generated test cases
    ├── negative_invalid_input_123.json
    ├── boundary_max_length_124.json
    ├── security_sql_injection_125.json
    └── ... (20-50 more tests)
```

### Test Case Format

```json
{
  "test_case_id": "negative_invalid_input_123",
  "name": "Login - Test with invalid input data",
  "description": "Test with invalid input data",
  "url": "https://example.com/login",
  "source_test_id": "login_001",
  "expansion_type": "negative",
  "scenario_type": "invalid_input",
  "steps": [
    {
      "prompt": "navigate to login page",
      "action": "navigate",
      "url": "https://example.com/login"
    },
    {
      "prompt": "enter username in username field (with invalid data)",
      "action": "input",
      "element": "#username",
      "test_data": "invalid_data_@#$%",
      "description": "enter username in username field (with invalid data)"
    },
    {
      "prompt": "enter password in password field (with invalid data)",
      "action": "input",
      "element": "#password",
      "test_data": "invalid_data_@#$%",
      "description": "enter password in password field (with invalid data)"
    },
    {
      "prompt": "click login button",
      "action": "click",
      "element": "#login-btn"
    }
  ],
  "priority": "high",
  "tags": ["negative", "invalid_input", "expanded", "generated"],
  "status": "draft",
  "created_at": "2026-04-01T11:00:00",
  "generated_by": "ml_expansion",
  "suite": "generated",
  "saved_at": 1743508800
}
```

---

## 🎨 UI/UX Workflow

### Semantic Analysis Page

```
┌────────────────────────────────────────────────────────┐
│  Semantic Analysis - Test Case Expansion              │
└────────────────────────────────────────────────────────┘

┌────────────────────────────────────────────────────────┐
│  Step 1: Select Test Case                             │
│                                                        │
│  [Select Test Case ▼]                                 │
│    • Login with valid credentials (login_001)         │
│    • Registration form submission (reg_001)           │
│    • Checkout process (checkout_001)                  │
│                                                        │
│  [Generate Test Cases] ← Click this                   │
└────────────────────────────────────────────────────────┘

↓ System retrains ML immediately

↓ Generates 25 complete test cases

┌────────────────────────────────────────────────────────┐
│  Step 2: Review Generated Tests (25 tests)            │
│                                                        │
│  Filter: [All ▼] [Priority ▼] [Type ▼]               │
│                                                        │
│  ☑ Login - Invalid email (HIGH)                       │
│  ☑ Login - Empty fields (HIGH)                        │
│  ☑ Login - SQL injection (CRITICAL)                   │
│  ☑ Login - XSS attempt (CRITICAL)                     │
│  ☐ Login - Min length password (MEDIUM)               │
│  ☐ Login - Max length username (MEDIUM)               │
│  ☑ Login - Special characters (MEDIUM)                │
│  ☐ Login - Unicode characters (LOW)                   │
│  ...                                                   │
│                                                        │
│  [Select All] [Deselect All]                          │
│  [Save Selected (8 tests)]                            │
└────────────────────────────────────────────────────────┘

↓ User selects 8 tests and clicks "Save Selected"

✅ 8 complete test cases saved to test_suites/generated/
```

---

## 🚀 Benefits of This Architecture

### 1. **Instant Learning**
- ML learns from EACH test case immediately
- No waiting for 50 tests
- Perfect for multi-tenant SaaS

### 2. **Complete Test Generation**
- Not just scenario names
- FULL test case objects with steps, data, priorities
- Ready to run immediately

### 3. **User Control**
- User decides WHEN to expand (not automatic)
- User selects WHICH generated tests to keep
- User controls test coverage

### 4. **Scalability**
- Works with 1 test or 1000 tests
- Each user's tests improve their suggestions
- DB-ready architecture

### 5. **Cost Efficiency**
- Only retrain when needed (not on schedule)
- Only generate tests when requested
- Only save tests user wants

---

## 🔧 Implementation Checklist

- ✅ **Removed:** Auto-retrain threshold logic (50 tests, 30 days)
- ✅ **Created:** On-demand trainer (retrain when user clicks)
- ✅ **Created:** Test case expander (generates complete tests)
- ✅ **Updated:** API endpoints for expansion workflow
- ✅ **Removed:** Auto-retrain trigger from save endpoints
- ✅ **Documented:** Complete workflow and architecture

---

## 📖 Usage Examples

### Example 1: Basic Expansion

```bash
# User creates and saves test case
POST /recorder/save-test-case
{
  "session_id": "session_123",
  "name": "Login Test",
  "username": "phaneendra"
}

# User goes to Semantic Analysis, clicks "Generate"
POST /semantic/expand-test-case
{
  "test_case_id": "login_test_123"
}

# Response: 25 complete test cases
# User selects 10 tests
# Clicks "Save Selected"

POST /semantic/save-generated-tests
{
  "test_cases": [... 10 complete test case objects ...],
  "suite_name": "generated"
}

# Result: Now have 11 total tests (1 original + 10 generated)
```

### Example 2: Targeted Expansion

```bash
# Expand only security and negative tests
POST /semantic/expand-test-case
{
  "test_case_id": "payment_001",
  "expansion_types": ["security", "negative"]
}

# Response: 10 focused test cases (5 security + 5 negative)
```

---

## 📊 Expected Results

### ROI Per Test Case

| Stage | Tests Created | Time Invested | Tests Generated |
|-------|---------------|---------------|-----------------|
| **Original** | 1 test | 5 minutes | 1 test |
| **After Expansion** | 1 test | 5 min + 30 sec | 1 + 25 tests = **26 tests** |
| **User Selects** | 1 test | 5 min + 2 min | **10 tests saved** |

**Result:** 10 complete test cases from 7 minutes work!

### Typical Usage

- User A creates 5 tests → Expands each → Saves 40 tests total
- User B creates 3 tests → Expands each → Saves 25 tests total
- User C creates 10 tests → Expands each → Saves 80 tests total

**Average:** 1 test → 8-10 saved tests after expansion

---

## 🎯 Next Steps

### For Users:
1. Create/record your first test case
2. Save it to test_suites/
3. Go to Semantic Analysis page
4. Select the test case
5. Click "Generate Test Cases"
6. Review 25+ generated tests
7. Select the ones you want
8. Save them back to test_suites/
9. Repeat!

### For Developers:
1. Build UI for Semantic Analysis page
2. Add test case selection dropdown
3. Add "Generate Test Cases" button
4. Display generated tests with checkboxes
5. Add "Save Selected" functionality
6. Show success message with count

---

## 📝 Summary

**Old Workflow (WRONG):**
- Save 50 tests → Wait → Auto-retrain → Get scenario names

**New Workflow (CORRECT):**
- Create 1 test → Save → Select→ Click "Generate" → **Retrain instantly** → Get 25 complete test cases → Select wanted ones → Save → Done!

**Key Innovation:**
- **On-demand ML retraining** (not scheduled)
- **Complete test case generation** (not just names)
- **User-controlled expansion** (not automatic)

---

**Status:** ✅ Ready for Production  
**Updated:** April 1, 2026  
**Version:** 2.0 - On-Demand Architecture
