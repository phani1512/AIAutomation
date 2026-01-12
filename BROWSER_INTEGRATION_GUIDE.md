# Browser Integration Guide

## Overview

The Selenium SLM project now includes **real browser execution** capability! You can now generate test automation code from natural language prompts and automatically execute it in a real browser (Chrome, Firefox, or Edge).

## Features

### 🌐 Browser Execution
- **Multi-Browser Support**: Chrome, Firefox, Edge
- **Headless Mode**: Run tests without visible browser window
- **Real-Time Execution**: Execute generated code immediately
- **Auto Driver Management**: Automatically downloads and manages browser drivers

### 🤖 Code Generation + Execution
- Generate Selenium code from prompts
- Execute code in real browser with one click
- View execution results and page information
- Take screenshots of executed tests

## Installation

### 1. Install Python Dependencies

```powershell
pip install -r requirements.txt
```

This will install:
- `selenium>=4.15.0` - Browser automation framework
- `webdriver-manager>=4.0.0` - Automatic driver management
- `flask>=2.3.0` - Web API server
- `flask-cors>=4.0.0` - CORS support

### 2. Browser Requirements

**Chrome** (Recommended):
- Install Chrome browser: https://www.google.com/chrome/
- Driver will be auto-downloaded

**Firefox**:
- Install Firefox browser: https://www.mozilla.org/firefox/
- Driver will be auto-downloaded

**Edge**:
- Pre-installed on Windows 10/11
- Driver will be auto-downloaded

## Usage

### Starting the Server

```powershell
python src/main/python/api_server_improved.py
```

Server will start on: http://localhost:5000

### Web Interface

Open browser and navigate to: **http://localhost:5000**

#### Browser Tab Workflow:

1. **Initialize Browser**
   - Select browser type (Chrome/Firefox/Edge)
   - Optional: Enable headless mode
   - Click "🚀 Initialize Browser"
   - Wait for "✅ Browser Ready" confirmation

2. **Execute Tests**
   - Enter target URL (e.g., https://example.com)
   - Enter test prompt (e.g., "click submit button")
   - Click "▶️ Execute in Browser"
   - View generated code and execution results

3. **Close Browser**
   - Click "⏹️ Close Browser" when done

### Example Prompts

**Navigation:**
- "navigate to https://example.com"
- "open login page"

**Click Actions:**
- "click login button"
- "click submit button"
- "click on search icon"

**Input Actions:**
- "enter username in input field"
- "type password in password field"
- "enter email in email field"

**Dropdown Selection:**
- "select country from dropdown"
- "select United States from country dropdown"

**Verification:**
- "verify page title"
- "verify success message"
- "check if element is displayed"

**Waits:**
- "wait for element to be visible"
- "wait for button to be clickable"

## API Endpoints

### Browser Control Endpoints

#### Initialize Browser
```http
POST /browser/initialize
Content-Type: application/json

{
  "browser": "chrome",
  "headless": false
}
```

**Response:**
```json
{
  "success": true,
  "browser": "chrome",
  "headless": false,
  "message": "Browser initialized successfully"
}
```

#### Execute Code
```http
POST /browser/execute
Content-Type: application/json

{
  "code": "// Generated Selenium code",
  "url": "https://example.com"
}
```

**Response:**
```json
{
  "success": true,
  "executed_code": "# Python code",
  "current_url": "https://example.com",
  "page_title": "Example Domain",
  "result": {
    "executed": true,
    "message": "Code executed successfully"
  }
}
```

#### Generate + Execute (Combined)
```http
POST /generate
Content-Type: application/json

{
  "prompt": "click login button",
  "execute": true,
  "url": "https://example.com"
}
```

**Response:**
```json
{
  "prompt": "click login button",
  "generated": "// Java Selenium code",
  "tokens_generated": 25,
  "execution": {
    "success": true,
    "executed_code": "# Python code",
    "current_url": "https://example.com",
    "page_title": "Example Domain"
  }
}
```

#### Get Browser Info
```http
GET /browser/info
```

**Response:**
```json
{
  "url": "https://example.com",
  "title": "Example Domain",
  "page_source_length": 1256
}
```

#### Take Screenshot
```http
POST /browser/screenshot
Content-Type: application/json

{
  "filename": "test_screenshot.png"
}
```

**Response:**
```json
{
  "success": true,
  "filepath": "test_screenshot.png",
  "message": "Screenshot saved to test_screenshot.png"
}
```

#### Close Browser
```http
POST /browser/close
```

**Response:**
```json
{
  "success": true,
  "message": "Browser closed successfully"
}
```

## Architecture

### Components

1. **Browser Executor** (`browser_executor.py`)
   - Manages WebDriver instances
   - Converts Java-style code to Python
   - Executes Selenium commands
   - Handles screenshots and page info

2. **API Server** (`api_server_improved.py`)
   - Flask REST API
   - Browser control endpoints
   - Code generation endpoints
   - CORS enabled for web interface

3. **Web Interface** (`index.html`)
   - Browser tab for execution controls
   - Real-time status updates
   - Multi-browser support
   - Execution result display

### Code Conversion

The system automatically converts generated Java-style Selenium code to Python for execution:

**Java Input:**
```java
WebElement button = driver.findElement(By.id("loginBtn"));
button.click();
```

**Python Output:**
```python
from selenium.webdriver.common.by import By
element = driver.find_element(By.ID, "loginBtn")
element.click()
```

## Troubleshooting

### Browser Not Starting

**Issue**: "Failed to initialize browser"

**Solutions**:
1. Install the browser (Chrome/Firefox/Edge)
2. Check internet connection (driver download)
3. Run as administrator if permission denied
4. Check antivirus/firewall settings

### WebDriver Issues

**Issue**: "WebDriver not found"

**Solution**: The `webdriver-manager` library automatically downloads drivers. Ensure:
- Internet connection is active
- No proxy blocking downloads
- Sufficient disk space

### Execution Errors

**Issue**: "Element not found" during execution

**Solutions**:
- Ensure correct URL is provided
- Add wait time for page load
- Verify element locators are correct
- Check if page requires login/authentication

### Port Already in Use

**Issue**: "Port 5000 is already in use"

**Solution**:
```powershell
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID with actual number)
taskkill /PID <PID> /F
```

## Best Practices

### 1. Always Initialize Browser First
Before executing tests, always initialize the browser using the "Initialize Browser" button or API endpoint.

### 2. Close Browser When Done
Always close the browser after testing to free resources.

### 3. Use Headless Mode for CI/CD
For automated testing pipelines, enable headless mode to avoid GUI overhead.

### 4. Verify URLs
Always provide complete URLs with protocol (https://) when navigating.

### 5. Handle Waits Properly
For dynamic content, use wait prompts:
- "wait for element to be visible"
- "wait for page to load"

## Example Workflow

### Complete Test Execution

1. **Start Server**
```powershell
python src/main/python/api_server_improved.py
```

2. **Open Web Interface**
Navigate to: http://localhost:5000

3. **Initialize Browser**
- Browser Tab → Select "Chrome"
- Click "🚀 Initialize Browser"
- Wait for "✅ Browser Ready"

4. **Execute Test**
- URL: `https://www.example.com`
- Prompt: `click on the "More information..." link`
- Click "▶️ Execute in Browser"

5. **View Results**
- See generated code
- Check execution status
- View current URL and page title

6. **Close Browser**
- Click "⏹️ Close Browser"

## Advanced Usage

### Programmatic API Usage (Python)

```python
import requests

API_URL = "http://localhost:5000"

# Initialize browser
response = requests.post(f"{API_URL}/browser/initialize", json={
    "browser": "chrome",
    "headless": True
})
print(response.json())

# Execute test
response = requests.post(f"{API_URL}/generate", json={
    "prompt": "click login button",
    "execute": True,
    "url": "https://example.com"
})
result = response.json()
print("Generated:", result['generated'])
print("Execution:", result['execution'])

# Close browser
requests.post(f"{API_URL}/browser/close")
```

### Programmatic API Usage (curl)

```bash
# Initialize browser
curl -X POST http://localhost:5000/browser/initialize \
  -H "Content-Type: application/json" \
  -d '{"browser":"chrome","headless":false}'

# Execute test
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt":"click submit button","execute":true,"url":"https://example.com"}'

# Close browser
curl -X POST http://localhost:5000/browser/close
```

## Limitations

1. **Java to Python Conversion**: Complex Java code might not convert perfectly
2. **Element Timing**: Fast execution may fail on slow-loading pages
3. **Authentication**: Cannot handle OAuth or complex authentication flows automatically
4. **File Downloads**: File download handling not implemented
5. **Multiple Windows**: Window switching limited to basic scenarios

## Future Enhancements

- [ ] Screenshot capture after each action
- [ ] Video recording of test execution
- [ ] Multi-tab/window support
- [ ] File upload/download handling
- [ ] Cookie and session management
- [ ] Custom wait conditions
- [ ] Page Object Model generation
- [ ] Test report generation
- [ ] Parallel execution support

## Support

For issues or questions:
1. Check server logs for error messages
2. Verify all dependencies are installed
3. Ensure browser is installed
4. Check network/firewall settings
5. Review API endpoint documentation

---

**Version**: 2.0.0
**Last Updated**: November 2025
**License**: MIT
