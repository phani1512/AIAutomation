# Page Helper Patterns - Quick Reference

## 🚀 Quick Start

This is a quick lookup guide for using Page Helper patterns in your Selenium automation tests.

## 📋 Common Patterns Cheat Sheet

### Input Fields (by Label)

```java
// Set value
setInputFieldValue("First Name", "John");

// Get value
String name = getInputFieldValue("First Name");

// Check if disabled
boolean disabled = isInputFieldDisabled("Email");

// Check if exists
boolean exists = isInputFieldFound("Password");

// Get validation message
String error = getInputFieldValidationMessage("Email");
```

### Dropdowns (by Label)

```java
// Select option
setDropdownValue("Country", "United States");

// Get selected value
String country = getSelectedDropdownValue("Country");

// Check if disabled
boolean disabled = isDropdownFieldDisabled("State");
```

### Checkboxes (by Label)

```java
// Check
setCheckboxOn("I agree to terms");

// Uncheck
setCheckboxOff("Subscribe to newsletter");

// Verify state
boolean checked = isCheckboxOn("Remember me");

// Check if disabled
boolean disabled = isCheckboxDisabled("Auto-renew");
```

### Radio Buttons (by Label)

```java
// Select
selectRadioButton("Credit Card");

// Verify selected
boolean selected = isRadioButtonSelected("Debit Card");
```

### Buttons (by Text)

```java
// Click button
clickButton("Submit");

// Click dialog button
clickDialogButton("Confirm");

// Check if exists
boolean exists = isButtonFound("Cancel");

// Check if disabled
boolean disabled = isSubmitButtonDisabled();
```

### Links (by Text)

```java
// Click link
clickLink("Forgot Password?");

// Check if exists
boolean exists = isLinkFound("Terms of Service");

// Check if opens new tab
boolean opensNew = isLinkOpeningInNewTab("Privacy Policy");
```

### Tabs & Navigation

```java
// Click navigation tab
clickNavigationTab("Settings");

// Click tab button
clickTabButton("Personal Info");

// Check if active
boolean active = isTabButtonActive("Profile");
```

### Dialogs/Modals

```java
// Check if open
boolean open = isDialogOpen();

// Get content
String content = getDialogContent();

// Close dialog
closeDialog();

// Submit dialog
clickDialogSubmitButton();

// Click specific dialog button
clickDialogButton("OK");
```

### Tables

```java
// Search table
searchTable("John Doe");

// Count rows
int rows = getTableRowCount();

// Check for content
boolean contains = isTableContains("Active");

// Check if no results
boolean empty = isSearchTableNoResultsFound();

// Select row
setTableRowCheckboxOn("John Doe");

// Edit/Delete row
clickEditPencilButton();
clickTrashCanButton();

// Row dropdown menu
clickTableRowDropdownToggle();
```

### Messages & Notifications

```java
// Get any message
String msg = getMessageBoxText();

// Get specific message types
String success = getMessageBoxSuccessText();
String error = getMessageBoxErrorText();
String warning = getMessageBoxWarningText();
String info = getMessageBoxInfoText();

// Toast notifications
String toast = getToastSuccessText();
```

### Wait Operations

```java
// Wait for page load
waitForPageLoading();

// Wait for processing spinner
waitForProcessingSpinner();

// Wait for toast
waitForToastSuccess();

// Wait for dialog
waitUntilDialogIsOpen(10);
```

### File Upload

```java
// Single file
selectFileToUpload("path/to/file.pdf");

// Multiple files
selectFileToUpload("file1.pdf", "file2.jpg", "file3.doc");
```

### Menus

```java
// Click menu
clickMenu("File");

// Click submenu
clickSubmenu("Export");
```

### Other Operations

```java
// Scroll to view
scrollToView(By.id("footer"));

// Check element exists
boolean exists = isElementFound(By.id("header"));

// Check element invisible
boolean hidden = isElementInvisible(By.id("spinner"));

// Get panel content
String content = getPanelContents();

// Check panel exists
boolean exists = isPanelFound("Summary");
```

## 🎯 Common Workflows

### Simple Form Fill

```java
setInputFieldValue("First Name", "John");
setInputFieldValue("Last Name", "Doe");
setInputFieldValue("Email", "john@example.com");
setCheckboxOn("I agree to terms");
clickButton("Submit");
waitForToastSuccess();
```

### Form with Validation

```java
setInputFieldValue("Email", "invalid");
clickButton("Submit");
String error = getInputFieldValidationMessage("Email");
assertEquals("Please enter a valid email", error);

setInputFieldValue("Email", "valid@example.com");
clickButton("Submit");
String success = getMessageBoxSuccessText();
```

### Table Search and Edit

```java
searchTable("John Doe");
waitForPageLoading();
boolean found = isTableContains("John Doe");
if (found) {
    clickEditPencilButton();
    setInputFieldValue("Status", "Active");
    clickDialogSubmitButton();
}
```

### Multi-Step Form

```java
// Step 1
clickNavigationTab("Personal Info");
setInputFieldValue("Name", "John Doe");
clickButton("Next");

// Step 2
clickNavigationTab("Contact");
setInputFieldValue("Email", "john@example.com");
clickButton("Next");

// Step 3
clickNavigationTab("Review");
String content = getPanelContents();
assertTrue(content.contains("John Doe"));
clickButton("Submit");
```

### Dialog Workflow

```java
clickButton("Add New");
waitUntilDialogIsOpen(5);
setInputFieldValue("Name", "New Item");
setDropdownValue("Category", "Type A");
clickDialogSubmitButton();
waitForToastSuccess();
```

## 🔍 Natural Language Examples

| What You Say | Code Generated |
|--------------|----------------|
| "Enter John in the name field" | `setInputFieldValue("Name", "John");` |
| "Select USA from country dropdown" | `setDropdownValue("Country", "USA");` |
| "Check the terms checkbox" | `setCheckboxOn("Terms");` |
| "Click the submit button" | `clickButton("Submit");` |
| "Search for John Doe in the table" | `searchTable("John Doe");` |
| "Get the error message for email" | `getInputFieldValidationMessage("Email");` |
| "Verify the save button is disabled" | `isSubmitButtonDisabled();` |
| "Wait for the page to load" | `waitForPageLoading();` |

## ⚡ Best Practices

### DO ✅
```java
// Use label-based methods
setInputFieldValue("Email", "user@example.com");

// Chain methods
setInputFieldValue("Name", "John")
    .setDropdownValue("Country", "USA")
    .clickButton("Submit");

// Wait appropriately
waitForPageLoading();
clickButton("Submit");
waitForToastSuccess();

// Validate before actions
if (isButtonFound("Submit") && !isSubmitButtonDisabled()) {
    clickButton("Submit");
}
```

### DON'T ❌
```java
// Don't use raw Selenium when Page Helper exists
driver.findElement(By.xpath("//label[text()='Email']/../input")).sendKeys("test");
// Instead: setInputFieldValue("Email", "test");

// Don't skip waits
clickButton("Submit");
String toast = getToastSuccessText(); // May fail without wait

// Don't hardcode delays
Thread.sleep(5000);
// Instead: waitForPageLoading();
```

## 🐛 Common Issues & Solutions

### Issue: "Element not found"
```java
// Problem
setInputFieldValue("Name", "John"); // Fails immediately

// Solution: Wait for page
waitForPageLoading();
setInputFieldValue("Name", "John");
```

### Issue: "Element is disabled"
```java
// Problem
clickButton("Submit"); // Button is disabled

// Solution: Check state first
if (!isSubmitButtonDisabled()) {
    clickButton("Submit");
} else {
    System.out.println("Submit button is disabled");
}
```

### Issue: "Stale element"
```java
// Problem
searchTable("John");
clickEditPencilButton(); // Element is stale after search

// Solution: Wait after search
searchTable("John");
waitForPageLoading();
clickEditPencilButton();
```

### Issue: "Wrong element clicked"
```java
// Problem
clickEditPencilButton(); // Clicks first edit button

// Solution: Use indexed version
clickEditPencilButton(1); // Clicks second edit button
```

## 📚 Method Categories

- **Input Fields**: 7 methods
- **Dropdowns**: 6 methods  
- **Checkboxes**: 6 methods
- **Radio Buttons**: 3 methods
- **Buttons**: 8 methods
- **Links**: 4 methods
- **Tabs**: 5 methods
- **Dialogs**: 8 methods
- **Tables**: 12 methods
- **Messages**: 8 methods
- **Waits**: 6 methods
- **File Upload**: 1 method
- **Menus**: 2 methods
- **Misc**: 8 methods

**Total**: 84 helper methods

## 🎓 Learning Path

1. **Start with basics**: Input fields, buttons, links
2. **Add selections**: Dropdowns, checkboxes, radio buttons
3. **Master dialogs**: Modal interactions and workflows
4. **Learn tables**: Search, edit, validate
5. **Handle waits**: Synchronization strategies
6. **Build workflows**: Combine patterns into complete tests

## 📖 More Resources

- `PAGE_HELPER_DATASETS_README.md` - Full documentation
- `page-helper-patterns-dataset.json` - All patterns with details
- `page-helper-training-dataset.json` - 70 training examples
- `toTrain.java` - Source code with all implementations

---

**Quick Tip**: Bookmark this page for instant access to all Page Helper patterns! 🚀
