# Selenium WebDriver Dataset for SLM Training

This directory contains datasets for training and test file uploads for the WebAutomation framework.

## 📁 Directory Structure

```
src/resources/
├── uploads/              # Test file uploads (default location for CI/CD)
│   ├── documents/       # PDF, DOCX, XLSX files
│   ├── images/          # PNG, JPG, SVG files
│   ├── auth/            # Profile photos, ID documents
│   └── README.md        # Detailed upload guide
├── selenium-methods-dataset.json
├── common-web-actions-dataset.json
├── element-locator-patterns.json
└── selenium_dataset.bin
```

## 📤 File Uploads

The `uploads/` directory is the **default location** for test file uploads. When recording tests:
- Place files in `uploads/` subdirectories (e.g., `uploads/documents/file.pdf`)
- Use filename only in the test: `file.pdf` or `documents/file.pdf`
- System auto-resolves to `src/resources/uploads/[your-path]`

See [uploads/README.md](uploads/README.md) for detailed usage guide.

## Dataset Files

### 1. selenium-methods-dataset.json
Complete catalog of WebDriverListener methods and Selenium WebDriver API:
- **WebDriverListener Events**: All before/after event methods for navigation, element interaction, finding elements, window/frame management, alerts, and scripts
- **Locator Strategies**: By.id, By.name, By.className, By.xpath, By.cssSelector, etc.
- **Wait Strategies**: Implicit waits, explicit waits, ExpectedConditions
- **Actions Class**: Advanced interactions like hover, drag-and-drop, keyboard actions
- **Select Class**: Dropdown/select element handling
- **Additional APIs**: Screenshots, cookies, JavaScript execution

**Total Methods**: 150+ methods with signatures, descriptions, examples, and usage patterns

### 2. common-web-actions-dataset.json
Real-world user interaction patterns:
- Login forms
- Search functionality
- Dropdown selections
- Checkbox/radio button interactions
- File uploads
- Modal dialog handling
- Tab/window navigation
- Alert handling
- Hover menus
- Form validation
- Scroll interactions
- Dynamic content/AJAX waits
- Table data extraction
- Multi-step forms

**Total Patterns**: 15+ common web interaction workflows

### 3. element-locator-patterns.json
HTML element recognition and locator generation:
- Input fields (text, password, email, search, date, file)
- Buttons and links
- Select/dropdown elements
- Checkboxes and radio buttons
- Textareas
- Tables and lists
- Forms
- Iframes
- Modals
- Images
- Error messages and alerts

Each element includes:
- HTML structure
- Multiple locator strategies ranked by priority and reliability
- Recommended action type
- Code examples

**Total Element Types**: 20+ element patterns

## Dataset Structure

### Method Entry Format
```json
{
  "category": "WebDriverListener_ElementInteraction",
  "method": "beforeClick",
  "signature": "void beforeClick(WebElement element)",
  "description": "Called before clicking an element",
  "example": "element.click();",
  "usage_pattern": "Click on button, link, or interactive element",
  "parameters": ["WebElement element"],
  "action_type": "click",
  "locator_examples": ["By.id(\"submitBtn\")", "By.xpath(\"//button[@type='submit']\")"]
}
```

### Action Pattern Format
```json
{
  "action": "Login Form",
  "description": "User enters credentials and submits login form",
  "steps": [
    {
      "step": 1,
      "action": "navigate",
      "code": "driver.get(\"https://example.com/login\");",
      "element_type": null,
      "locator": null
    },
    {
      "step": 2,
      "action": "sendKeys",
      "code": "driver.findElement(By.id(\"username\")).sendKeys(\"testuser\");",
      "element_type": "input",
      "locator": "By.id(\"username\")",
      "value": "testuser"
    }
  ],
  "pattern_type": "form_submission"
}
```

### Element Locator Format
```json
{
  "html": "<input id=\"username\" type=\"text\">",
  "element_type": "input",
  "locator_options": [
    { "locator": "By.id(\"username\")", "priority": 1, "reliability": "high" }
  ],
  "recommended_action": "sendKeys",
  "action_example": "driver.findElement(By.id(\"username\")).sendKeys(\"text\");"
}
```

## Usage for SLM Training

### Training Objectives
1. **Method Recognition**: Understand all WebDriverListener methods and their lifecycle
2. **Action Mapping**: Map user actions (click, type, select) to Selenium code
3. **Locator Generation**: Generate optimal locator strategies for HTML elements
4. **Pattern Recognition**: Recognize common web interaction patterns
5. **Code Generation**: Generate complete test scripts from user actions

### Key Categories

#### Navigation (14 methods)
- beforeGet/afterGet
- beforeGetCurrentUrl/afterGetCurrentUrl
- beforeGetTitle/afterGetTitle
- beforeBack/afterBack
- beforeForward/afterForward
- beforeRefresh/afterRefresh
- beforeTo/afterTo

#### Element Interaction (12 methods)
- beforeClick/afterClick
- beforeSendKeys/afterSendKeys
- beforeClear/afterClear
- beforeSubmit/afterSubmit

#### Element Query (18 methods)
- beforeGetText/afterGetText
- beforeGetAttribute/afterGetAttribute
- beforeIsDisplayed/afterIsDisplayed
- beforeIsEnabled/afterIsEnabled
- beforeIsSelected/afterIsSelected
- beforeGetTagName/afterGetTagName
- beforeGetCssValue/afterGetCssValue

#### Element Finding (8 methods)
- beforeFindElement/afterFindElement (driver level)
- beforeFindElements/afterFindElements (driver level)
- beforeFindElement/afterFindElement (element level)
- beforeFindElements/afterFindElements (element level)

#### Window Management (8 methods)
- beforeGetWindowHandle/afterGetWindowHandle
- beforeGetWindowHandles/afterGetWindowHandles
- beforeSwitchToWindow/afterSwitchToWindow

#### Frame Management (8 methods)
- Switch by index, name/id, or WebElement
- Switch to parent frame

#### Alert Handling (10 methods)
- beforeSwitchToAlert/afterSwitchToAlert
- beforeAccept/afterAccept
- beforeDismiss/afterDismiss
- beforeGetText/afterGetText
- beforeSendKeys/afterSendKeys (for alert prompts)

#### JavaScript Execution (4 methods)
- beforeExecuteScript/afterExecuteScript
- beforeExecuteAsyncScript/afterExecuteAsyncScript

#### Session Management (4 methods)
- beforeQuit/afterQuit
- beforeClose/afterClose

## Action Types
- **navigate**: Browser navigation actions
- **click**: Element click actions
- **sendKeys**: Text input actions
- **clear**: Clear text field actions
- **submit**: Form submission
- **select**: Dropdown selection
- **query**: Information retrieval (getText, getAttribute, etc.)
- **find**: Element location
- **switch**: Context switching (windows, frames, alerts)
- **wait**: Explicit/implicit waits
- **action**: Advanced actions (hover, drag-drop, etc.)
- **alert**: Alert dialog handling
- **script**: JavaScript execution
- **session**: Browser session management
- **screenshot**: Screen capture
- **cookie**: Cookie management

## Locator Strategy Priority
1. **By.id** - Highest priority, most reliable
2. **By.name** - High priority for form elements
3. **By.linkText** - High priority for links with unique text
4. **By.cssSelector** - Medium-high priority, flexible
5. **By.xpath** - Medium priority, most powerful but slower
6. **By.className** - Lower priority, less unique
7. **By.tagName** - Lowest priority, least specific

## Common Patterns

### Form Submission Pattern
1. Navigate to page
2. Find input fields
3. Enter data (sendKeys)
4. Click submit button
5. Wait for result/validation

### Dynamic Content Pattern
1. Trigger action (click/navigate)
2. Wait for element presence/visibility
3. Verify content loaded
4. Extract/interact with data

### Multi-Window Pattern
1. Get current window handle
2. Trigger new window (click link)
3. Get all window handles
4. Switch to new window
5. Perform actions
6. Switch back to original

### Alert Handling Pattern
1. Trigger alert (click button)
2. Switch to alert
3. Get alert text (optional)
4. Accept or dismiss alert
5. Continue with main content

## Element Capture Examples

When user **clicks** on an element:
```java
// beforeClick is triggered
@Override
public void beforeClick(WebElement element) {
    String locator = generateLocator(element);
    recordedActions.add(new RecordedAction(++stepCounter, "click", locator, null, element.getTagName()));
}
```

When user **enters text** in an element:
```java
// beforeSendKeys is triggered
@Override
public void beforeSendKeys(WebElement element, CharSequence... keysToSend) {
    String text = String.join("", keysToSend);
    String locator = generateLocator(element);
    recordedActions.add(new RecordedAction(++stepCounter, "sendKeys", locator, text, element.getTagName()));
}
```

## Dataset Statistics
- **Total WebDriverListener Methods**: 80+ (before/after pairs)
- **Total Locator Strategies**: 8 types
- **Total Wait Conditions**: 20+ ExpectedConditions
- **Total Action Patterns**: 15+ common workflows
- **Total Element Types**: 20+ HTML element patterns
- **Code Examples**: 200+ complete examples

## Training Recommendations

1. **Phase 1**: Learn basic WebDriverListener methods and element interactions
2. **Phase 2**: Master locator strategies and reliability rankings
3. **Phase 3**: Understand wait strategies and timing
4. **Phase 4**: Recognize common interaction patterns
5. **Phase 5**: Generate complete test scripts from patterns

## File Locations
- `src/main/resources/selenium-methods-dataset.json`
- `src/main/resources/common-web-actions-dataset.json`
- `src/main/resources/element-locator-patterns.json`
- `src/main/resources/README.md` (this file)
