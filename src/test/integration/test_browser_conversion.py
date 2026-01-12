"""
Test script to debug browser code conversion
"""

import sys
sys.path.insert(0, 'src/main/python')

from browser_executor import BrowserExecutor

# Test cases
test_cases = [
    "// Click button\nWebElement button = driver.findElement(By.id(\"loginBtn\"));\nbutton.click();",
    "// Navigate\ndriver.get(\"https://example.com\");",
    "// Input text\nWebElement input = driver.findElement(By.id(\"username\"));\ninput.sendKeys(\"testuser\");",
]

executor = BrowserExecutor()

print("="*60)
print("Testing Java to Python Code Conversion")
print("="*60)

for idx, java_code in enumerate(test_cases, 1):
    print(f"\n--- Test Case {idx} ---")
    print(f"Java Code:\n{java_code}\n")
    
    python_code = executor._convert_java_to_python(java_code)
    print(f"Python Code:\n{python_code}\n")
    print("-"*60)
