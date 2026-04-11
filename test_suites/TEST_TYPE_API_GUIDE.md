# Test Type Classification - API Guide

**Date:** April 1, 2026  
**Status:** ✅ ACTIVE  
**Purpose:** Guide for saving tests with proper type classification

---

## 🎯 Overview

Both **Test Builder** and **Test Recorder** now support **test type classification** for better organization.

**Structure:**
```
test_suites/
├── {test_type}/          # regression, smoke, integration, etc.
│   ├── builder/          # Tests from Test Builder
│   └── recorded/         # Tests from Test Recorder
```

---

## 📋 Available Test Types

| Test Type | Purpose | When to Use |
|-----------|---------|-------------|
| `regression` | Verify existing functionality still works | Recurring tests after changes |
| `smoke` | Quick critical path validation | Fast sanity checks |
| `integration` | Test component interactions | Multi-system workflows |
| `performance` | Measure speed and resources | Load and benchmark tests |
| `security` | Identify vulnerabilities | Security audits |
| `exploratory` | Ad-hoc testing | Experimentation, learning |
| `general` | Default catch-all | When type is uncertain |

---

## 🔧 API Reference

### 1. Save Test from Recorder

**Endpoint:** `POST /recorder/save-test-case`

**Request Body:**
```json
{
  "session_id": "abc123",
  "name": "Login Happy Path",
  "username": "john",
  "test_type": "smoke"     // NEW: Specify test type
}
```

**Response:**
```json
{
  "success": true,
  "test_case_id": "login_happy_path",
  "filepath": "test_suites/smoke/recorded/login_happy_path.json",
  "test_type": "smoke",
  "message": "Test case saved successfully to test_suites/smoke/recorded/"
}
```

**Result:** Saves to `test_suites/smoke/recorded/login_happy_path.json`

---

### 2. Save Test from Builder

**Endpoint:** `POST /test-case/save/{session_id}`

**Request Body:**
```json
{
  "name": "Checkout Flow",
  "test_case_id": "test_checkout",
  "tags": ["ecommerce", "payment"],
  "priority": "high",
  "test_type": "regression"  // NEW: Specify test type
}
```

**Response:**
```json
{
  "success": true,
  "test_case": { ... },
  "filepath": "test_suites/regression/builder/test_checkout_Checkout_Flow.json",
  "test_type": "regression"
}
```

**Result:** Saves to `test_suites/regression/builder/test_checkout_Checkout_Flow.json`

---

## 🖥️ Frontend Integration Examples

### Example 1: Recorder Save Dialog

```javascript
// When user clicks "Save Test Case" in recorder
async function saveRecorderTest() {
    const testType = document.getElementById('test-type-select').value; // NEW
    
    const response = await fetch('/recorder/save-test-case', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            session_id: currentSessionId,
            name: testName,
            username: currentUser,
            test_type: testType  // NEW: Send test type
        })
    });
    
    const result = await response.json();
    console.log(`Saved to: ${result.filepath}`);
    console.log(`Test Type: ${result.test_type}`);
}
```

**HTML:**
```html
<select id="test-type-select">
    <option value="general">General</option>
    <option value="smoke">Smoke Test</option>
    <option value="regression" selected>Regression</option>
    <option value="integration">Integration</option>
    <option value="performance">Performance</option>
    <option value="security">Security</option>
    <option value="exploratory">Exploratory</option>
</select>
```

---

### Example 2: Builder Save Dialog

```javascript
// When user clicks "Save Test" in builder
async function saveBuilderTest(sessionId) {
    const testType = document.getElementById('builder-test-type').value; // NEW
    
    const response = await fetch(`/test-case/save/${sessionId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            name: testName,
            test_case_id: testId,
            tags: tags,
            priority: priority,
            test_type: testType  // NEW: Send test type
        })
    });
    
    const result = await response.json();
    console.log(`Saved to: ${result.filepath}`);
    console.log(`Test Type: ${result.test_type}`);
}
```

---

## 📊 Metadata in Saved Files

### Recorder Test Example

**File:** `test_suites/regression/recorded/login_test.json`

```json
{
  "test_case_id": "login_test",
  "name": "Login Test",
  "test_type": "regression",    // ← From folder structure
  "source": "recorded",          // ← Always "recorded" for recorder
  "saved_to_suite_at": "2026-04-01T10:30:00",
  "username": "john",
  "actions": [...],
  "tags": ["recorder", "regression"]
}
```

### Builder Test Example

**File:** `test_suites/smoke/builder/homepage_load.json`

```json
{
  "test_case_id": "test_001",
  "name": "Homepage Load",
  "test_type": "smoke",          // ← From folder structure
  "source": "builder",           // ← Always "builder" for builder
  "saved_to_suite_at": "2026-04-01T10:30:00",
  "prompts": [...],
  "tags": ["critical-path"]
}
```

---

## 🔄 Loading Tests

When loading tests for semantic analysis or execution, the system **automatically detects**:

- **test_type** from folder name (`regression`, `smoke`, etc.)
- **source** from subfolder (`builder` or `recorded`)

**Example:**
```python
# Load test from: test_suites/regression/builder/test_001.json
test_case = generator._load_from_test_suites("test_001")

# Returns:
{
    "test_case_id": "test_001",
    "test_type": "regression",  // ← Detected automatically
    "source": "builder",        // ← Detected automatically
    ...
}
```

---

## ✅ Default Behavior

### If `test_type` is NOT specified:

**Recorder:**
- Defaults to `"general"`
- Saves to: `test_suites/general/recorded/`

**Builder:**
- Defaults to `"general"`
- Saves to: `test_suites/general/builder/`

### Backward Compatibility:

Old tests in `test_suites/builder/` or `test_suites/recorded/` still work:
- `test_type` detected as `"general"`
- `source` detected as `"builder"` or `"recorded"`

---

## 💡 Best Practices

### 1. **Choose Appropriate Test Type**
   - Use `smoke` for quick critical path tests
   - Use `regression` for recurring validation tests
   - Use `exploratory` for ad-hoc experiments

### 2. **Consistent Naming**
   - Clear, descriptive test names
   - Example: `login_happy_path`, `checkout_with_discount`

### 3. **Use Tags for Additional Context**
   ```json
   {
     "test_type": "regression",
     "tags": ["authentication", "critical-path", "p0"]
   }
   ```

### 4. **Migrate Old Tests Gradually**
   - No rush to migrate legacy tests
   - Move important tests to proper categories first
   - Keep exploratory tests in `general/`

---

## 🧪 Testing the Integration

### Test 1: Save Recorder Test with Type

```bash
curl -X POST http://localhost:5002/recorder/save-test-case \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session_123",
    "name": "Login Test",
    "username": "john",
    "test_type": "smoke"
  }'
```

**Expected:** Saves to `test_suites/smoke/recorded/login_test.json`

### Test 2: Save Builder Test with Type

```bash
curl -X POST http://localhost:5002/test-case/save/session_456 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Checkout Flow",
    "test_type": "regression",
    "priority": "high"
  }'
```

**Expected:** Saves to `test_suites/regression/builder/test_*_Checkout_Flow.json`

### Test 3: Load and Verify Metadata

```bash
# Trigger semantic analysis on saved test
curl -X POST http://localhost:5002/semantic/generate-test-cases \
  -H "Content-Type: application/json" \
  -d '{
    "test_case_id": "login_test"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "source_test": {
    "id": "login_test",
    "name": "Login Test",
    "test_type": "smoke",     // ← Detected from folder
    "source": "recorded"      // ← Detected from folder
  },
  "generated_tests": [...]
}
```

---

## 🚀 Summary

**Now UNIFORM across Builder and Recorder:**

| Feature | Recorder | Builder |
|---------|----------|---------|
| **Test Type Parameter** | ✅ `test_type` | ✅ `test_type` |
| **Default Type** | `general` | `general` |
| **Folder Structure** | `test_suites/{type}/recorded/` | `test_suites/{type}/builder/` |
| **Metadata** | `source: "recorded"` | `source: "builder"` |
| **Auto-Detection** | ✅ Yes | ✅ Yes |

**Benefits:**
- ✅ Consistent API across all test creation methods
- ✅ Better test organization
- ✅ Improved ML learning by test category
- ✅ Clear folder structure
- ✅ Easy to locate and manage tests

---

**Next Steps:**
1. Update frontend to include test type dropdown
2. Test saving from both builder and recorder
3. Verify folder structure is created correctly
4. Confirm semantic analysis loads metadata properly
