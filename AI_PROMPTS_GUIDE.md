# AI Prompts Guide - Common Web Actions Dataset

## 📋 Overview

This document explains how to use AI prompts in the WebAutomation project based on the trained actions in `common-web-actions-dataset.json`. These prompts are used in the **Generate Code** section of the web interface to generate Selenium test automation code.

## 🎯 Where to Use AI Prompts

### **Generate Code Page** (Main Usage Area)

**Location:** Web Interface → Generate Code Tab

**URL:** `http://localhost:5001` → Click "Generate Code" in sidebar

**Features:**
- Text area for entering prompts
- Example prompt buttons for quick access
- AI-powered code generation
- Save prompts to account
- View prompt history
- Export generated code

**Interface Elements:**
```
┌────────────────────────────────────────────────────┐
│ ✨ Generate Test Code                             │
├────────────────────────────────────────────────────┤
│ [Example Prompts: Quick Click Buttons]            │
│                                                    │
│ ┌────────────────────────────────────────────┐   │
│ │ Enter your test automation prompt:         │   │
│ │ [Text Area]                                │   │
│ └────────────────────────────────────────────┘   │
│                                                    │
│ [💾 Save Prompt] [📚 My Prompts] [🕐 History]    │
│                                                    │
│ [🚀 Generate Code Button]                         │
└────────────────────────────────────────────────────┘
```

## 📝 Complete Prompt List by Action Category

### 1️⃣ LOGIN & AUTHENTICATION

#### **Action: Login Form**
**Dataset Pattern:** `form_submission`

**AI Prompts:**
```
✅ "enter username and password and click login button"
✅ "login with credentials testuser and password123"
✅ "fill login form and submit"
✅ "enter testuser in username field"
✅ "enter password in password field"
✅ "click login button"
```

**Generated Code Pattern:**
```java
// Navigate to login page
driver.get("https://example.com/login");

// Enter username
driver.findElement(By.id("username")).sendKeys("testuser");

// Enter password
driver.findElement(By.id("password")).sendKeys("password123");

// Click login button
driver.findElement(By.id("loginBtn")).click();
```

**When to Use:**
- Testing login functionality
- User authentication flows
- Form submission scenarios

---

### 2️⃣ SEARCH & NAVIGATION

#### **Action: Search Functionality**
**Dataset Pattern:** `search`

**AI Prompts:**
```
✅ "search for selenium webdriver"
✅ "enter search query and click search button"
✅ "type in search box and submit"
✅ "click search box and enter text"
```

**Generated Code Pattern:**
```java
// Click search box
driver.findElement(By.id("searchBox")).click();

// Enter search query
driver.findElement(By.id("searchBox")).sendKeys("selenium webdriver");

// Click search button
driver.findElement(By.cssSelector("button[type='submit']")).click();
```

**When to Use:**
- Testing search features
- Query submission
- Filter/search bars

---

### 3️⃣ DROPDOWNS & SELECTIONS

#### **Action: Dropdown Selection**
**Dataset Pattern:** `dropdown_selection`

**AI Prompts:**
```
✅ "select value from dropdown"
✅ "select United States from country dropdown"
✅ "click dropdown and select option"
✅ "choose option from select menu"
```

**Generated Code Pattern:**
```java
// Click dropdown
driver.findElement(By.id("country")).click();

// Select option
Select select = new Select(driver.findElement(By.id("country")));
select.selectByVisibleText("United States");
```

**When to Use:**
- Form dropdowns (country, state, category)
- Filter selections
- Multi-option menus

---

### 4️⃣ CHECKBOXES & RADIO BUTTONS

#### **Action: Checkbox Selection**
**Dataset Pattern:** `checkbox_selection`

**AI Prompts:**
```
✅ "select checkbox for terms and conditions"
✅ "click terms checkbox"
✅ "select multiple checkboxes"
✅ "check newsletter subscription"
```

**Generated Code Pattern:**
```java
// Select terms checkbox
driver.findElement(By.id("terms")).click();

// Select newsletter checkbox
driver.findElement(By.id("newsletter")).click();
```

**When to Use:**
- Terms & conditions acceptance
- Multi-select options
- Preference selections

#### **Action: Radio Button Selection**
**Dataset Pattern:** `radio_selection`

**AI Prompts:**
```
✅ "select radio button for male"
✅ "choose radio option"
✅ "select gender male"
```

**Generated Code Pattern:**
```java
// Select radio button
driver.findElement(By.id("male")).click();
```

**When to Use:**
- Single-choice selections
- Gender/payment method options
- Yes/No questions

---

### 5️⃣ FILE UPLOADS

#### **Action: File Upload**
**Dataset Pattern:** `file_upload`

**AI Prompts:**
```
✅ "upload file from path"
✅ "select file and click upload button"
✅ "upload document file.pdf"
✅ "send file path to upload input"
```

**Generated Code Pattern:**
```java
// Send file path to file input
driver.findElement(By.id("fileUpload")).sendKeys("C:\\path\\to\\file.pdf");

// Click upload button
driver.findElement(By.id("uploadBtn")).click();
```

**When to Use:**
- Document uploads
- Image/avatar uploads
- CSV/Excel file imports

**💡 Note:** In this project, use the enhanced file upload with `src/resources/uploads/` directory:
```
Prompt: "upload file resume.pdf"
System resolves: src/resources/uploads/resume.pdf
```

---

### 6️⃣ MODAL DIALOGS

#### **Action: Modal Dialog Interaction**
**Dataset Pattern:** `modal_interaction`

**AI Prompts:**
```
✅ "open modal and enter text"
✅ "click button to open modal and fill form"
✅ "interact with popup dialog"
✅ "wait for modal to appear and click confirm"
```

**Generated Code Pattern:**
```java
// Open modal
driver.findElement(By.id("openModal")).click();

// Wait for modal to appear
new WebDriverWait(driver, Duration.ofSeconds(10))
    .until(ExpectedConditions.visibilityOfElementLocated(By.id("modal")));

// Enter text in modal
driver.findElement(By.id("modalInput")).sendKeys("modal text");

// Confirm
driver.findElement(By.id("confirmBtn")).click();
```

**When to Use:**
- Popup confirmations
- Dialog forms
- Overlay interactions

---

### 7️⃣ TAB & WINDOW MANAGEMENT

#### **Action: Tab Navigation**
**Dataset Pattern:** `window_switching`

**AI Prompts:**
```
✅ "open new tab and switch to it"
✅ "click link to open new window"
✅ "switch to new browser tab"
✅ "handle multiple windows"
```

**Generated Code Pattern:**
```java
// Click link to open new tab
driver.findElement(By.linkText("Open New Tab")).click();

// Switch to new window
String originalWindow = driver.getWindowHandle();
Set<String> handles = driver.getWindowHandles();
for(String handle : handles) {
    if(!handle.equals(originalWindow)) {
        driver.switchTo().window(handle);
    }
}
```

**When to Use:**
- Multi-window applications
- External link testing
- Tab-based workflows

---

### 8️⃣ ALERTS & JAVASCRIPT DIALOGS

#### **Action: Alert Handling**
**Dataset Pattern:** `alert_handling`

**AI Prompts:**
```
✅ "click button and accept alert"
✅ "handle JavaScript alert"
✅ "dismiss alert popup"
✅ "accept browser alert"
```

**Generated Code Pattern:**
```java
// Click button that triggers alert
driver.findElement(By.id("alertBtn")).click();

// Handle alert
Alert alert = driver.switchTo().alert();
alert.accept();
```

**When to Use:**
- JavaScript alerts
- Confirmation dialogs
- Browser prompts

---

### 9️⃣ HOVER & MOUSE ACTIONS

#### **Action: Hover Menu Navigation**
**Dataset Pattern:** `hover_navigation`

**AI Prompts:**
```
✅ "hover over menu to reveal submenu"
✅ "move mouse to menu and click submenu item"
✅ "hover and click dropdown menu"
✅ "mouse over element and select option"
```

**Generated Code Pattern:**
```java
// Hover over menu
WebElement menu = driver.findElement(By.id("mainMenu"));
new Actions(driver).moveToElement(menu).perform();

// Wait for submenu
new WebDriverWait(driver, Duration.ofSeconds(5))
    .until(ExpectedConditions.visibilityOfElementLocated(By.id("subMenu")));

// Click submenu item
driver.findElement(By.id("subMenuItem")).click();
```

**When to Use:**
- Dropdown menus
- Tooltip interactions
- Hover-triggered elements

---

### 🔟 FORM VALIDATION

#### **Action: Form Validation**
**Dataset Pattern:** `validation_check`

**AI Prompts:**
```
✅ "submit form and verify error message"
✅ "click submit and check validation"
✅ "verify required field error"
✅ "check form validation message"
```

**Generated Code Pattern:**
```java
// Submit form
driver.findElement(By.id("submitBtn")).click();

// Verify error message
String errorMsg = driver.findElement(By.id("errorMessage")).getText();
assert errorMsg.equals("Please fill all required fields");
```

**When to Use:**
- Form validation testing
- Error message verification
- Required field checks

---

### 1️⃣1️⃣ SCROLL & VISIBILITY

#### **Action: Scroll to Element**
**Dataset Pattern:** `scroll_interaction`

**AI Prompts:**
```
✅ "scroll to footer element"
✅ "scroll down to element and click"
✅ "scroll into view and interact"
✅ "scroll to bottom of page"
```

**Generated Code Pattern:**
```java
// Scroll to element
WebElement element = driver.findElement(By.id("footer"));
((JavascriptExecutor)driver).executeScript("arguments[0].scrollIntoView(true);", element);

// Click element
driver.findElement(By.id("footerLink")).click();
```

**When to Use:**
- Long pages
- Elements below fold
- Lazy-loaded content

---

### 1️⃣2️⃣ DYNAMIC CONTENT & AJAX

#### **Action: Dynamic Content Wait**
**Dataset Pattern:** `ajax_wait`

**AI Prompts:**
```
✅ "click button and wait for data to load"
✅ "wait for ajax content"
✅ "load data and verify rows appear"
✅ "wait for dynamic content"
```

**Generated Code Pattern:**
```java
// Trigger data load
driver.findElement(By.id("loadDataBtn")).click();

// Wait for content
new WebDriverWait(driver, Duration.ofSeconds(15))
    .until(ExpectedConditions.presenceOfElementLocated(By.className("dataRow")));

// Verify content loaded
List<WebElement> rows = driver.findElements(By.className("dataRow"));
assert rows.size() > 0;
```

**When to Use:**
- AJAX loading
- Infinite scroll
- Lazy-loaded content
- API-driven UIs

---

### 1️⃣3️⃣ TABLE DATA

#### **Action: Table Data Extraction**
**Dataset Pattern:** `table_extraction`

**AI Prompts:**
```
✅ "extract data from table"
✅ "get all rows from data table"
✅ "iterate through table cells"
✅ "read table content"
```

**Generated Code Pattern:**
```java
// Find table
WebElement table = driver.findElement(By.id("dataTable"));

// Extract rows
List<WebElement> rows = table.findElements(By.tagName("tr"));
for(WebElement row : rows) {
    List<WebElement> cells = row.findElements(By.tagName("td"));
    // Process cells
}
```

**When to Use:**
- Data verification
- Table parsing
- Report validation

---

### 1️⃣4️⃣ MULTI-STEP FORMS

#### **Action: Multi-Step Form**
**Dataset Pattern:** `multi_step_form`

**AI Prompts:**
```
✅ "complete multi-step registration form"
✅ "fill first name last name and click next"
✅ "enter personal details and proceed"
✅ "complete wizard form steps"
```

**Generated Code Pattern:**
```java
// Step 1: Personal Info
driver.findElement(By.name("firstName")).sendKeys("John");
driver.findElement(By.name("lastName")).sendKeys("Doe");
driver.findElement(By.id("nextBtn")).click();

// Step 2: Contact Info
driver.findElement(By.name("email")).sendKeys("john.doe@example.com");
driver.findElement(By.name("phone")).sendKeys("123-456-7890");
driver.findElement(By.id("submitBtn")).click();
```

**When to Use:**
- Registration wizards
- Checkout processes
- Multi-page forms

---

## 🎨 Prompt Engineering Tips

### ✅ **Good Prompts** (Specific & Clear)

```
✓ "enter username testuser and password secret123"
✓ "select United States from country dropdown"
✓ "click submit button and verify success message"
✓ "wait for loading spinner to disappear"
✓ "hover over Products menu and click Laptops submenu"
```

### ❌ **Poor Prompts** (Vague & Ambiguous)

```
✗ "do login"
✗ "select something"
✗ "click"
✗ "test the form"
✗ "check if it works"
```

### 💡 **Best Practices**

1. **Be Specific:** Include element names, actions, and values
   ```
   Good: "enter john@example.com in email field"
   Bad:  "enter email"
   ```

2. **Use Action Verbs:** click, enter, select, verify, wait, hover
   ```
   Good: "click login button"
   Bad:  "login button"
   ```

3. **Include Context:** Mention element type (button, field, dropdown)
   ```
   Good: "select USA from country dropdown"
   Bad:  "select USA"
   ```

4. **Chain Related Actions:** Combine steps logically
   ```
   Good: "enter username and password then click submit"
   Bad:  "username" (separate prompt for each field)
   ```

5. **Specify Values:** Include actual test data
   ```
   Good: "enter testuser in username field"
   Bad:  "enter username"
   ```

---

## 🔧 How to Use in the Project

### **Step-by-Step Guide**

1. **Open Web Interface**
   ```
   http://localhost:5001
   ```

2. **Navigate to Generate Code**
   - Click "Generate Code" in the left sidebar
   - Or click the "Generate Code" tab

3. **Choose a Prompt Method**

   **Option A: Use Example Buttons**
   - Click predefined example buttons
   - Modify the prompt if needed

   **Option B: Type Custom Prompt**
   - Enter your prompt in the text area
   - Use natural language
   - Reference the prompt lists above

   **Option C: Use Saved Prompts**
   - Click "📚 My Prompts" button
   - Select from previously saved prompts

4. **Generate Code**
   - Click "🚀 Generate Code" button
   - Wait for AI to process (1-2 seconds)
   - Review generated code on the right

5. **Actions on Generated Code**
   - **📋 Copy:** Copy to clipboard
   - **🔍 Validate:** Check code syntax
   - **💾 Save:** Save to snippets library
   - **💾 Export:** Export to .java file
   - **▶️ Execute:** Run the test immediately

---

## 📊 Prompt Categories Quick Reference

| Category | Example Prompt | Use Case |
|----------|---------------|----------|
| **Login** | `enter username and password` | Authentication forms |
| **Search** | `search for selenium webdriver` | Search boxes |
| **Dropdown** | `select USA from country dropdown` | Select menus |
| **Checkbox** | `click terms checkbox` | Agreement checkboxes |
| **Radio** | `select male radio button` | Single choices |
| **Upload** | `upload file resume.pdf` | File uploads |
| **Modal** | `open modal and enter text` | Popup dialogs |
| **Tabs** | `switch to new tab` | Window management |
| **Alert** | `accept JavaScript alert` | Browser alerts |
| **Hover** | `hover over menu and click item` | Dropdown menus |
| **Validation** | `verify error message appears` | Form validation |
| **Scroll** | `scroll to footer and click link` | Long pages |
| **Wait** | `wait for data to load` | AJAX content |
| **Table** | `extract data from table` | Data tables |
| **Wizard** | `complete multi-step form` | Multi-page forms |

---

## 🚀 Advanced Usage

### **Combining Multiple Actions**

You can chain multiple actions in one prompt:

```
"navigate to login page, enter username admin and password secret, 
 click login button, and verify welcome message appears"
```

This generates a complete test flow with multiple steps.

### **Using Template Variables**

The AI recognizes common patterns:

```
"enter {value} in {field} field"
↓
driver.findElement(By.id("field")).sendKeys("value");
```

### **Contextual Generation**

The AI understands context from previous prompts:

```
First prompt: "enter username testuser"
Next prompt: "enter password"  ← AI knows you're still on login form
```

---

## 📈 Prompt Library (Organized by Frequency)

### **Most Common Prompts (Daily Use)**

1. `enter username and password and login`
2. `click submit button`
3. `verify success message`
4. `select option from dropdown`
5. `upload file document.pdf`

### **Frequently Used (Weekly)**

6. `wait for page to load`
7. `switch to new tab`
8. `accept alert`
9. `hover over menu and click submenu`
10. `scroll to element and click`

### **Occasionally Used (Monthly)**

11. `extract data from table`
12. `handle modal dialog`
13. `verify form validation error`
14. `complete multi-step wizard`
15. `drag and drop element`

---

## 💾 Saving & Reusing Prompts

### **Save to Account**
1. Enter your prompt
2. Click "💾 Save Prompt"
3. Give it a name
4. Access later from "📚 My Prompts"

### **View History**
- Click "🕐 History" to see recent prompts
- Re-use successful prompts
- Learn from prompt patterns

---

## 🎯 Real-World Examples

### **E-Commerce Checkout Flow**
```
1. "search for laptop in search box"
2. "click first product in results"
3. "select quantity 2 from dropdown"
4. "click add to cart button"
5. "click proceed to checkout"
6. "enter shipping address details"
7. "select express shipping radio button"
8. "enter credit card information"
9. "click place order button"
10. "verify order confirmation message"
```

### **User Registration Flow**
```
1. "navigate to registration page"
2. "enter john in first name field"
3. "enter doe in last name field"
4. "enter john.doe@email.com in email field"
5. "select USA from country dropdown"
6. "click terms checkbox"
7. "click newsletter checkbox"
8. "click register button"
9. "verify registration success message"
```

---

## 🔍 Troubleshooting

### **Prompt Not Working?**

✅ **Check for:**
- Spelling errors
- Missing element identifiers
- Ambiguous action verbs
- Too vague or too complex

✅ **Try:**
- Simplifying the prompt
- Breaking into smaller steps
- Using example prompts as templates
- Adding more specific details

### **Generated Code Not Correct?**

✅ **Solutions:**
- Refine your prompt with more details
- Use element-specific language (button vs. link)
- Specify the action more clearly
- Check if element IDs match your app

---

## 📚 Summary

**Total Actions in Dataset:** 14 major patterns
**Total Prompts Listed:** 100+ examples
**Use Location:** Generate Code page (Web UI)
**Primary Purpose:** AI-powered Selenium code generation
**Supported Languages:** Java (Selenium WebDriver)

Use this guide as a reference when writing prompts in the **Generate Code** section to leverage the AI model's training on common web automation patterns!

---

**🎉 Happy Testing with AI-Powered Automation!**
