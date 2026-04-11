# Test Suites

This directory contains test suites - collections of multiple test cases that run together as a cohesive test scenario.

## 📦 What are Test Suites?

Test suites group multiple test cases for:
- **End-to-end workflows** - Complete user journeys across multiple pages
- **Regression testing** - Run all critical tests together
- **Feature testing** - Group tests for specific features
- **Environment testing** - Run same tests across different environments

## 📂 Structure

```
test_suites/
├── <suite_name>.json       # Suite definition file
└── .gitkeep               # Keep folder in version control
```

## 🔧 Suite Format

```json
{
  "suite_id": "SUITE001",
  "name": "User Authentication Flow",
  "description": "Complete login, profile update, and logout flow",
  "test_cases": [
    {
      "test_id": "TC001",
      "source": "builder",
      "order": 1
    },
    {
      "test_id": "TC002",
      "source": "recorder",
      "order": 2
    }
  ],
  "execution_config": {
    "browser": "chrome",
    "headless": false,
    "screenshot_on_failure": true,
    "stop_on_failure": false
  }
}
```

## 🚀 Creating a Test Suite

### Via Web UI (Phase 0)
1. Open http://localhost:5000/pages/advanced-test-builder.html
2. Click "Test Suites" tab
3. Select multiple test cases
4. Configure execution order
5. Save suite

### Via API
```bash
POST /test-suites/create
{
  "name": "Suite Name",
  "test_cases": ["TC001", "TC002"],
  "config": {...}
}
```

### Manually
Create a JSON file in this directory following the structure above.

## ▶️ Running Test Suites

### Web UI
1. Go to Test Suites page
2. Select suite
3. Click "Run Suite"
4. View real-time progress
5. Check results

### API
```bash
POST /test-suites/execute/<suite_id>
```

### CLI
```bash
python src/main/python/test_suite_runner.py --suite SUITE001
```

## 📊 Execution Flow

1. **Load Suite** - Read suite definition
2. **Load Test Cases** - Fetch all test cases in order
3. **Initialize Browser** - Start browser session
4. **Execute Tests** - Run each test sequentially
5. **Collect Results** - Aggregate pass/fail status
6. **Generate Report** - Create detailed execution report
7. **Cleanup** - Close browser, save artifacts

## 🎯 Suite Features

### Sequential Execution
- Tests run in specified order
- Maintains browser state between tests
- Shares session data

### Parallel Execution (Future)
- Run independent tests simultaneously
- Faster execution for large suites
- Separate browser instances

### Conditional Execution
- Skip tests based on previous results
- Run cleanup tests only on failure
- Environment-specific test selection

### Data Sharing
- Pass data between tests
- Store variables in suite context
- Use previous test outputs

## 📈 Results & Reports

Suite execution generates:
- **Summary Report** - Pass/fail count, duration
- **Detailed Logs** - Step-by-step execution trace
- **Screenshots** - Saved in `execution_results/suites/<suite_id>/`
- **Video Recording** - Optional full session recording

Results location:
```
execution_results/
└── suites/
    └── <suite_id>_<timestamp>/
        ├── summary.json
        ├── detailed_log.txt
        └── screenshots/
```

## 🔍 Example Suites

### E2E User Flow
```json
{
  "name": "Complete User Journey",
  "test_cases": [
    "TC001_register",
    "TC002_login",
    "TC003_update_profile",
    "TC004_logout"
  ]
}
```

### Regression Suite
```json
{
  "name": "Critical Path Regression",
  "test_cases": [
    "TC_LOGIN",
    "TC_SEARCH",
    "TC_CHECKOUT",
    "TC_PAYMENT"
  ],
  "config": {
    "stop_on_failure": true
  }
}
```

### Smoke Test
```json
{
  "name": "Quick Smoke Test",
  "test_cases": [
    "TC_HOME_LOAD",
    "TC_LOGIN_PAGE",
    "TC_SIGNUP_PAGE"
  ],
  "config": {
    "headless": true,
    "timeout": 5000
  }
}
```

## 🛠️ Best Practices

1. **Keep suites focused** - Group related tests only
2. **Maintain order** - Tests should be independent or properly sequenced
3. **Use meaningful names** - Clear suite purpose
4. **Document dependencies** - Note if tests share state
5. **Set appropriate timeouts** - Don't make suites too long
6. **Handle failures gracefully** - Configure stop_on_failure appropriately
7. **Clean up after execution** - Reset test data if needed

## 🔄 Suite Management

### List All Suites
```bash
GET /test-suites/list
```

### Update Suite
```bash
PUT /test-suites/<suite_id>
{
  "test_cases": [...]
}
```

### Delete Suite
```bash
DELETE /test-suites/<suite_id>
```

## 📝 Notes

- Currently in **Phase 0** - Advanced features coming soon
- Suite execution maintains single browser session
- Can mix builder and recorder test cases
- Supports same self-healing as individual tests
- Results integrated with main execution results

---

**Related Documentation:**
- [Test Cases](../test_cases/README.md)
- [Test Execution](../TESTING_GUIDE.md)
- [Phase 0 Implementation](../PHASE0_IMPLEMENTATION.md)
