# 🔄 Hybrid Test Execution Architecture

## Overview

Test cases are saved in DUAL format for maximum flexibility:
- **JSON** - Metadata, steps, and execution control
- **Python files** - Executable test code for direct pytest execution  

```
test_cases/
  builder/
    TC001_LoginTest.json     ← Metadata + all language code
    exports/
      TC001_test.py          ← ✅ Executable Python test
      LoginTestTest.java     ← ✅ Executable Java test
      TC001.spec.js          ← ✅ Playwright test
      TC001.cy.js            ← ✅ Cypress test
```

---

## 🎯 Execution Modes

### Mode 1: JSON Step-by-Step (Default)
**Best for:** UI execution, debugging, screenshots, data overrides

```python
# Via API
POST /test-suite/execute/TC001
{
  "headless": false,
  "data_overrides": {"1": "new_email@example.com"}
}

# Via CLI
python run_tests.py TC001
python run_tests.py --mode api TC001
```

**Features:**
- ✅ Step-by-step execution with screenshots
- ✅ Runtime data overrides per step
- ✅ Detailed logging and error reporting
- ✅ Full UI control

### Mode 2: Python File Direct (Hybrid)
**Best for:** CI/CD, command line, standard pytest workflows

```bash
# Run with pytest directly
cd test_cases/builder/exports
pytest TC001_test.py -v

# Via CLI runner
python run_tests.py --mode pytest TC001
python run_tests.py --mode pytest  # All tests

# Run with pytest options
pytest TC001_test.py -v -s --tb=short
pytest -k "login" -v  # Run tests matching "login"
```

**Features:**
- ✅ Standard pytest execution
- ✅ CI/CD integration
- ✅ IDE integration (run/debug in PyCharm, VS Code)
- ✅ Faster execution
- ✅ Standard Python testing practices

---

## 📊 Comparison

| Feature | JSON Steps | Python File |
|---------|-----------|-------------|
| **UI Execution** | ✅ Full control | ❌ N/A |
| **Screenshots** | ✅ Per step | ⚠️ Manual |
| **Data Overrides** | ✅ Runtime | ⚠️ Edit file |
| **CI/CD** | ⚠️ Via API | ✅ Direct |
| **IDE Support** | ❌ Limited | ✅ Full |
| **Debugging** | ✅ Step-by-step | ✅ Standard |
| **Speed** | ⚠️ Slower | ✅ Faster |
| **Flexibility** | ✅ High | ⚠️ Medium |

---

## 🚀 Quick Start

### Create a Test
```python
# Via UI (Test Builder)
1. Go to http://localhost:5002
2. Click "Test Builder"
3. Add steps
4. Save

# Generates both:
# - TC001_MyTest.json
# - exports/TC001_test.py
```

### Execute the Test

**Option A: From UI**
```
1. Go to "Test Suite"
2. Click on test
3. Click "Execute"
# Uses JSON step-by-step mode
```

**Option B: From Command Line (JSON mode)**
```bash
python run_tests.py TC001
```

**Option C: From Command Line (Pytest mode)**
```bash
python run_tests.py --mode pytest TC001
# OR
cd test_cases/builder/exports
pytest TC001_test.py -v
```

**Option D: In CI/CD Pipeline**
```yaml
# .github/workflows/tests.yml
- name: Run tests
  run: pytest test_cases/builder/exports/ -v
```

---

## 🔧 API Changes

### Execute Test Case (Enhanced)

```python
# Default: JSON step-by-step
POST /test-suite/execute/TC001
{
  "headless": false,
  "execution_mode": "json_steps"  # Default
}

# Hybrid: Python file direct
POST /test-suite/execute/TC001
{
  "headless": false,
  "execution_mode": "python_file"  # New!
}
```

---

## 💡 Best Practices

### When to use JSON mode:
- ✅ Testing from UI
- ✅ Need runtime data overrides
- ✅ Want step-by-step screenshots
- ✅ Debugging test failures

### When to use Python file mode:
- ✅ CI/CD pipelines
- ✅ Command line execution
- ✅ Integration with existing pytest suites
- ✅ IDE debugging
- ✅ Faster execution needed

---

## 🎓 Examples

### Example 1: Run all tests in CI
```bash
# In your CI pipeline
pytest test_cases/builder/exports/ -v --junitxml=results.xml
```

### Example 2: Run specific tests with tags
```bash
pytest test_cases/builder/exports/ -v -m "smoke"
```

### Example 3: Debug in IDE
Open `TC001_test.py` in PyCharm/VS Code and click "Run" or "Debug"

### Example 4: Runtime data override (JSON mode only)
```python
# Via API
POST /test-suite/execute/TC001
{
  "data_overrides": {
    "1": "custom_username@test.com",
    "2": "custom_password"
  }
}
```

---

## 🔮 Future Enhancements

- [ ] Live reload of .py files when JSON changes
- [ ] Parameterized test execution
- [ ] Test data from CSV/Excel
- [ ] Parallel execution support
- [ ] Video recording for pytest mode
- [ ] Allure report integration
