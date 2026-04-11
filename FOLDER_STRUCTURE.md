# 📁 Project Folder Structure

## Overview

This document explains the folder structure for test automation framework storage.

**Last Updated:** March 20, 2026

---

## 🗂️ Root Level Directories

```
AIAutomation/
├── test_cases/              # Test case definitions (persistent)
│   ├── builder/             # Test Builder test cases (JSON)
│   │   ├── TC001_login.json
│   │   ├── TC002_registration.json
│   │   └── exports/         # Exported executable test files
│   │       ├── TC001_test.py
│   │       ├── LoginTest.java
│   │       └── TC001.spec.js
│   └── recorder/            # Test Recorder test cases (JSON) - FUTURE
│       └── ...
│
├── test_suites/             # Test suite definitions (persistent) - FUTURE
│   ├── builder/             # Test Builder test suites
│   │   ├── smoke_tests.json
│   │   └── regression_tests.json
│   └── recorder/            # Test Recorder test suites
│       └── ...
│
├── execution_results/       # Test execution results (persistent)
│   ├── recorder/            # Test Recorder execution results
│   │   ├── Producer_Login_20260320_143025.json
│   │   ├── Producer_Login_20260320_150512.json
│   │   └── screenshots/
│   │       └── failure_step3_20260320_143030.png
│   └── builder/             # Test Builder execution results
│       ├── TC001_20260320_153045.json
│       ├── TC002_20260320_154120.json
│       └── screenshots/
│           └── TC001_step5_failed.png
│
├── screenshots/             # Additional screenshots (if needed)
│   └── failures/            # Failure screenshots from recorder
│       └── ...
│
└── src/                     # Source code
    ├── main/python/         # Python source files
    └── resources/           # Application resources
        ├── test_sessions/   # Active test creation sessions (temporary)
        │   ├── session_abc123.json
        │   └── session_def456.json
        ├── combined_dataset.json
        └── ...
```

---

## 📂 Directory Details

### **test_cases/**
**Purpose:** Store test case definitions in JSON format

**Structure:**
- `test_cases/builder/` - Test cases created via Test Builder
  - Contains JSON files with complete test case data
  - Includes prompts, generated code, metadata
  - Auto-generates `exports/` subdirectory with executable files

- `test_cases/recorder/` - Test cases created via Test Recorder (FUTURE)
  - Will contain recorded test sessions saved as test cases

**Storage Format:** JSON files
**Persistence:** ✅ Persistent (survives server restart)
**Created By:** `TestCaseBuilder` class

---

### **test_suites/**
**Purpose:** Store test suite definitions (collections of test cases)

**Structure:**
- `test_suites/builder/` - Test suites for Test Builder test cases
- `test_suites/recorder/` - Test suites for Test Recorder test cases

**Storage Format:** JSON files
**Persistence:** ✅ Persistent (survives server restart)
**Status:** 🚧 PLANNED (not yet implemented)

---

### **execution_results/**
**Purpose:** Store test execution results with complete details

**Structure:**
- `execution_results/recorder/` - Results from Test Recorder test execution
  - Execution status (passed/failed)
  - Duration, timestamps
  - Failure screenshots (only on failures)
  - Error messages
  - Step-by-step execution data

- `execution_results/builder/` - Results from Test Builder test execution
  - Same data structure as recorder
  - Linked to test case ID

**Storage Format:** JSON files with timestamps
**Persistence:** ✅ Persistent (survives server restart)
**Filename Pattern:** `{test_name}_{YYYYMMDD_HHMMSS}.json`

**Example File:**
```json
{
  "session_id": "abc123" or "test_case_id": "TC001",
  "test_name": "Producer Login Flow",
  "start_time": "2026-03-20T14:30:25",
  "end_time": "2026-03-20T14:30:45",
  "status": "passed",
  "duration_ms": 20555,
  "steps_executed": 5,
  "total_steps": 5,
  "failed_step": null,
  "error_message": null,
  "screenshots": [],
  "result_file": "/path/to/execution_results/recorder/Producer_Login_20260320_143025.json"
}
```

---

### **src/resources/test_sessions/**
**Purpose:** Active test creation sessions (temporary working files)

**Structure:**
- Stores in-progress test building sessions
- Each session has a unique ID
- Used by Test Builder multi-prompt workflow

**Storage Format:** JSON files
**Persistence:** ✅ Persistent but temporary (can be cleared)
**Created By:** `TestSessionManager` class

**Difference from test_cases:**
- `test_sessions/` = Work in progress (active editing)
- `test_cases/` = Saved, complete test cases (ready to execute)

---

## 🔄 Data Flow

### **Test Builder Workflow (Multi-Prompt)**

```
1. User creates session
   → TestSessionManager
   → Saves to: src/resources/test_sessions/session_{id}.json

2. User adds prompts, edits, previews code
   → Session updated in test_sessions/

3. User clicks "Save as Test Case"
   → TestCaseBuilder
   → Saves to: test_cases/builder/TC{num}_{name}.json
   → Auto-exports to: test_cases/builder/exports/{files}

4. User executes test case
   → TestSuiteRunner
   → Saves results to: execution_results/builder/TC{num}_{timestamp}.json
   → Saves screenshots to: execution_results/builder/screenshots/
```

### **Test Recorder Workflow**

```
1. User starts recording
   → RecorderHandler
   → Stores in memory (session)

2. User performs actions, generates code
   → Actions captured in session

3. User executes test
   → test_executor.py
   → Saves results to: execution_results/recorder/{name}_{timestamp}.json
   → Saves failure screenshots to: screenshots/failures/

4. Future: Save recorded session as test case
   → Will save to: test_cases/recorder/{name}.json
```

---

## ⚠️ Important Notes

### **Before Server Restart (Old Behavior):**
- ❌ Test Recorder execution results stored in Flask session (LOST on restart)
- ✅ Test Builder execution results saved to JSON files (PRESERVED)

### **After Fix (March 20, 2026):**
- ✅ Test Recorder execution results NOW saved to JSON files (PRESERVED)
- ✅ Test Builder execution results already saved to JSON files (PRESERVED)
- ✅ Both use proper folder structure

### **Backwards Compatibility:**
- Execution results still stored in Flask session for API responses
- But also saved to files for persistence
- No breaking changes to existing API

---

## 📊 Storage Summary

| Data Type | Location | Test Recorder | Test Builder | Persistent? |
|-----------|----------|---------------|--------------|-------------|
| **Test Cases** | `test_cases/{type}/` | 🚧 Future | ✅ Yes | ✅ Yes |
| **Test Suites** | `test_suites/{type}/` | 🚧 Future | 🚧 Future | ✅ Yes |
| **Execution Results** | `execution_results/{type}/` | ✅ Yes | ✅ Yes | ✅ Yes |
| **Active Sessions** | `src/resources/test_sessions/` | N/A | ✅ Yes | ⚠️ Temporary |
| **Exported Tests** | `test_cases/builder/exports/` | N/A | ✅ Yes | ✅ Yes |
| **Failure Screenshots** | `screenshots/failures/` or `execution_results/` | ✅ Yes | ✅ Yes | ✅ Yes |

---

## 🔧 Configuration

All directory paths are automatically created by the respective classes:

- **TestCaseBuilder**: Creates `test_cases/builder/` and `exports/`
- **TestSuiteRunner**: Creates `execution_results/builder/` and `screenshots/`
- **test_executor**: Creates `execution_results/recorder/` and `screenshots/failures/`
- **TestSessionManager**: Creates `src/resources/test_sessions/`

No manual configuration required! 🎉

---

## 🚀 Future Enhancements

1. **Test Recorder Test Cases** (High Priority)
   - Save recorded sessions to `test_cases/recorder/`
   - Reloadable and re-executable

2. **Test Suites** (Medium Priority)
   - Group related test cases
   - Save to `test_suites/builder/` and `test_suites/recorder/`

3. **Database Integration** (Q2 2026)
   - Migrate from JSON files to PostgreSQL/MongoDB
   - Keep folder structure as backup/export

---

**Status:** ✅ All folder structures implemented and operational as of March 20, 2026
