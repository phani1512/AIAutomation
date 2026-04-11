"""
Enhance dataset with value-extraction examples and varied code patterns.
"""
import json
from pathlib import Path

def create_enhanced_examples():
    """Create examples showing how to extract values from prompts"""
    
    enhanced_examples = [
        # Examples with actual values in prompts
        {
            "prompt": "enter john@example.com in email field",
            "category": "sendKeys",
            "description": "Extract email value from prompt",
            "code": "WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));\nWebElement element = wait.until(ExpectedConditions.visibilityOfElementLocated(By.id(\"email\")));\nelement.clear();\nelement.sendKeys(\"john@example.com\");",
            "xpath": "By.id(\"email\")",
            "metadata": {
                "extracted_value": "john@example.com",
                "extracted_field": "email",
                "action": "sendKeys"
            }
        },
        {
            "prompt": "type password123 into password field",
            "category": "sendKeys",
            "description": "Extract password value from prompt",
            "code": "driver.findElement(By.id(\"password\")).sendKeys(\"password123\");",
            "xpath": "By.id(\"password\")",
            "metadata": {
                "extracted_value": "password123",
                "extracted_field": "password",
                "action": "sendKeys",
                "note": "Concise version without explicit wait"
            }
        },
        {
            "prompt": "click the submit button",
            "category": "click",
            "description": "Simple click action",
            "code": "driver.findElement(By.id(\"submit-button\")).click();",
            "xpath": "By.id(\"submit-button\")",
            "metadata": {
                "action": "click",
                "note": "Concise version for simple click"
            }
        },
        {
            "prompt": "get text from username label",
            "category": "getText",
            "description": "Get text without storing",
            "code": "String text = driver.findElement(By.className(\"username-label\")).getText();",
            "xpath": "By.className(\"username-label\")",
            "metadata": {
                "action": "getText",
                "returns": "String"
            }
        },
        {
            "prompt": "verify save button is enabled",
            "category": "verify",
            "description": "Check if element is enabled",
            "code": "WebElement saveBtn = driver.findElement(By.id(\"save-btn\"));\nboolean isEnabled = saveBtn.isEnabled();\nassertTrue(isEnabled, \"Save button should be enabled\");",
            "xpath": "By.id(\"save-btn\")",
            "metadata": {
                "action": "verify",
                "assertion": "assertTrue"
            }
        },
        {
            "prompt": "select United States from country dropdown",
            "category": "select",
            "description": "Select option from dropdown by visible text",
            "code": "Select countryDropdown = new Select(driver.findElement(By.id(\"country\")));\ncountryDropdown.selectByVisibleText(\"United States\");",
            "xpath": "By.id(\"country\")",
            "metadata": {
                "extracted_value": "United States",
                "extracted_field": "country",
                "action": "select"
            }
        },
        {
            "prompt": "wait for loading spinner to disappear",
            "category": "wait",
            "description": "Wait for element to be invisible",
            "code": "WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(30));\nwait.until(ExpectedConditions.invisibilityOfElementLocated(By.className(\"loading-spinner\")));",
            "xpath": "By.className(\"loading-spinner\")",
            "metadata": {
                "action": "wait",
                "wait_type": "invisibility"
            }
        },
        {
            "prompt": "enter John Doe in first name then Smith in last name",
            "category": "sendKeys",
            "description": "Multiple field entry from single prompt",
            "code": "driver.findElement(By.id(\"first-name\")).sendKeys(\"John Doe\");\ndriver.findElement(By.id(\"last-name\")).sendKeys(\"Smith\");",
            "xpath": "By.id(\"first-name\"), By.id(\"last-name\")",
            "metadata": {
                "extracted_values": ["John Doe", "Smith"],
                "extracted_fields": ["first-name", "last-name"],
                "action": "sendKeys",
                "note": "Multiple actions from one prompt"
            }
        },
        {
            "prompt": "check if error message contains invalid",
            "category": "verify",
            "description": "Verify text contains specific substring",
            "code": "String errorMsg = driver.findElement(By.className(\"error-message\")).getText();\nassertTrue(errorMsg.toLowerCase().contains(\"invalid\"), \"Error message should contain 'invalid'\");",
            "xpath": "By.className(\"error-message\")",
            "metadata": {
                "action": "verify",
                "extracted_value": "invalid",
                "assertion": "assertTrue with contains"
            }
        },
        {
            "prompt": "scroll to bottom of page",
            "category": "scroll",
            "description": "Scroll to page bottom",
            "code": "JavascriptExecutor js = (JavascriptExecutor) driver;\njs.executeScript(\"window.scrollTo(0, document.body.scrollHeight);\");",
            "xpath": "",
            "metadata": {
                "action": "scroll",
                "note": "JavaScript executor pattern"
            }
        }
    ]
    
    return enhanced_examples

def main():
    dataset_path = Path('src/resources/combined-training-dataset-final.json')
    
    # Load existing dataset
    with open(dataset_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Current dataset: {len(data)} entries")
    
    # Add enhanced examples
    enhanced = create_enhanced_examples()
    data.extend(enhanced)
    
    print(f"Added {len(enhanced)} enhanced examples")
    print(f"New total: {len(data)} entries")
    
    # Save updated dataset
    with open(dataset_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print("\n✅ Enhanced dataset saved!")
    print("\nNew examples include:")
    print("  - Value extraction from prompts")
    print("  - Concise code patterns (without explicit waits)")
    print("  - Multi-action prompts")
    print("  - Verification with assertions")
    print("  - Scroll and JavaScript patterns")

if __name__ == '__main__':
    main()
