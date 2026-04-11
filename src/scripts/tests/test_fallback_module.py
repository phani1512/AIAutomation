"""Test fallback_strategy module directly"""
import sys
sys.path.insert(0, r'c:\Users\valaboph\AIAutomation\src\main\python')

from fallback_strategy import FallbackStrategyGenerator

# Create instance
generator = FallbackStrategyGenerator()

# Test Python click generation
selectors = ['.login-row .primary-btn', 'button', "input[type='button']", "[role='button']", '.btn', 'a.button']
code = generator.generate_code_with_fallbacks(
    prompt="click login button",
    fallback_selectors=selectors,
    action_type="click",
    language="python",
    comprehensive_mode=True,
    value_extractor_func=None
)

print("=== Generated Code from Module ===")
print(code)
print("\n=== Checking for scroll code ===")
if "scrollIntoView" in code:
    print("✅ Scroll code is PRESENT")
else:
    print("❌ Scroll code is MISSING")
