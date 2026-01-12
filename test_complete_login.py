import sys
sys.path.insert(0, 'src/main/python')

from inference_improved import ImprovedSeleniumGenerator

gen = ImprovedSeleniumGenerator()

# Test the complete login flow
prompt = "enter pvalaboju@vertafore.com in producer-email field and enter Phanindraa$1215 in producer-password and click on producer-login"

print("=" * 80)
print("TESTING COMPLETE LOGIN FLOW")
print("=" * 80)
print(f"\nPrompt:\n{prompt}")
print("\n" + "=" * 80)
print("GENERATED CODE:")
print("=" * 80)

result = gen.generate_clean(prompt)
print(result)

print("\n" + "=" * 80)
print("VERIFICATION:")
print("=" * 80)

# Check if all three steps are present
checks = [
    ("Step 1: Email input", "producer-email" in result and "sendKeys" in result and "pvalaboju@vertafore.com" in result),
    ("Step 2: Password input", "producer-password" in result and "Phanindraa$1215" in result),
    ("Step 3: Login click", "//button[@type" in result and "click()" in result)
]

all_passed = True
for check_name, passed in checks:
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {check_name}")
    if not passed:
        all_passed = False

print("\n" + "=" * 80)
if all_passed:
    print("✅ ALL CHECKS PASSED!")
else:
    print("❌ SOME CHECKS FAILED")
print("=" * 80)
