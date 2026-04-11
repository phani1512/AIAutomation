"""Debug why 'select option' matches wrong pattern"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'main', 'python'))

from core.inference_improved import ImprovedSeleniumGenerator

gen = ImprovedSeleniumGenerator(silent=True)

prompt = "select option"
print(f"Debugging prompt: '{prompt}'")
print()

# Check PageHelper patterns
print("PageHelper patterns with 'select':")
patterns = [(k, v) for k, v in gen.pagehelper_cache.items() if 'select' in k.lower()]
for p, d in sorted(patterns, key=lambda x: len(x[0]), reverse=True)[:10]:
    print(f"  {p} -> {d['method_name']}")
print()

# Generate code
code = gen.generate_clean(prompt, language='java', comprehensive_mode=False)
print("Generated code:")
print(code)
print()

# Check what it should be
print("Expected: Should contain 'Select' (dropdown selection)")
print(f"Actual: {'Select' in code}")
