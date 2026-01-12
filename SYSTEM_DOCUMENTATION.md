# Web Automation System - Complete Documentation

**Last Updated:** November 23, 2025  
**Version:** 2.0

---

## Table of Contents
1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Technologies Used](#technologies-used)
4. [Frontend Details](#frontend-details)
5. [Backend Details](#backend-details)
6. [Features](#features)
7. [API Endpoints](#api-endpoints)
8. [Data Flow](#data-flow)
9. [Storage](#storage)
10. [Setup & Installation](#setup--installation)

---

## System Overview

The Web Automation System is an AI-powered test automation platform that helps users record, generate, manage, and execute Selenium test cases. It combines machine learning with web automation to provide intelligent code generation and test management capabilities.

### Key Capabilities
- **AI Code Generation**: Generate Selenium test code using trained language models
- **Browser Recording**: Record user interactions and convert them to test code
- **Test Management**: Organize, execute, and manage test suites
- **Code Snippets**: Save and reuse code snippets across projects
- **Live Browser Control**: Execute tests in real-time with visual feedback

---

## Architecture

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────┐
│                    Web Browser (Client)                  │
│  ┌────────────────────────────────────────────────────┐ │
│  │         Frontend (HTML/CSS/JavaScript)             │ │
│  │  - Single Page Application (SPA)                   │ │
│  │  - No frameworks (Vanilla JS)                      │ │
│  │  - LocalStorage for client-side data               │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                           ↕ HTTP/REST API
┌─────────────────────────────────────────────────────────┐
│              Backend Server (Python/Flask)               │
│  ┌────────────────────────────────────────────────────┐ │
│  │  Flask Application (api_server_improved.py)        │ │
│  │  - REST API Endpoints                              │ │
│  │  - Session Management                              │ │
│  │  - Browser Control (Selenium WebDriver)            │ │
│  └────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────┐ │
│  │  AI Model (N-gram Language Model)                  │ │
│  │  - Code Generation                                 │ │
│  │  - Smart Locator Suggestions                       │ │
│  │  - Action Recommendations                          │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                           ↕
┌─────────────────────────────────────────────────────────┐
│              Selenium WebDriver (Chrome)                 │
│  - Browser Automation                                   │
│  - Test Execution                                       │
│  - DOM Interaction                                      │
└─────────────────────────────────────────────────────────┘
```

### Component Interaction Flow
1. **User** interacts with the web interface
2. **Frontend** sends HTTP requests to the backend API
3. **Backend** processes requests and uses AI model or Selenium
4. **Response** is sent back to frontend
5. **Frontend** updates UI and stores data in localStorage

---

## Technologies Used

### Frontend Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **HTML5** | Latest | Structure and markup |
| **CSS3** | Latest | Styling and animations |
| **JavaScript (ES6+)** | Latest | Application logic |
| **Prism.js** | Latest | Syntax highlighting |
| **LocalStorage API** | Browser Native | Client-side data persistence |
| **Fetch API** | Browser Native | HTTP requests |

**Key Frontend Characteristics:**
- ✅ No frontend frameworks (React, Vue, Angular)
- ✅ Pure Vanilla JavaScript
- ✅ CSS Custom Properties for theming
- ✅ Responsive design with Flexbox/Grid
- ✅ Dark mode support
- ✅ Single-page application (SPA) architecture

### Backend Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.8+ | Primary programming language |
| **Flask** | 2.x | Web framework and REST API |
| **Waitress** | Latest | Production WSGI server |
| **Selenium WebDriver** | 4.x | Browser automation |
| **ChromeDriver** | Latest | Chrome browser control |
| **Pickle** | Built-in | Model serialization |
| **JSON** | Built-in | Data interchange format |

**Key Backend Characteristics:**
- ✅ RESTful API architecture
- ✅ Stateful session management
- ✅ In-memory data storage
- ✅ N-gram based language model
- ✅ CORS enabled for localhost

### AI Implementation

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Tokenizer** | tiktoken (cl100k_base) | Text tokenization (GPT-4 tokenizer library) |
| **Language Model** | Custom N-gram (4-gram) | Statistical code generation |
| **Model Storage** | Pickle (.pkl file) | Local model persistence |
| **Training** | NumPy + Python | Custom implementation |

**AI Architecture:**
- ❌ **No External AI Services**: Completely offline, no API calls
- ✅ **Custom N-gram Model**: Trained locally on Selenium code datasets
- ✅ **Statistical Predictions**: Uses probability distributions from training data
- ✅ **Template-based Fallbacks**: Predefined patterns for common actions
- ✅ **No Internet Required**: All AI runs locally on your machine
- ✅ **No API Keys Needed**: No OpenAI, Anthropic, HuggingFace, or cloud dependencies

**How It Works:**
1. **Training**: Model learns patterns from local JSON datasets containing Selenium code examples
2. **Tokenization**: Uses tiktoken library (offline) to convert text to tokens
3. **Prediction**: N-gram model predicts next token based on previous tokens using probability counts
4. **Generation**: Combines statistical predictions with template-based patterns
5. **Inference**: All code generation runs locally using `selenium_ngram_model.pkl`

**Model Details:**
- **File**: `selenium_ngram_model.pkl` (local pickle file)
- **Type**: 4-gram statistical language model
- **Implementation**: `train_simple.py` (custom Python class)
- **Inference**: `inference_improved.py` (enhanced generator with templates)
- **Datasets**: `common-web-actions-dataset.json`, `element-locator-patterns.json`, `selenium-methods-dataset.json`

**Key Advantage**: This is a **completely self-contained AI system** with no external dependencies, API costs, or internet requirements. Perfect for enterprise environments with strict security policies.

---

## Frontend Details

### File Structure
```
src/main/resources/web/
├── index.html              # Main application (5,249 lines)
├── recorder-inject.js      # Browser recorder script
└── README.md              # Web interface documentation
```

### index.html - Structure

**Lines 1-1000: HTML Structure & CSS Styles**
- Root variables for theming
- Dark mode styles
- Responsive layout
- Custom scrollbars
- Modal styles
- Dashboard metrics cards
- Navigation sidebar

**Lines 1001-2000: HTML Content**
- Dashboard page (metrics, charts, activity)
- Code Generator tab
- Browser Control tab
- Test Recorder tab
- Test Suite Management tab
- Test Runner Configuration tab
- Code Snippet Library tab

**Lines 2001-5249: JavaScript Application Logic**
- Global variables and configuration
- Navigation functions
- Dark mode toggle
- Code generation functions
- Browser control functions
- Recording functions
- Test suite management
- Code snippet library
- Data override modals
- Test execution
- Dashboard updates
- Event listeners

### Frontend Features

#### 1. Navigation System
```javascript
function navigateTo(page) {
    // Hide all pages
    // Show selected page
    // Update sidebar active state
    // Update URL hash
}
```

#### 2. Dark Mode Support
```javascript
function toggleDarkMode() {
    // Toggle dark-mode class on body
    // Save preference to localStorage
    // Update all UI elements dynamically
}
```

#### 3. API Communication
```javascript
const API_URL = 'http://localhost:5000';

async function callAPI(endpoint, method, data) {
    const response = await fetch(`${API_URL}${endpoint}`, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    return await response.json();
}
```

#### 4. LocalStorage Management
```javascript
// Code Snippets Storage
localStorage.setItem('codeSnippets', JSON.stringify(snippets));
const snippets = JSON.parse(localStorage.getItem('codeSnippets') || '[]');

// Dark Mode Preference
localStorage.setItem('darkMode', 'enabled');
```

---

## Backend Details

### File Structure
```
src/main/python/
├── api_server_improved.py  # Main Flask application (1,518 lines)
├── inference_improved.py   # AI model inference
├── smart_locator_generator.py  # Locator suggestions
└── browser_executor.py     # Browser automation
```

### api_server_improved.py - Structure

**Lines 1-50: Imports and Configuration**
```python
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from selenium import webdriver
import pickle
import logging
```

**Lines 51-200: Flask App Setup**
```python
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# Global variables
generator = None  # AI model instance
browser_manager = None  # Selenium browser instance
recorded_sessions = {}  # In-memory test sessions
active_session_id = None
```

**Lines 201-800: API Endpoints**
- Health check
- Code generation
- Locator suggestions
- Action recommendations
- Browser control
- Recording endpoints
- Test suite management

**Lines 801-1518: Helper Functions & Server Startup**
- Session management
- Code generation logic
- Browser initialization
- Test execution
- Server configuration

### Backend Architecture Patterns

#### 1. Session Management
```python
recorded_sessions = {
    'session_id_123': {
        'id': 'session_id_123',
        'name': 'Login Test',
        'url': 'https://example.com',
        'module': 'Authentication',
        'actions': [
            {'type': 'click', 'element': '#login-btn', 'timestamp': 1234567890},
            {'type': 'input', 'element': '#username', 'value': 'user@example.com'}
        ],
        'created_at': 1234567890,
        'action_count': 2
    }
}
```

#### 2. Browser Control
```python
class BrowserManager:
    def __init__(self):
        self.driver = None
        self.is_initialized = False
    
    def initialize(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        self.driver = webdriver.Chrome(options=options)
        self.is_initialized = True
    
    def execute_code(self, code):
        # Execute Selenium code in browser
        exec(code)
```

#### 3. AI Model Integration
```python
class ImprovedSeleniumGenerator:
    def __init__(self, model_path):
        with open(model_path, 'rb') as f:
            self.model_data = pickle.load(f)
        self.ngram_model = self.model_data['ngram_model']
    
    def generate_code(self, prompt, max_length=150):
        # Generate Selenium code using N-gram model
        tokens = self.tokenize(prompt)
        generated = self.predict_next_tokens(tokens, max_length)
        return self.detokenize(generated)
```

---

## Features

### 1. Dashboard
**Purpose:** Overview of system metrics and activity

**Features:**
- Total requests/tests generated count
- Tests passed/failed statistics
- Recent test results timeline
- Activity log
- Quick access cards

**Data Sources:**
- Frontend: localStorage for persistence
- Backend: In-memory stats from test executions
- Updates: Real-time after each test execution

### 2. Code Generator
**Purpose:** AI-powered Selenium code generation

**Features:**
- Natural language prompt input
- Multi-language support (Java, Python, JavaScript, C#)
- Syntax highlighting
- Copy to clipboard
- Download generated code
- Response time tracking

**API Endpoint:** `POST /generate`

**Request:**
```json
{
  "prompt": "click login button",
  "language": "java"
}
```

**Response:**
```json
{
  "code": "driver.findElement(By.id(\"login-btn\")).click();",
  "confidence": 0.85
}
```

### 3. Browser Control
**Purpose:** Execute code in live browser

**Features:**
- Initialize browser session
- Execute Selenium code
- View execution results
- Error handling
- Close browser

**API Endpoints:**
- `POST /browser/initialize` - Start Chrome browser
- `POST /browser/execute` - Run Selenium code
- `POST /browser/close` - Close browser

**Workflow:**
1. User clicks "Initialize Browser"
2. Backend starts ChromeDriver
3. User enters/generates Selenium code
4. User clicks "Execute in Browser"
5. Code runs in live browser
6. Results displayed in UI

### 4. Test Recorder
**Purpose:** Record browser interactions as test steps

**Features:**
- Module-based organization
- URL navigation with script injection
- Action recording (click, input, select, etc.)
- Live action preview
- Start new test in same browser
- Stop recording (keeps browser open)

**API Endpoints:**
- `POST /recorder/start` - Start recording session
- `POST /recorder/navigate` - Navigate and inject recorder script
- `POST /recorder/record-action` - Save recorded action
- `POST /recorder/stop` - Stop recording
- `POST /recorder/new-test` - Start new test in same browser

**Workflow:**
1. User enters test name, URL, and module
2. Clicks "Start Recording"
3. Backend initializes browser and injects recorder script
4. User interacts with website
5. Actions are captured and sent to backend
6. Actions displayed in real-time in UI
7. User clicks "Stop Recording"
8. Test session saved for later use

**Module Support:**
- Organize tests by module (e.g., "Login", "Checkout", "Admin")
- Filter tests by module
- Autocomplete for existing modules

### 5. Test Suite Management
**Purpose:** Manage and execute recorded tests

**Features:**
- View all recorded test cases
- Module-based filtering
- Select all / individual selection
- Bulk delete with count
- Individual test deletion
- View generated test code
- Execute individual tests
- Execute entire test suite
- Data override capabilities
- Clear all tests

**API Endpoints:**
- `GET /recorder/sessions` - List all test cases
- `POST /recorder/generate-test` - Generate code from session
- `POST /recorder/execute-test` - Execute single test
- `POST /recorder/execute-suite` - Execute all tests
- `POST /recorder/delete-session` - Delete specific test
- `POST /recorder/clear-sessions` - Clear all tests

**Test Case Structure:**
```javascript
{
  id: "unique_session_id",
  name: "Login Test",
  url: "https://example.com/login",
  module: "Authentication",
  actions: [...],
  created_at: 1234567890,
  action_count: 15
}
```

**Selection Features:**
- Checkbox on each test card
- "Select All" checkbox with indeterminate state
- "Delete Selected (N)" button appears when tests selected
- Dashboard count updates after deletion

### 6. Code Snippet Library
**Purpose:** Save and organize reusable code snippets

**Features:**
- Save snippets with metadata
- Upload snippets from files (.java, .py, .js, .cs, .txt)
- Language detection
- Tag-based organization
- Search and filter by language/tags
- View snippet with syntax highlighting
- Copy to clipboard
- Select all / individual selection
- Bulk delete
- Use snippet (load into output)
- Delete individual snippets

**Storage:** Browser localStorage (key: 'codeSnippets')

**Snippet Structure:**
```javascript
{
  id: 1234567890,
  title: "Login Helper",
  language: "java",
  tags: ["selenium", "login", "helper"],
  description: "Helper method for login functionality",
  code: "public void login(String user, String pass) {...}",
  createdAt: "2025-11-23T10:30:00.000Z",
  date: "11/23/2025, 10:30:00 AM"
}
```

**Selection Features:**
- Checkbox on each snippet card
- "Select All" checkbox with indeterminate state
- "Delete Selected (N)" button appears when snippets selected

### 7. Test Runner Configuration
**Purpose:** Configure test execution frameworks

**Supported Frameworks:**
- **JUnit** (Java) - Maven-based execution
- **TestNG** (Java) - Maven-based execution
- **pytest** (Python) - Command-line execution
- **unittest** (Python) - Built-in module
- **Jest** (JavaScript) - npm-based execution
- **Mocha** (JavaScript) - npm-based execution

**Features:**
- Framework selection dropdown
- Test file path input
- Test method/function name input
- Additional arguments input
- Dynamic command generation
- Setup instructions

### 8. Data Override Modal
**Purpose:** Customize test data before execution

**Features:**
- Extract input fields from recorded actions
- Override values for each input
- Execute test with custom data
- Validation and error handling

**Workflow:**
1. User selects test to execute
2. System extracts all input actions
3. Modal shows form with current values
4. User modifies values
5. Test executes with new data

---

## API Endpoints

### Complete Endpoint Reference

#### Health & Status
```
GET /health
Response: { "status": "healthy", "model_loaded": true }
```

#### Code Generation
```
POST /generate
Request: { "prompt": "string", "language": "java|python|javascript|csharp" }
Response: { "code": "string", "confidence": 0.85 }
```

#### Locator Suggestions
```
POST /suggest-locator
Request: { "html": "<div id='test'>...</div>" }
Response: {
  "recommended_locators": ["By.id('test')", "By.cssSelector('#test')"],
  "element_analysis": { "has_id": true, "has_name": false, "has_class": false }
}
```

#### Action Recommendations
```
POST /suggest-action
Request: { "element_type": "button", "context": "login page" }
Response: { "actions": ["click()", "submit()"], "recommended": "click()" }
```

#### Browser Control
```
POST /browser/initialize
Response: { "success": true, "message": "Browser initialized" }

POST /browser/execute
Request: { "code": "driver.get('https://example.com')" }
Response: { "success": true, "result": "..." }

POST /browser/close
Response: { "success": true, "message": "Browser closed" }
```

#### Test Recording
```
POST /recorder/start
Request: { "name": "string", "url": "string", "module": "string" }
Response: { "success": true, "session_id": "string" }

POST /recorder/navigate
Request: { "session_id": "string", "url": "string" }
Response: { "success": true }

POST /recorder/record-action
Request: {
  "session_id": "string",
  "action": { "type": "click", "element": "#btn", "value": "" }
}
Response: { "success": true }

POST /recorder/stop
Request: { "session_id": "string" }
Response: { "success": true }

POST /recorder/new-test
Request: { "name": "string", "url": "string", "module": "string" }
Response: { "success": true, "session_id": "string" }
```

#### Test Suite Management
```
GET /recorder/sessions
Response: { "success": true, "sessions": [...] }

POST /recorder/generate-test
Request: { "session_id": "string", "test_name": "string" }
Response: { "success": true, "code": "string" }

POST /recorder/execute-test
Request: { "session_id": "string", "data_overrides": {...} }
Response: { "success": true, "result": {...} }

POST /recorder/execute-suite
Request: { "module": "string" }  // optional filter
Response: { "success": true, "results": [...] }

POST /recorder/delete-session
Request: { "session_id": "string" }
Response: { "success": true, "message": "Session deleted" }

POST /recorder/clear-sessions
Response: { "success": true, "message": "All sessions cleared" }
```

---

## Data Flow

### Recording Flow
```
User Browser
    ↓ (1) Start Recording
Backend (POST /recorder/start)
    ↓ (2) Create session, Initialize browser
Browser (Chrome via Selenium)
    ↓ (3) Navigate to URL
Backend (Inject recorder-inject.js)
    ↓ (4) Script attached to page
User Interaction (Click, Type, etc.)
    ↓ (5) Event captured by injected script
Backend (POST /recorder/record-action)
    ↓ (6) Action saved to session
Frontend
    ↓ (7) Display action in real-time
Repeat steps 5-7 for each action
    ↓ (8) Stop Recording
Backend (Session saved in memory)
```

### Test Execution Flow
```
User
    ↓ (1) Click Execute Test
Frontend (POST /recorder/execute-test)
    ↓ (2) Send session_id + data_overrides
Backend
    ↓ (3) Fetch session from recorded_sessions
    ↓ (4) Generate Selenium code from actions
    ↓ (5) Apply data overrides
    ↓ (6) Initialize browser
Browser
    ↓ (7) Execute generated code
    ↓ (8) Capture screenshots/errors
Backend
    ↓ (9) Collect results
Frontend
    ↓ (10) Display results + update dashboard
```

### Code Generation Flow
```
User
    ↓ (1) Enter prompt
Frontend (POST /generate)
    ↓ (2) Send prompt + language
Backend
    ↓ (3) Load AI model
AI Model (N-gram)
    ↓ (4) Tokenize prompt
    ↓ (5) Generate tokens using N-gram probabilities
    ↓ (6) Detokenize to code
Backend
    ↓ (7) Format code for target language
Frontend
    ↓ (8) Display with syntax highlighting
```

---

## Storage

### Backend Storage (In-Memory)
```python
# Session Storage
recorded_sessions = {
    'session_id': {
        'id': 'string',
        'name': 'string',
        'url': 'string',
        'module': 'string',
        'actions': [],
        'created_at': timestamp,
        'action_count': int
    }
}

# Browser Instance
browser_manager = BrowserManager()

# AI Model
generator = ImprovedSeleniumGenerator(MODEL_PATH)
```

**Characteristics:**
- ❌ Data lost on server restart
- ✅ Fast access
- ✅ No database required
- ⚠️ Limited to server memory

### Frontend Storage (localStorage)
```javascript
// Code Snippets
localStorage.setItem('codeSnippets', JSON.stringify([
    {
        id: 1234567890,
        title: 'string',
        language: 'java',
        tags: ['tag1', 'tag2'],
        description: 'string',
        code: 'string',
        createdAt: 'ISO date string',
        date: 'locale date string'
    }
]));

// Dark Mode Preference
localStorage.setItem('darkMode', 'enabled|disabled');

// User Stats (if needed)
localStorage.setItem('userStats', JSON.stringify({
    totalTests: 0,
    lastVisit: 'date'
}));
```

**Characteristics:**
- ✅ Persists across browser sessions
- ✅ Domain-specific (localhost:5000)
- ⚠️ ~5-10MB storage limit
- ⚠️ Cleared when user clears browser data

---

## Setup & Installation

### Prerequisites
```bash
# Python 3.8 or higher
python --version

# Chrome Browser
# ChromeDriver (matching Chrome version)
```

### Backend Setup
```bash
# 1. Install Python dependencies
pip install flask flask-cors selenium waitress

# 2. Ensure model file exists
# selenium_ngram_model.pkl should be in project root

# 3. Start server
python src/main/python/api_server_improved.py

# Server starts on http://localhost:5000
```

### Frontend Access
```bash
# Open browser and navigate to:
http://localhost:5000

# Or open index.html directly in browser
# (Some features require backend server)
```

### Configuration
```python
# api_server_improved.py
PORT = 5000
HOST = '0.0.0.0'
MODEL_PATH = 'selenium_ngram_model.pkl'

# Enable CORS for development
CORS(app)
```

---

## Feature Summary Table

| Feature | Frontend Tech | Backend Tech | Storage | APIs Used |
|---------|---------------|--------------|---------|-----------|
| Dashboard | HTML/CSS/JS | - | localStorage | - |
| Code Generator | JS/Fetch API | Flask/AI Model | - | /generate |
| Browser Control | JS/Fetch API | Flask/Selenium | In-memory | /browser/* |
| Test Recorder | JS/Fetch API | Flask/Selenium | In-memory | /recorder/* |
| Test Suite Mgmt | JS/Fetch API | Flask/Selenium | In-memory | /recorder/* |
| Code Snippets | JS/localStorage | - | localStorage | - |
| Test Runner Config | JS | - | - | - |
| Dark Mode | CSS/JS | - | localStorage | - |

---

## Development Notes

### Adding New Features

**Frontend:**
1. Add HTML structure to appropriate section in `index.html`
2. Add CSS styles in `<style>` section
3. Add JavaScript functions in `<script>` section
4. Update navigation if needed

**Backend:**
1. Add endpoint in `api_server_improved.py`
2. Define route with `@app.route()`
3. Implement handler function
4. Return JSON response
5. Update API documentation in startup message

### Code Style Guidelines

**Frontend:**
- Use `camelCase` for JavaScript variables/functions
- Use `kebab-case` for CSS classes
- Use template literals for HTML generation
- Always use `const` or `let` (never `var`)

**Backend:**
- Use `snake_case` for Python variables/functions
- Use docstrings for all functions
- Return consistent JSON structure: `{ "success": bool, "data": any, "error": string }`
- Log important operations

---

## Security Considerations

⚠️ **This is a development tool - NOT production-ready**

**Current Security Limitations:**
- No authentication/authorization
- No input validation/sanitization
- Eval/exec used for code execution
- CORS fully open
- No HTTPS
- localStorage unencrypted
- No rate limiting

**For Production Use:**
- Add user authentication
- Implement input validation
- Use sandboxed code execution
- Configure CORS properly
- Enable HTTPS/SSL
- Encrypt sensitive data
- Add rate limiting
- Use database instead of in-memory storage

---

## Troubleshooting

### Common Issues

**Issue:** Browser doesn't open
- Check ChromeDriver version matches Chrome
- Ensure ChromeDriver is in PATH
- Check Selenium version compatibility

**Issue:** 404 errors on API calls
- Verify backend server is running
- Check API_URL in frontend (should be http://localhost:5000)
- Restart server after code changes

**Issue:** Code snippets not appearing
- Open browser console (F12) for errors
- Check localStorage is enabled
- Verify snippet format is correct

**Issue:** Dark mode not working
- Clear localStorage and retry
- Check browser supports CSS custom properties
- Refresh browser cache

---

## Performance Metrics

**Typical Response Times:**
- Code Generation: 500-2000ms
- Browser Initialize: 2000-4000ms
- Execute Code: 100-1000ms (depends on code complexity)
- Record Action: <100ms
- Load Test Cases: <200ms

**Resource Usage:**
- Frontend: ~5-10MB (DOM + localStorage)
- Backend: ~100-200MB (Python + Model + Browser)
- Browser Instance: ~200-500MB (Chrome)

---

## Future Enhancements

**Planned Features:**
- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] User authentication and multi-user support
- [ ] Test scheduling and CI/CD integration
- [ ] Video recording of test execution
- [ ] Better AI models (GPT integration)
- [ ] Cloud deployment support
- [ ] Mobile app testing support
- [ ] API testing capabilities
- [ ] Test analytics and reporting
- [ ] Export tests to various formats (JUnit XML, Allure, etc.)

---

## Version History

**v2.0 (2025-11-23)**
- ✅ Added module-based test organization
- ✅ Added bulk delete for tests and snippets
- ✅ Added checkbox selection for tests
- ✅ Added code snippet upload from files
- ✅ Fixed dark mode visibility issues
- ✅ Added delete-session API endpoint
- ✅ Improved error handling and logging

**v1.0 (Initial Release)**
- ✅ Basic code generation
- ✅ Browser control
- ✅ Test recording
- ✅ Test suite management
- ✅ Code snippet library

---

## Credits & License

**Technologies Used:**
- Flask (BSD License)
- Selenium (Apache License 2.0)
- Prism.js (MIT License)
- Chrome/ChromeDriver (Google)

**Model Training:**
- Custom N-gram model trained on Selenium documentation and examples

---

**End of Documentation**

For support or questions, please refer to the source code comments or consult the API endpoint documentation within the application.