"""Test language conversion directly"""
import sys
sys.path.insert(0, 'src/main/python')

from language_converter import LanguageConverter

# Test Python to Java conversion
python_code = """wait = WebDriverWait(driver, 10)
element = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".login-row .primary-btn")))
element.click()"""

print("="*80)
print("INPUT (Python):")
print(python_code)
print("\n" + "="*80)

converter = LanguageConverter()
java_code = converter.convert_code_to_language(python_code, 'java')

print("OUTPUT (Java):")
print(java_code)
print("="*80)

# Check if conversion happened
if 'WebElement' in java_code and 'new WebDriverWait' in java_code:
    print("\n✓ CONVERSION SUCCESSFUL!")
else:
    print("\n✗ CONVERSION FAILED - still Python syntax!")
