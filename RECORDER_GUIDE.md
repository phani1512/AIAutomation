# 🎬 Selenium SLM Recorder Feature

## Overview
The Selenium SLM now includes a powerful **Action Recorder** that captures manual browser interactions and automatically generates test automation code with AI-suggested locators.

## Features

### 1. **🔴 Recording Tab**
- Start/stop recording sessions
- Capture user interactions in real-time
- AI-powered locator suggestions
- Visual action list with step-by-step breakdown

### 2. **📋 Test Cases Tab**
- View all recorded test sessions
- Browse saved test cases
- Execute tests directly from the UI
- Track creation date, URL, and action count

### 3. **🤖 AI-Enhanced Locators**
- Automatically suggests optimal element locators
- Provides alternative locator options
- Uses trained SLM model for intelligent suggestions
- Prioritizes stable, maintainable selectors

## How to Use

### Step 1: Start Recording
1. Navigate to the **🎬 Recorder** tab
2. Enter a **test name** (e.g., "Login Test")
3. Enter the **starting URL** (e.g., "https://example.com")
4. Click **🔴 Start Recording**

### Step 2: Interact with Browser
- A browser window will open
- Manually perform your test actions:
  - Click buttons
  - Type in input fields
  - Select from dropdowns
  - Navigate between pages
- All actions are captured automatically

### Step 3: Stop Recording
- Click **⏹️ Stop Recording** when done
- Review captured actions in the action list
- Each action shows:
  - Step number
  - Action type (click, input, select)
  - AI-suggested locator
  - Values (for inputs/selects)

### Step 4: Generate Test Code
- Click **🚀 Generate Test Code**
- Complete Java test class is generated
- Includes:
  - WebDriver setup
  - Test method with all recorded steps
  - Teardown method
  - TestNG annotations

### Step 5: View & Execute
- Switch to **📋 Test Cases** tab
- See all saved test cases
- Click **👁️ View Code** to see generated test
- Click **▶️ Execute** to run the test

## API Endpoints

### Recorder Endpoints
```
POST /recorder/start           - Start new recording session
POST /recorder/record-action   - Record a user action
POST /recorder/stop            - Stop recording
POST /recorder/generate-test   - Generate test code from session
GET  /recorder/sessions        - List all recorded sessions
GET  /recorder/session/<id>    - Get specific session details
```

## Architecture

### Backend Components
1. **api_server_improved.py**
   - Recorder session management
   - In-memory storage of actions
   - Test code generation endpoint

2. **browser_executor.py**
   - Browser automation
   - Script injection for recording
   - Event capture support

3. **ai_recorder.py**
   - AI-enhanced action recording
   - Locator suggestion integration
   - Test code generation logic

### Frontend Components
1. **Recorder Tab**
   - Session configuration
   - Recording controls
   - Action list display

2. **Test Cases Tab**
   - Session browsing
   - Code viewer
   - Execution controls

3. **recorder-inject.js**
   - Browser-side event capture
   - Real-time action monitoring
   - Visual feedback overlay

## Captured Actions

### Click Events
- Buttons
- Links
- Any clickable elements
- Records: element locator

### Input Events
- Text fields
- Textareas
- Password fields
- Records: element locator + value

### Select Events
- Dropdown menus
- Multi-select lists
- Records: element locator + selected option

## Generated Test Code

Example output:
```java
package com.testing.tests;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.chrome.ChromeDriver;
import org.testng.annotations.*;

public class LoginTest {
    private WebDriver driver;
    
    @BeforeMethod
    public void setUp() {
        driver = new ChromeDriver();
        driver.get("https://example.com");
    }
    
    @Test
    public void recordedTest() {
        // Step 1: click
        driver.findElement(By.id("username")).click();
        
        // Step 2: input
        driver.findElement(By.id("username")).sendKeys("testuser");
        
        // Step 3: click
        driver.findElement(By.id("loginBtn")).click();
    }
    
    @AfterMethod
    public void tearDown() {
        if (driver != null) {
            driver.quit();
        }
    }
}
```

## Dark Mode Support
- Full dark mode compatibility
- Smooth theme transitions
- Persistent preference storage
- Toggle button in header

## Tips & Best Practices

### Recording
- ✅ Start with a clean browser state
- ✅ Perform actions slowly and deliberately
- ✅ Use meaningful test names
- ✅ Record complete user flows
- ❌ Avoid recording navigation away from test domain
- ❌ Don't include unnecessary actions

### Locators
- AI suggests best locators based on:
  - Element attributes (id, name, class)
  - Context and action type
  - Stability and maintainability
- Review alternative locators if suggested one is unstable
- Prefer IDs over XPath when available

### Test Organization
- One recording session = One test case
- Group related tests by naming convention
- Review generated code before execution
- Add assertions manually if needed

## Future Enhancements
- [ ] Direct test execution from UI
- [ ] Edit recorded actions before generation
- [ ] Export tests to file system
- [ ] Support for assertions and validations
- [ ] Screenshot capture on each step
- [ ] Page Object Model generation
- [ ] Data-driven test support
- [ ] Integration with CI/CD pipelines

## Troubleshooting

### Recording doesn't start
- Ensure server is running on port 5002
- Check browser initialized successfully
- Verify URL is accessible

### Actions not captured
- Browser must have focus
- Some dynamic elements may need delays
- Check browser console for errors

### Generated code doesn't work
- Review locators in generated code
- Check if element attributes changed
- Add explicit waits if needed
- Verify page loaded completely

## Integration with Existing Features

The Recorder works seamlessly with:
- **Generate Tab**: Use AI to create individual actions
- **Browser Tab**: Execute generated code immediately
- **Locator Tab**: Get AI suggestions for specific elements
- **Action Tab**: Suggest actions for recorded elements

---

**🎉 Happy Testing!** The recorder makes test creation faster, easier, and more maintainable with AI-powered intelligence.

