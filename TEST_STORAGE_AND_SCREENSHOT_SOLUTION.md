# 📁 Test Storage & Screenshot Solution

## 🔍 Current Issues Identified

### Issue 1: Test Cases Not Appearing in Test Suite

**Problem:**
- **Recorder** saves test cases to: `test_cases/user_{username}/recorder/`  
  Example: `test_cases/user_phaneendra/recorder/login_test_1774523839.json`

- **Test Builder** saves test cases to: `test_cases/builder/`

- **Test Suite page** loads two sources:
  1. `/recorder/sessions` - Shows active recording sessions (temporary)
  2. `/test-suite/test-cases` - Shows only Builder test cases (from `test_cases/builder/`)

**Result:** Saved recorder test cases are stored on disk but NOT appearing in Test Suite!

### Issue 2: No Screenshots for Failed Tests in Test Suite

**Problem:** When tests fail, execution results are saved without screenshot paths or references.

---

## ✅ Solution 1: Make Recorder Test Cases Visible in Test Suite

### Option A: Modify API to Include Recorder Test Cases (RECOMMENDED)

Add a new endpoint to list recorder test cases from all user folders:

```python
# In api_server_modular.py
@app.route('/test-suite/recorder-test-cases', methods=['GET'])
def list_recorder_test_cases():
    """List all saved recorder test cases from user folders."""
    return recorder_handler.list_saved_recorder_tests()
```

```python
# In recorder_handler.py
def list_saved_recorder_tests():
    """
    Scan test_cases/user_*/recorder/ folders and return all saved tests.
    """
    import glob
    
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    recorder_pattern = os.path.join(project_root, 'test_cases', 'user_*', 'recorder', '*.json')
    
    test_cases = []
    
    for filepath in glob.glob(recorder_pattern):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                test_data = json.load(f)
                
                test_cases.append({
                    'test_case_id': test_data.get('test_case_id'),
                    'name': test_data.get('name'),
                    'url': test_data.get('url'),
                    'action_count': len(test_data.get('actions', [])),
                    'created_at': test_data.get('saved_at', test_data.get('created_at', 0)),
                    'username': test_data.get('username', 'unknown'),
                    'source': 'recorder',
                    'status': test_data.get('status', 'active'),
                    'filepath': filepath
                })
        except Exception as e:
            logger.error(f"Error reading recorder test: {filepath}, {e}")
            continue
    
    return jsonify({
        'success': True,
        'test_cases': test_cases,
        'count': len(test_cases)
    }), 200
```

```javascript
// In test-suite.js - Update loadTestCases()
async function loadTestCases() {
    try {
        const [recorderSessionsResponse, builderTestsResponse, recorderTestsResponse] = await Promise.all([
            fetch(`${API_URL}/recorder/sessions`),
            fetch(`${API_URL}/test-suite/test-cases`),
            fetch(`${API_URL}/test-suite/recorder-test-cases`)  // NEW
        ]);
        
        const recorderSessions = await recorderSessionsResponse.json();
        const builderTests = await builderTestsResponse.json();
        const recorderTests = await recorderTestsResponse.json();  // NEW
        
        let allSessions = [];
        
        // Add active recorder sessions
        if (recorderSessions.success) {
            allSessions = recorderSessions.sessions || [];
        }
        
        // Add saved builder test cases
        if (builderTests.success) {
            allSessions = [...allSessions, ...convertTestCases(builderTests.test_cases)];
        }
        
        // Add saved recorder test cases  // NEW
        if (recorderTests.success) {
            allSessions = [...allSessions, ...convertTestCases(recorderTests.test_cases)];
        }
        
        // Continue with existing logic...
    }
}
```

### Option B: Unified Storage Structure (FUTURE - Better Long-term)

Migrate to a unified structure:
```
test_cases/
├── user_phaneendra/
│   ├── builder/         # AI-generated tests
│   │   ├── login_flow_test.json
│   │   └── checkout_test.json
│   └── recorder/        # Recorded tests
│       ├── login_test_1774523839.json
│       └── search_test_1774524000.json
```

Update `test_case_builder.py` to scan ALL test case folders (builder + recorder):
```python
def list_test_cases(self, include_recorder=True):
    """List test cases from builder AND recorder folders."""
    results = []
    
    # Load builder test cases
    builder_dir = os.path.join(self.test_cases_dir, 'builder')
    results.extend(self._load_from_dir(builder_dir, source='builder'))
    
    # Load recorder test cases (NEW)
    if include_recorder:
        recorder_pattern = os.path.join(self.test_cases_dir, 'user_*', 'recorder')
        for recorder_dir in glob.glob(recorder_pattern):
            results.extend(self._load_from_dir(recorder_dir, source='recorder'))
    
    return results
```

---

## ✅ Solution 2: Add Screenshots for Failed Tests

### Current State
- Screenshots are captured in: `screenshots/failures/`
- Execution results are saved in: `execution_results/`
- BUT connection between them is missing!

### Enhancement Needed

**1. Update Test Executor to Capture Screenshot Paths**

```python
# In test_executor.py or test_suite_runner.py
def execute_test_with_screenshots(test_case_id, browser='chrome'):
    """
    Execute test and capture screenshots on failure.
    """
    results = {
        'test_case_id': test_case_id,
        'start_time': datetime.now().isoformat(),
        'status': 'running',
        'screenshots': [],  # NEW
        'failed_step': None,
        'error_message': None
    }
    
    try:
        # Execute test steps...
        for step_idx, step in enumerate(test_steps):
            try:
                execute_step(step)
            except Exception as step_error:
                # CAPTURE SCREENSHOT ON FAILURE
                screenshot_path = capture_failure_screenshot(
                    test_case_id, 
                    step_idx, 
                    browser
                )
                
                results['screenshots'].append({
                    'step': step_idx,
                    'path': screenshot_path,
                    'timestamp': datetime.now().isoformat(),
                    'error': str(step_error)
                })
                
                results['failed_step'] = step_idx
                results['error_message'] = str(step_error)
                results['status'] = 'failed'
                break
        
        if results['status'] == 'running':
            results['status'] = 'passed'
            
    except Exception as e:
        results['status'] = 'error'
        results['error_message'] = str(e)
    
    finally:
        results['end_time'] = datetime.now().isoformat()
        
    # Save execution results with screenshot paths
    save_execution_results(results)
    
    return results


def capture_failure_screenshot(test_case_id, step_idx, browser):
    """
    Capture screenshot and return the file path.
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{test_case_id}_step{step_idx}_{timestamp}.png"
    
    screenshots_dir = os.path.join('screenshots', 'failures')
    os.makedirs(screenshots_dir, exist_ok=True)
    
    filepath = os.path.join(screenshots_dir, filename)
    
    driver.save_screenshot(filepath)
    
    logger.info(f"[SCREENSHOT] Saved failure screenshot: {filepath}")
    
    return filepath
```

**2. Update Execution Results Schema**

```json
{
  "execution_id": "EXE_20260326_153045",
  "test_case_id": "login_test_1774523839",
  "start_time": "2026-03-26T15:30:45",
  "end_time": "2026-03-26T15:31:12",
  "status": "failed",
  "duration_ms": 27000,
  "browser": "chrome",
  "failed_step": 3,
  "error_message": "Element not found: id=submit-button",
  "screenshots": [
    {
      "step": 3,
      "path": "screenshots/failures/login_test_1774523839_step3_20260326_153108.png",
      "timestamp": "2026-03-26T15:31:08",
      "error": "NoSuchElementException: Unable to locate element"
    }
  ]
}
```

**3. Display Screenshots in Test Suite UI**

```javascript
// In test-suite.js
function displayExecutionResults(results) {
    let html = `
        <div class="execution-results">
            <h4>Test Execution Results</h4>
            <p>Status: <span class="${results.status}">${results.status}</span></p>
            <p>Duration: ${(results.duration_ms / 1000).toFixed(2)}s</p>
    `;
    
    // Show screenshots if test failed
    if (results.status === 'failed' && results.screenshots && results.screenshots.length > 0) {
        html += `
            <div class="failure-screenshots">
                <h5>🖼️ Failure Screenshots:</h5>
        `;
        
        results.screenshots.forEach(screenshot => {
            html += `
                <div class="screenshot-item">
                    <p><strong>Step ${screenshot.step}:</strong> ${screenshot.error}</p>
                    <img src="/${screenshot.path}" alt="Failure at step ${screenshot.step}" 
                         style="max-width: 600px; border: 2px solid red; border-radius: 8px; margin: 10px 0;">
                    <p><small>Captured at: ${new Date(screenshot.timestamp).toLocaleString()}</small></p>
                </div>
            `;
        });
        
        html += `</div>`;
    }
    
    html += `</div>`;
    
    document.getElementById('executionResultsContainer').innerHTML = html;
}
```

---

## 📊 Summary of Changes Needed

### High Priority (Immediate)
1. ✅ **Add endpoint** `/test-suite/recorder-test-cases` to list saved recorder tests
2. ✅ **Update** `loadTestCases()` in test-suite.js to fetch recorder tests
3. ✅ **Capture** screenshot paths during test execution
4. ✅ **Save** screenshot paths in execution results JSON
5. ✅ **Display** screenshots in Test Suite when viewing failed test results

### Medium Priority (This Week)
6. ⏳ **Add** execution history viewer in Test Suite (show past runs with screenshots)
7. ⏳ **Add** screenshot comparison (before/after) for visual regression
8. ⏳ **Add** annotations on screenshots (highlight failed element)

### Low Priority (Future)
9. 🔮 Unified folder structure for all test cases
10. 🔮 Database storage for execution results (fast queries)
11. 🔮 Dashboard with failure analytics and trends

---

## 📂 Current File Locations

**Saved Test Cases:**
```
✅ test_cases/user_phaneendra/recorder/login_test_1774523839.json
✅ test_cases/builder/  (Builder tests - currently showing in Test Suite)
```

**Execution Results:**
```
✅ execution_results/recorder/Login_Test_20260324_153131.json
✅ execution_results/builder/  (Builder test results)
```

**Screenshots:**
```
✅ screenshots/failures/  (Failure screenshots captured)
```

---

## 🚀 Implementation Steps

### Step 1: Make Recorder Tests Visible (1 hour)
1. Add `list_saved_recorder_tests()` function to recorder_handler.py
2. Add `/test-suite/recorder-test-cases` endpoint to api_server_modular.py
3. Update `loadTestCases()` in test-suite.js
4. Test by refreshing Test Suite page

### Step 2: Add Screenshot Capture (2 hours)
1. Update test execution functions to capture screenshots
2. Modify execution results schema to include screenshot array
3. Save screenshot paths when tests fail
4. Test by running a failing test

### Step 3: Display Screenshots in UI (1 hour)
1. Update test-suite.html to show screenshot section
2. Update test-suite.js to display screenshots
3. Add CSS styling for screenshot gallery
4. Test by viewing failed test results

**Total Time: ~4 hours for complete solution**

---

## ✅ Testing Checklist

- [ ] Saved recorder test case appears in Test Suite after refresh
- [ ] Test source filter shows "Test Recorder" vs "Test Builder" correctly
- [ ] Failed test execution captures screenshot
- [ ] Screenshot path saved in execution results JSON
- [ ] Screenshot displays when viewing test results in UI
- [ ] Screenshot downloads/opens when clicked
- [ ] Multiple screenshots shown if multiple steps fail

---

## 🎯 Expected Result

After implementation:
1. ✅ **All saved test cases visible** - Both recorder and builder tests show in Test Suite
2. ✅ **Screenshots captured** - Failure screenshots automatically saved during execution
3. ✅ **Visual debugging** - Screenshots displayed alongside error messages in UI
4. ✅ **Better debugging** - Users can see exactly where and why tests failed
