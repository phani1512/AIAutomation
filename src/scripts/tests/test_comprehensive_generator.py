"""Test comprehensive generator directly"""
import sys
sys.path.insert(0, 'src/main/python')

from comprehensive_code_generator import ComprehensiveCodeGenerator

# Initialize generat generator = ComprehensiveCodeGenerator()

# Test generating code for "click login button" in Java
prompt = "click login button"
simple_code = 'driver.findElement(By.cssSelector(".login-row .primary-btn")).click();'

print("="*80)
print(f"Prompt: {prompt}")
print(f"Simple code (input): {simple_code}")
print("\n" + "="*80)

java_code = generator.enhance_to_comprehensive(
    simple_code=simple_code,
    prompt=prompt,
    language='java'
)

print("Generated Java code:")
print(java_code)
print("="*80)

# Check language
if 'new WebDriverWait' in java_code:
    print("\n✓ Java syntax correct!")
else:
    print("\n✗ NOT Java syntax!")
