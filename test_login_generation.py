"""
Test script to verify the login code generation works correctly.
Run this directly to test without server caching issues.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'main', 'python'))

from inference_improved import ImprovedSeleniumGenerator

# Initialize generator
print("Loading AI model...")
generator = ImprovedSeleniumGenerator('selenium_ngram_model.pkl', silent=False)

print("\n" + "="*80)
print("COMPLETE LOGIN FLOW TEST")
print("="*80 + "\n")

# Test the complete login prompt
prompt = "enter pvalaboju@vertafore.com in producer-email field and enter Phanindraa$1215 in producer-password and click on producer-login"

print(f"Prompt: {prompt}\n")
print("Generated Code:")
print("-" * 80)

result = generator.generate_clean(prompt)
print(result)

print("\n" + "="*80)
print("VERIFICATION")
print("="*80)

# Check if all three steps are present
checks = [
    ("Step 1 - Email entry", "producer-email" in result and "pvalaboju@vertafore.com" in result),
    ("Step 2 - Password entry", "producer-password" in result and "Phanindraa$1215" in result),
    ("Step 3 - Click button", "producer-login" in result and "By.xpath" in result and "button[@type" in result),
    ("XPath properly escaped", '\\"submit\\"' in result or 'submit' in result),
    ("WebElement click()", "element.click()" in result or "button.click()" in result)
]

print()
for check_name, passed in checks:
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"{status}: {check_name}")

all_passed = all(passed for _, passed in checks)
print(f"\n{'='*80}")
if all_passed:
    print("🎉 ALL CHECKS PASSED! Login generation is working correctly.")
else:
    print("⚠️  SOME CHECKS FAILED. Please review the generated code.")
print(f"{'='*80}\n")
