# Test Suites - Recommended Folder Structure

**Date:** April 1, 2026  
**Status:** ✅ ACTIVE  
**Purpose:** Organize test cases by TYPE and SOURCE for better management

---

## 🎯 Recommended Structure

### Organization by Test Type and Source

```
test_suites/
├── regression/                   # Regression tests
│   ├── builder/                  # Created with Test Builder
│   │   ├── test_001_login.json
│   │   ├── test_002_checkout.json
│   │   └── test_003_profile_update.json
│   └── recorded/                 # Created with Test Recorder
│       ├── session_001_full_flow.json
│       └── session_002_payment_flow.json
│
├── smoke/                        # Smoke tests (critical path)
│   ├── builder/
│   │   ├── test_001_homepage_load.json
│   │   └── test_002_login_happy_path.json
│   └── recorded/
│       └── session_001_quick_check.json
│
├── integration/                  # Integration tests
│   ├── builder/
│   │   └── test_001_api_integration.json
│   └── recorded/
│       └── session_001_e2e_flow.json
│
├── performance/                  # Performance tests
│   ├── builder/
│   └── recorded/
│
├── security/                     # Security tests
│   ├── builder/
│   └── recorded/
│
└── exploratory/                  # Exploratory/Ad-hoc tests
    ├── builder/
    └── recorded/
```

---

## 📋 Test Type Categories

### 1. **regression/** - Regression Tests
**Purpose:** Verify that existing functionality still works after changes

**Examples:**
- Login flow after UI update
- Checkout process after payment gateway change
- Search functionality after database migration

**When to use:** For recurring tests that verify core functionality

---

### 2. **smoke/** - Smoke Tests
**Purpose:** Quick verification that critical functionality works

**Examples:**
- Homepage loads successfully
- Login with valid credentials works
- Can add item to cart

**When to use:** For fast, critical path validation before deeper testing

---

### 3. **integration/** - Integration Tests
**Purpose:** Test interactions between multiple components/systems

**Examples:**
- Frontend + Backend + Database flow
- Third-party API integrations
- Multi-step workflows across modules

**When to use:** For testing component interactions and data flow

---

### 4. **performance/** - Performance Tests
**Purpose:** Measure speed, responsiveness, and resource usage

**Examples:**
- Page load time under load
- API response times
- Concurrent user handling

**When to use:** For benchmark and performance validation

---

### 5. **security/** - Security Tests
**Purpose:** Identify vulnerabilities and security issues

**Examples:**
- SQL injection attempts
- XSS attack vectors
- Authentication bypass tests

**When to use:** For security auditing and vulnerability scanning

---

### 6. **exploratory/** - Exploratory Tests
**Purpose:** Ad-hoc testing and experimentation

**Examples:**
- Testing new features without formal spec
- Investigating bugs
- Learning application behavior

**When to use:** For informal testing and discovery

---

## 🔧 How It Works

### Automatic Metadata Extraction

When you save a test to this structure, the system automatically detects:

**From folder structure:**
```
test_suites/regression/builder/test_001.json
              ↓          ↓
         test_type    source
```

**Enriched test case:**
```json
{
  "test_case_id": "test_001",
  "name": "Login Test",
  "test_type": "regression",  // ← Added automatically
  "source": "builder",         // ← Added automatically
  "storage_path": "test_suites/regression/builder/test_001.json",
  "actions": [...]
}
```

### When Generating Test Cases

When you click "Generate Test Cases" in Semantic Analysis:

**Frontend displays:**
```
📋 Source Test: Login Test
🔍 Test Type: Regression
⚙️  Source: Test Builder
📊 Actions: 5 steps

Generated 5 test variants:
- Negative Test
- Boundary Test
- Edge Case Test
- Variation Test
- Compatibility Test
```

---

## 💾 How to Save Tests

### Option 1: Test Builder (Manual Organization)

When building tests, you can specify the test type:

```javascript
// In Test Builder
saveTest({
  name: "Login Happy Path",
  test_type: "smoke",    // ← Specify test type
  // ... test steps
});

// Saves to: test_suites/smoke/builder/
```

### Option 2: Test Recorder (Auto Organization)

When recording tests, they auto-save to:

```
test_suites/exploratory/recorded/  (default)
```

You can move them later to proper categories.

---

## 📊 Benefits

### 1. **Better Organization**
- Find tests by purpose (regression, smoke, etc.)
- Know which tool created each test
- Clear folder hierarchy

### 2. **ML Semantic Analysis Enhancement**
- ML learns patterns PER test type
- Better suggestions for each category
- Improved accuracy over time

### 3. **Team Collaboration**
- Clear test ownership
- Easy to assign test types to team members
- Consistent structure across projects

### 4. **Reporting & Metrics**
- Track test counts by type
- Measure coverage per category
- Identify gaps in test suites

---

## 🔄 Backward Compatibility

### Legacy Structure Still Supported

If you have tests in the old structure:

```
test_suites/
├── builder/
│   └── test_001.json
└── recorded/
    └── session_001.json
```

**They still work!** The system detects:
- `test_type`: "general"
- `source`: "builder" or "recorded"

### Migration (Optional)

To migrate to the new structure:

```powershell
# PowerShell script
cd C:\Users\valaboph\AIAutomation

# Move builder tests to regression/builder
New-Item -ItemType Directory -Path "test_suites\regression\builder" -Force
Move-Item "test_suites\builder\*.json" "test_suites\regression\builder\"

# Move recorded tests to exploratory/recorded
New-Item -ItemType Directory -Path "test_suites\exploratory\recorded" -Force
Move-Item "test_suites\recorded\*.json" "test_suites\exploratory\recorded\"
```

---

## 🚀 Best Practices

### 1. **Start with Categories You Need**
Don't create all folders upfront. Start with:
- `smoke/` - For critical path tests
- `regression/` - For recurring tests
- `exploratory/` - For ad-hoc tests

### 2. **Use Consistent Naming**
```
test_001_login_happy_path.json        ✅ Good
test_002_checkout_with_discount.json  ✅ Good
random_test.json                      ❌ Bad
test.json                             ❌ Bad
```

### 3. **Move Tests to Proper Categories**
- Start in `exploratory/`
- Once stable, move to `regression/`
- Critical tests go to `smoke/`

### 4. **Document Your Tests**
Add descriptions in test JSON:
```json
{
  "name": "Login Test",
  "description": "Verifies user can login with valid credentials",
  "test_type": "smoke",
  "tags": ["authentication", "critical-path"]
}
```

---

## 📈 Expected Results

### After Implementation:

**Week 1:** Save 10 tests to different categories
```
test_suites/
├── smoke/builder/        (3 tests)
├── regression/builder/   (5 tests)
└── exploratory/recorded/ (2 tests)
```

**Week 2:** Semantic Analysis learns patterns
- Better suggestions for smoke tests
- More relevant variations for regression tests

**Week 4:** Team collaboration improves
- Everyone knows where to find tests
- Clear ownership by test type
- Easy to track progress

---

## ✅ Summary

**Key Points:**
- ✅ Organize by test type (regression, smoke, integration, etc.)
- ✅ Subdivide by source (builder, recorded)
- ✅ Backward compatible with legacy structure
- ✅ Automatic metadata extraction
- ✅ Better ML learning and suggestions

**Next Steps:**
1. Review this structure
2. Choose test types you need
3. Start saving tests to proper categories
4. Enjoy better organization and ML suggestions!

---

**Questions?** Check the main [UNIFIED_STORAGE_GUIDE.md](./UNIFIED_STORAGE_GUIDE.md) for more details.
