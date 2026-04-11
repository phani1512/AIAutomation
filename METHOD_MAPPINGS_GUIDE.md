# Method Name Mappings System

## Overview
The method name mappings system allows you to define custom helper method conversions **in a dataset file** (`method-name-mappings.json`) instead of hardcoding them in Python.

## Benefits
✅ **Data-driven**: Add new mappings without touching Python code  
✅ **Maintainable**: All mappings in one centralized file  
✅ **Version-controlled**: Track changes to mappings over time  
✅ **Extensible**: Easy to add support for new languages  
✅ **Documented**: Each mapping includes description and category  

## File Location
```
src/resources/method-name-mappings.json
```

## Structure

### Python Mappings
```json
{
  "mappings": {
    "python": {
      "type_conversions": [
        {
          "pattern": "boolean (\\w+)",
          "replacement": "\\1",
          "description": "Remove Java boolean type declaration"
        }
      ],
      "method_mappings": [
        {
          "java_method": "clickButton(",
          "python_method": "click_button(",
          "category": "button",
          "description": "Click button by text"
        }
      ]
    }
  }
}
```

## How to Add New Mappings

### 1. Add a New Method Mapping (Python)
```json
{
  "java_method": "customMethod(",
  "python_method": "custom_method(",
  "category": "custom",
  "description": "Your description here"
}
```

### 2. Add Type Conversion (Regex Pattern)
```json
{
  "pattern": "YourType (\\w+)",
  "replacement": "your_type \\1",
  "description": "Convert YourType to your_type"
}
```

### 3. Add C# Method Pattern
```json
{
  "pattern": "perform(\\w)",
  "replacement": "Perform\\1",
  "capitalize_first": true,
  "description": "Capitalize perform* methods"
}
```

## Usage in Code

The mappings are **automatically loaded** when the `ImprovedSeleniumGenerator` is initialized:

```python
generator = ImprovedSeleniumGenerator()
# Mappings loaded from dataset file automatically
```

### Simple Mode (Test Recorder/Builder)
```python
# Uses _convert_code_to_language() with dataset mappings
generated = generator.generate_clean(
    prompt="click submit", 
    language="python",
    comprehensive_mode=False  # Uses simple dataset mappings
)
```

### Comprehensive Mode (Generate Code)
```python
# Parses custom methods and generates full Selenium code
generated = generator.generate_clean(
    prompt="click submit",
    language="java",
    comprehensive_mode=True  # Parses and enhances to full Selenium
)
```

## Custom Helper Methods Recognized

The system recognizes these custom page helper methods from your datasets:

### Dialog Methods
- `isDialogOpen()` → Check if dialog is visible
- `getDialogContent()` → Get dialog content
- `closeDialog()` → Close dialog with multiple strategies

### Button Methods
- `clickButton("text")` → Click button by text
- `clickTabButton("text")` → Click tab button

### Input Methods
- `setInputFieldValue("label", "value")` → Set input by label
- `getInputFieldValue("label")` → Get input value
- `.clear()` → Clear input field

### Dropdown Methods
- `setDropdownValue("label", "value")` → Select from dropdown
- `getSelectedDropdownValue("label")` → Get selected value

### Checkbox Methods
- `setCheckboxOn("label")` → Enable checkbox
- `setCheckboxOff("label")` → Disable checkbox
- `isCheckboxOn("label")` → Check if enabled

### Radio Button Methods
- `selectRadioButton("label")` → Select radio button
- `isRadioButtonSelected("label")` → Check if selected

### Navigation Methods
- `clickLink("text")` → Click link by text
- `clickNavigationTab("text")` → Click navigation tab

### Table Methods
- `searchTable("text")` → Search in table
- `getTableRowCount()` → Get row count

## Comprehensive Mode Enhancements

When `comprehensive_mode=True`, custom helper methods are converted to **full Selenium code** with:
- ✅ WebDriverWait (10 second timeout)
- ✅ Expected Conditions
- ✅ Multiple fallback strategies
- ✅ Error handling
- ✅ Proper imports

### Example Transformation

**Input (Custom Helper):**
```java
clickButton("Submit");
```

**Output (Comprehensive Java):**
```java
// Click button 'Submit' with wait
WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));
WebElement element = wait.until(ExpectedConditions.elementToBeClickable(
    By.xpath("//button[contains(text(), 'Submit')]")
));
element.click();
```

## Adding Support for New Languages

To add a new language (e.g., Ruby):

1. Add to `method-name-mappings.json`:
```json
{
  "mappings": {
    "ruby": {
      "type_conversions": [...],
      "method_mappings": [...]
    }
  }
}
```

2. Update `_convert_code_to_language()` in Python (if custom logic needed)

3. Add language-specific comprehensive generation methods (if needed)

## Maintenance

### To Update a Mapping
1. Edit `src/resources/method-name-mappings.json`
2. Change the `java_method` or target language method
3. Save the file
4. Restart the server - changes load automatically

### To Remove a Mapping
1. Delete the mapping entry from the JSON file
2. Restart the server

## Notes

⚠️ **Order Matters**: Mappings are applied in the order they appear in the JSON file  
⚠️ **Regex Patterns**: Use proper escaping for regex patterns (`\\w` not `\w`)  
⚠️ **Testing**: Test mappings with both simple and comprehensive modes  

## Version History

- **v1.0.0** (2026-03-17): Initial dataset-based mapping system
  - Moved hardcoded mappings from Python to JSON dataset
  - Added support for custom helper methods in comprehensive mode
  - Implemented category-based organization
